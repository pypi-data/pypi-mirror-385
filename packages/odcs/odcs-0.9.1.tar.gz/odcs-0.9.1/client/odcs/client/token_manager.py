import base64
import hashlib
import json
import logging
import os
import secrets
import shlex
import sys
import time
import webbrowser
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

import filelock
import jwt
import requests


logger = logging.getLogger(__name__)

LOCAL_SERVER_RESPONSE = b"""\
<html>
<h2>You may now close this window and return to the app that launched it.</h2>
<p>This was opened by <code>%s</code></p>
</html>
"""


class OIDCAuthError(RuntimeError):
    pass


class AuthorizationCodeFlowError(OIDCAuthError):
    pass


class ClientCredentialsFlowError(OIDCAuthError):
    pass


class RefreshTokenError(OIDCAuthError):
    pass


def _get_default_cache_file(*args):
    h = hashlib.sha256()
    for arg in args:
        h.update(str(args).encode("utf-8"))
    digest = h.hexdigest()
    return os.path.expandvars(f"$HOME/.cache/odcs_auth_token_{digest[:8]}.json")


class TokenManager:
    """
    Helper class for managing OIDC access tokens.

    # How to use this

    Create an instance of this class. This requires your client ID and location
    of the SSO server.

    The public API of this class consists of three properties:
        * `access_token` returns a valid access token (suitable for usage in
           Authorization HTTP as `Bearer <token>`)
        * `token` returns a dict with access token, refresh token and any other
           information returned by SSO server.
        * `auth` returns an object that implements requests.auth.AuthBase and
          can be assigned to session.auth

    This class automatically refreshes the access token when it expires.

    Both access and refresh tokens are cached in a local file. The cache is
    protected by a lock preventing two clients from trying to use the same
    refresh token.

    # Authorization flow selection

    If OIDC_CLIENT_ID and OIDC_CLIENT_SECRET environment variables are set,
    they will be used for client credentials flow.

    Otherwise authorization code flow will be used. If running under graphical
    environment, a local server will start and handle the redirect from SSO
    server. Otherwise (or if there is no browser installed), user will be
    prompted to visit the SSO login page on another machine and copy the
    resulting redirect URL.
    """

    def __init__(
        self,
        client_id,
        auth_endpoint,
        token_endpoint,
        cache_file=None,
        client_secret=None,
        scope="openid email",
    ):
        """Initialize TokenManager.

        :param str client_id: Client ID used only for authorization code flow. For
             client credentials flow, the ID is from environment variable `OIDC_CLIENT_ID`.
        :param str auth_endpoint: The URL of OIDC authorization endpoint.
        :param str token_endpoint: The URL of OIDC token endpoint.
        :param str cache_file: File used for caching token. If not set, the default cache
            file will be used.
        :param str client_secret: Client secret used only for authorization code flow.
            This must be provided if PKCE is not supported.
            For client credentials flow, the secret is from environment variable `OIDC_CLIENT_SECRET`.
        :scope str scope: A string of OIDC scopes separeted by space.
        """
        # This client ID is used only for authorization flow. For client
        # credentials flow an ID from environment variable is used instead.
        self.client_id = client_id
        self.auth_endpoint = auth_endpoint
        self.token_endpoint = token_endpoint
        self.cache_file = cache_file or _get_default_cache_file(
            client_id, auth_endpoint, token_endpoint
        )
        self.client_secret = client_secret
        self.scope = scope
        self.lock = filelock.FileLock(self.cache_file + ".lock")

    def __str__(self):
        return self.access_token

    def _read_token_from_cache(self):
        logger.debug("Reading token from %s", self.cache_file)
        try:
            with open(self.cache_file) as f:
                token = json.load(f)
            if not token or "access_token" not in token:
                logger.warning("access_token not found in token file")
            return token
        except ValueError as exc:
            logger.warning("Failed to parse %s: %s", self.cache_file, exc)
        except OSError as exc:
            logger.debug("Failed to read token: %s", exc)

        return None

    def _write_token_to_cache(self, token):
        logger.debug("Writing token to local file")
        try:
            with open(self.cache_file, "w") as file:
                os.chmod(self.cache_file, 0o600)
                json.dump(token, file)
        except Exception as exc:
            logger.error("unable to save token to local file", exc_info=exc)

    def _local_server(self, handler):
        # The port is hardcoded here. Ideally the port should be specified as
        # 0, which would mean the code would pick a random available port.
        # However, that would be rejected by SSO server.
        logger.debug("Creating a webserver to host the callback url")
        for port in (12345, 9000):
            try:
                return HTTPServer(("localhost", port), handler)
            except Exception as exc:
                logger.error("Failed to create local webserver", exc_info=exc)
        raise OIDCAuthError("Failed to create local webserver")

    def _open_in_browser(self, url):
        try:
            logger.debug("Attempting to launch a browser")
            print(
                "Attempting to launch a browser on your laptop. If it doesn't "
                f"work, please go to {url} on your own",
                file=sys.stderr,
            )
            return webbrowser.open(url)
        except webbrowser.Error:
            return False

    def _gen_things(self):
        """Generate code_verifier and code_challenge for PKCE and also state."""
        logger.debug("Generating verifier, challenge, state")
        code_verifier = secrets.token_urlsafe(96)
        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("ascii")).digest()
            )
            .rstrip(b"=")
            .decode()
        )
        state = secrets.token_urlsafe(16)
        logger.debug(f"Code Verifier: {code_verifier}")
        logger.debug(f"Code Challenge: {code_challenge}")
        logger.debug(f"state: {state}")
        return code_verifier, code_challenge, state

    def _code_to_token(self, code, code_verifier, redirect_uri):
        """Get a token using the authorization code.

        :param str code: authorization code.
        :param str code_verifier: code_verifier.
        :param str redirect_uri: redirect_uri.
        """
        logger.debug("Exchaning the code for a token via http calls.")
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        if self.client_secret:
            data.update({"client_secret": self.client_secret})
        else:
            data.update({"code_verifier": code_verifier})
        resp = requests.post(url=self.token_endpoint, data=data, allow_redirects=False)
        if resp.status_code != 200:
            raise AuthorizationCodeFlowError(resp.text)
        return resp.json()

    def _authorization_code_flow(self, with_browser):
        logger.debug("Starting authorization code flow")
        token = None
        try:
            auth_response = None

            class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    nonlocal auth_response
                    auth_response = (
                        f"http://localhost:{self.server.server_port}{self.path}"
                    )
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    cmd = " ".join(map(shlex.quote, sys.argv))
                    self.wfile.write(LOCAL_SERVER_RESPONSE % cmd.encode("utf-8"))

            httpd = self._local_server(SimpleHTTPRequestHandler)

            code_verifier, code_challenge, state = self._gen_things()
            redirect_uri = f"http://localhost:{httpd.server_port}/"
            params = {
                "response_type": "code",
                "client_id": self.client_id,
                "scope": self.scope,
                "redirect_uri": redirect_uri,
                "state": state,
            }
            if self.client_secret:
                params.update({"client_secret": self.client_secret})
            else:
                params.update(
                    {
                        "code_challenge": code_challenge,
                        "code_challenge_method": "S256",
                    }
                )
            url = requests.PreparedRequest()
            url.prepare_url(self.auth_endpoint, params)

            if with_browser and self._open_in_browser(url.url):
                logger.debug("Waiting for the redirect to arrive")
                # This will set auth_response variable
                httpd.handle_request()
            else:
                print(
                    f"Please open a browser on your laptop and go to {url.url}\n"
                    "You will end up on a localhost page that DOES NOT load.\n"
                    "Enter the address from the URL bar of the localhost page that did NOT load: ",
                    file=sys.stderr,
                    end="",
                    flush=True,
                )
                auth_response = input()

            code = parse_qs(urlparse(auth_response).query)["code"][0]
            token = self._code_to_token(code, code_verifier, redirect_uri)

        except Exception as exc:  # TODO be more specific
            logger.error(
                "Unable to auth using authorization code flow",
                exc_info=exc,
            )
            raise AuthorizationCodeFlowError(
                "Unable to auth using authorization code flow"
            )
        return token

    def _client_cred_auth(self):
        logger.debug("Starting client credentials flow")
        try:
            data = {
                "client_id": os.environ["OIDC_CLIENT_ID"],
                "client_secret": os.environ["OIDC_CLIENT_SECRET"],
                "grant_type": "client_credentials",
            }
            resp = requests.post(self.token_endpoint, data=data, allow_redirects=False)
            if resp.status_code != 200:
                raise ClientCredentialsFlowError(resp.text)
            token = resp.json()
        except Exception as exc:
            logger.error("Unable to auth using client credentials", exc_info=exc)
            raise ClientCredentialsFlowError("unable to auth using client credentials")
        return token

    def _refresh_token(self, token):
        """Refresh expired token.

        :param dict token: The token returned by token endpoint.
        """
        logger.debug("Getting a new access token using a refresh token")
        try:
            rf_token_suffix = token["refresh_token"][-4:]
            token_suffix = token["access_token"][-4:]
            data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": token["refresh_token"],
            }
            resp = requests.post(
                url=self.token_endpoint, data=data, allow_redirects=False
            )
            if resp.status_code != 200:
                raise RefreshTokenError(resp.text)
            newtoken = resp.json()
            new_token_suffix = newtoken["access_token"][-4:]
            new_rf_token_suffix = newtoken["refresh_token"][-4:]
            logger.debug(
                "refresh token ending in %r was used to replace expired access "
                "token ending in %r.",
                rf_token_suffix,
                token_suffix,
            )
            logger.debug(
                "New access token ends in %r and new refresh token ends in %r",
                new_token_suffix,
                new_rf_token_suffix,
            )
        except Exception as exc:
            logger.error("Failed to refresh access token", exc_info=exc)
            raise RefreshTokenError("unable to swap refresh token for new access token")
        return newtoken

    def _get_token_exp(self, token, key):
        """Get exp time of token[key].

        :param dict token: OAuth token.
        :param str key: 'access_token' or 'refresh_token'.
        """
        # We are decoding only to get expiration time. There's no need to verify
        # anything else.
        try:
            return jwt.decode(token[key], options={"verify_signature": False})["exp"]
        except jwt.DecodeError as e:
            # Token from https://id.fedoraproject.org/ is not in JWT format
            logger.debug(
                "Unable to decode the token, maybe it's not a JWT token", exc_info=e
            )

        # Try to get the exp
        if "expires_in" in token:
            try:
                return os.stat(self.cache_file).st_mtime + token["expires_in"]
            except Exception as e:
                logger.debug("Unable to get token exp", exc_info=e)

        return 0

    def _get_token(self):
        token = self._read_token_from_cache()
        if token:
            # Cached token looks to be in proper format. If it expires more
            # than 20 seconds from now, we should be able to use it directly.
            # We are not using the token for authn/authz, so don't need to
            # verify it.
            time_to_live = self._get_token_exp(token, "access_token") - time.time()
            logger.debug("Access token expires in %d s", time_to_live)
            if time_to_live > 20:
                logger.info("Cached access token is not expired, use it.")
                return token
            logger.debug("Access token in local file has expired")
            if token.get("refresh_token", False):
                # We have a refresh token. Is it still good?
                time_to_live = self._get_token_exp(token, "refresh_token") - time.time()
                logger.debug("Cached refresh token expires in %d s", time_to_live)
                if time_to_live > 20:
                    token = self._refresh_token(token)
                else:
                    logger.debug("Refresh token in local file has expired")
                    token = None
            else:
                # There is no refresh token, we have to auth again.
                logger.debug("No refresh token is available")
                token = None
        # If refresh token is expired, never existed (client creds), or there
        # was nothing cached, we will need to reauth. Note that we don't
        # support continual auto re-auth of humans using authorization_code.
        # You get a single 10 hours from a refresh token once.
        if not token:
            # No cached token found, create a new one.
            if "OIDC_CLIENT_ID" in os.environ and "OIDC_CLIENT_SECRET" in os.environ:
                # We have client credentials, use them!
                token = self._client_cred_auth()
            else:
                logger.debug(
                    "OIDC client credentials flow is disabled as environment variables"
                    " OIDC_CLIENT_ID and OIDC_CLIENT_SECRET are not set."
                )
                if "NO_OIDC_AUTHZ_CODE" in os.environ:
                    logger.debug(
                        "OIDC authorization code flow is disabled by environment"
                        " variable NO_OIDC_AUTHZ_CODE."
                    )
                    return None
                with_browser = os.environ.keys() & {"DISPLAY", "WAYLAND_DISPLAY"}
                if not with_browser and not os.isatty(sys.stdin.fileno()):
                    logger.debug(
                        "OIDC authorization code flow is disabled as we have no"
                        " TTY nor ability to launch a browser."
                    )
                    return None
                token = self._authorization_code_flow(with_browser=with_browser)

        if token:
            self._write_token_to_cache(token)
        return token

    @property
    def token(self):
        with self.lock:
            return self._get_token()

    @property
    def access_token(self):
        return self.token.get("access_token") if self.token else None

    @property
    def auth(self):
        return BearerAuth(self)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token_manager):
        self.token_manager = token_manager

    def __call__(self, request):
        token = self.token_manager.access_token
        request.headers["Authorization"] = f"Bearer {token}"
        return request

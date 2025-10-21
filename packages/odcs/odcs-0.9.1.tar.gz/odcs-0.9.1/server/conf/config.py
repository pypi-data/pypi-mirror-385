import errno
import json
from os import path, makedirs, environ


# FIXME: workaround for this moment till confdir, dbdir (installdir etc.) are
# declared properly somewhere/somehow
confdir = path.abspath(path.dirname(__file__))
# use parent dir as dbdir else fallback to current dir
dbdir = (
    path.abspath(path.join(confdir, "../..")) if confdir.endswith("conf") else confdir
)


class BaseConfiguration(object):
    # Make this random (used to generate session keys)
    SECRET_KEY = "74d9e9f9cd40e66fc6c4c2e9987dce48df3ce98542529fd0"
    SQLALCHEMY_DATABASE_URI = environ.get(
        "ODCS_DB_URL", "sqlite:///{0}".format(path.join(dbdir, "odcs.db"))
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    HOST = "127.0.0.1"
    PORT = 5005

    DEBUG = False
    # Global network-related values, in seconds
    NET_TIMEOUT = 120
    NET_RETRY_INTERVAL = 30

    # Available backends are: console, file, journal.
    LOG_BACKEND = "journal"

    # Path to log file when LOG_BACKEND is set to "file".
    LOG_FILE = "odcs.log"

    # Available log levels are: debug, info, warn, error.
    LOG_LEVEL = "info"

    SSL_ENABLED = False

    # Users are required to be in allowed_clients to generate composes,
    # you can add group names or usernames (it can be normal user or host
    # principal) into ALLOWED_CLIENTS. The group names are from ldap for
    # kerberos users or FAS for openidc users.
    #
    # You can also specify granular per-user or per-group permissions like
    # this:
    #
    # ALLOWED_CLIENTS = {
    #   'users': {
    #     'joe': {}, # Can use any flags/source_types/... as globally allowed
    #     'mike': {  # Can do only tag/module composes
    #       'source_types': ['tag', 'module'],
    #     },
    #     'ralph': { # Can use only 'no_deps' flags and 'repository' results
    #       'flags': ['no_deps'],
    #       'results': ['repository'],
    #     },
    #     'foo': { # Allow any source
    #       'source': [''],
    #     },
    #   }
    # }
    ALLOWED_CLIENTS = {
        "groups": {},
        "users": {},
    }

    # Users in ADMINS are granted with admin permission.
    ADMINS = {
        "groups": [],
        "users": [],
    }

    # Select which authentication backend to work with. There are 3 choices
    # noauth: no authentication is enabled. Useful for development particularly.
    # kerberos: Kerberos authentication is enabled.
    # openidc: OpenIDC authentication is enabled.
    # oidc_or_kerberos: OpenIDC or Kerberos authentication is enabled.
    AUTH_BACKEND = "noauth"

    # Used for Kerberos authentication and to query user's groups.
    # Format: ldap://hostname[:port]
    # For example: ldap://ldap.example.com/
    AUTH_LDAP_SERVER = ""

    # List of (base, filter) pairs to query groups from LDAP server.
    # ODCS can query groups from multi base with different filter, for example:
    # AUTH_LDAP_GROUPS = [
    #     ("ou=groups,dc=example,dc=com", "memberUid={}"),
    #     ("ou=adhoc,ou=managedGroups,dc=example,dc=com", "uniqueMember=uid={},ou=users,dc=example,dc=com")
    # ]
    AUTH_LDAP_GROUPS = []

    # This is required by openidc and oidc_or_kerberos auth backends.
    AUTH_OPENIDC_USERINFO_URI = "https://id.fedoraproject.org/openidc/UserInfo"

    # This is required by openidc auth backend.
    # Scope requested from Fedora Infra for permission of submitting request to
    # run a new compose.
    # See also: https://fedoraproject.org/wiki/Infrastructure/Authentication
    # Add additional required scope in following list
    #
    # ODCS has additional scopes, which will be checked later when specific
    # API is called.
    # https://pagure.io/odcs/new-compose
    # https://pagure.io/odcs/renew-compose
    # https://pagure.io/odcs/delete-compose
    AUTH_OPENIDC_REQUIRED_SCOPES = [
        "openid",
        "https://id.fedoraproject.org/scope/groups",
    ]

    # This is required by openidc auth backend.
    # OIDC base namespace
    # See also section pagure.io/odcs in
    # https://fedoraproject.org/wiki/Infrastructure/Authentication
    OIDC_BASE_NAMESPACE = "https://pagure.io/odcs/"

    # These three options are required when authenticate to CTS via OIDC.
    # When these options are configured, ODCS will pass them to Pungi and then
    # Pungi will authenticate to CTS via OIDC.
    OIDC_CLIENT_ID = ""
    OIDC_CLIENT_SECRET = ""
    OIDC_TOKEN_URL = ""

    # Select backend where message will be sent to. Currently, umb is supported
    # which means the Unified Message Bus.
    MESSAGING_BACKEND = ""  # fedora-messaging or umb

    # List of broker URLs. Each of them is a string consisting of domain and
    # optiona port.
    MESSAGING_BROKER_URLS = []

    # Path to certificate file used to authenticate ODCS by messaging broker.
    MESSAGING_CERT_FILE = ""

    # Path to private key file used to authenticate ODCS by messaging broker.
    MESSAGING_KEY_FILE = ""

    MESSAGING_CA_CERT = ""

    # The MESSAGING_TOPIC is used as topic for messages sent when compose
    # state is change.
    # The INTERNAL_MESSAGING_TOPIC is used for ODCS internal messages sent
    # from frontends to backends. It for example triggers removal of expired
    # composes.
    # For umb, it is the ActiveMQ virtual topic e.g.
    # VirtualTopic.eng.odcs.state.changed.
    MESSAGING_TOPIC = ""
    INTERNAL_MESSAGING_TOPIC = ""

    # Command line arguments used to construct pungi-koji command.
    PUNGI_KOJI_ARGS = []

    # Command line argument for raw_config source type, which overwrite
    # arguments listed PUNGI_KOJI_ARGS.
    # If a particular raw config should have specific pungi-koji arguments, add
    # a key/value into this option, where key should exist in the
    # RAW_CONFIG_URLS, and value lists each arguments.
    # If no argument is required, just omit it, or add a key/value just as
    # mentioned, but keep value as a empty list.
    # RAW_CONFIG_PUNGI_KOJI_ARGS = {
    #     'my_raw_config': ['arg1', ...],
    #     'another_raw_config': ['arg1', ...],
    # }

    # Expected number of celery backends
    EXPECTED_BACKEND_NUMBER = 1

    CELERY_BROKER_URL = environ.get("ODCS_CELERY_BROKER_URL", "")

    CELERY_CONFIG = {
        "broker_transport_options": {
            "max_retries": 3,
            "interval_start": 0,
            "interval_step": 0.2,
            "interval_max": 0.5,
        },
        # Add this option to stop invoking celery built-in periodic task
        # celery.backend_cleanup which is useless and causes issue in odcs.
        "result_expires": None,
    }

    if "PULP_SERVER_URL" in environ:
        PULP_SERVER_URL = environ.get("PULP_SERVER_URL")
    if "PULP_SSL_KEY" in environ:
        PULP_SSL_KEY = environ.get("PULP_SSL_KEY")
    if "PULP_SSL_CERT" in environ:
        PULP_SSL_CERT = environ.get("PULP_SSL_CERT")
    if "TARGET_DIR_URL" in environ:
        TARGET_DIR_URL = environ.get("TARGET_DIR_URL")
    if "RAW_CONFIG_URLS" in environ:
        RAW_CONFIG_URLS = json.loads(environ.get("RAW_CONFIG_URLS"))
    if "RAW_CONFIG_CREDENTIALS" in environ:
        RAW_CONFIG_CREDENTIALS = json.loads(environ.get("RAW_CONFIG_CREDENTIALS"))


class DevConfiguration(BaseConfiguration):
    DEBUG = True
    LOG_BACKEND = "console"
    LOG_LEVEL = "debug"

    # Global network-related values, in seconds
    NET_TIMEOUT = 5
    NET_RETRY_INTERVAL = 1
    TARGET_DIR = environ.get("ODCS_TARGET_DIR", path.join(dbdir, "test_composes"))
    try:
        makedirs(TARGET_DIR, mode=0o775)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise RuntimeError(
                "Can't create compose target dir %s: %s" % (TARGET_DIR, ex.strerror)
            )

    PUNGI_CONF_PATH = path.join(confdir, "pungi.conf")
    AUTH_BACKEND = "noauth"
    AUTH_OPENIDC_USERINFO_URI = "https://iddev.fedorainfracloud.org/openidc/UserInfo"

    KOJI_PROFILE = "koji"

    RAW_CONFIG_WRAPPER_CONF_PATH = path.join(confdir, "raw_config_wrapper.conf")


class TestConfiguration(BaseConfiguration):
    LOG_BACKEND = "console"
    LOG_LEVEL = "debug"
    DEBUG = True

    # Use in-memory sqlite db to make tests fast.
    SQLALCHEMY_DATABASE_URI = "sqlite://"

    PUNGI_CONF_PATH = path.join(confdir, "pungi.conf")
    RAW_CONFIG_WRAPPER_CONF_PATH = path.join(confdir, "raw_config_wrapper.conf")
    # Global network-related values, in seconds
    NET_TIMEOUT = 0
    NET_RETRY_INTERVAL = 0
    TARGET_DIR = path.join(dbdir, "test_composes")
    try:
        makedirs(TARGET_DIR, mode=0o775)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise RuntimeError(
                "Can't create compose target dir %s: %s" % (TARGET_DIR, ex.strerror)
            )

    AUTH_BACKEND = "noauth"
    AUTH_LDAP_SERVER = "ldap://ldap.example.com"
    AUTH_LDAP_GROUPS = [("ou=groups,dc=example,dc=com", "memberUid={}")]

    MESSAGING_BACKEND = "rhmsg"
    KOJI_PROFILE = "koji"


class ProdConfiguration(BaseConfiguration):
    pass

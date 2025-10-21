import os
import re
import sys

from odcs.server import conf


def print_creds(vars):
    for var, value in vars.items():
        print("%s=%s" % (var, value))


def main():
    try:
        _, cmd = sys.argv
    except ValueError:
        print("Usage: odcs-credential-helper get", file=sys.stderr)
        sys.exit(1)
    if cmd == "get":
        params = dict(line.strip().split("=", 1) for line in sys.stdin)
        if params.get("protocol") != "https":
            print(
                "Not going to send credentials over unencrypted http protocol",
                file=sys.stderr,
            )
            sys.exit(1)
        repo_url = "%(protocol)s://%(host)s/%(path)s" % params
        try:
            source_name = os.environ["ODCS_RAW_CONFIG_SOURCE_NAME"]
        except KeyError:
            print("Missing ODCS_RAW_CONFIG_SOURCE_NAME in environment", file=sys.stderr)
            sys.exit(1)
        credentials = conf.raw_config_credentials.get(source_name, {})
        for host, creds in credentials.items():
            if re.match(host, repo_url):
                print_creds(creds)
                # Stop on first match.
                break

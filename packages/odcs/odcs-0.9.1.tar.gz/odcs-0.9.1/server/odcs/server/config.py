# -*- coding: utf-8 -*-

# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

import os
import sys

from importlib.machinery import SourceFileLoader

from kobo.conf import PyConfigParser

from odcs.server import logger
from odcs.common.types import COMPOSE_RESULTS, COMPOSE_FLAGS


def init_config(app):
    """
    Configure ODCS
    """
    config_dir = os.environ.get("ODCS_CONFIG_DIR", "/etc/odcs")
    config_section = os.environ.get("ODCS_CONFIG_SECTION", "ProdConfiguration")

    # Try to autodecect config dir and section for test and development
    # TestConfiguration shall only be used for running tests, otherwise...
    if any(
        [
            "nosetests" in arg
            or "noserunner.py" in arg
            or "py.test" in arg
            or "pytest" in arg
            for arg in sys.argv
        ]
    ):
        config_section = "TestConfiguration"
        sys.stderr.write("WARN: TestConfiguration will be used.\n")
    # DevConfiguration should be used when ODCS_DEVELOPER_ENV is equivalent to true
    elif os.environ.get("ODCS_DEVELOPER_ENV", "").lower() in (
        "1",
        "on",
        "true",
        "y",
        "yes",
    ):
        config_section = "DevConfiguration"
        sys.stderr.write("WARN: DevConfiguration will be used.\n")

    # Try loading configuration from file
    config_file = os.path.join(config_dir, "config.py")
    try:
        config_module = SourceFileLoader(
            "odcs_runtime_config", config_file
        ).load_module()
    except Exception as e:
        raise SystemError(
            "Error when loading configuration file {} : {}.".format(config_file, str(e))
        )

    # finally configure ODCS
    config_section_obj = getattr(config_module, config_section)
    conf = Config(config_section_obj, config_dir)
    app.config.from_object(config_section_obj)
    return conf


class Config(object):
    """Class representing the odcs configuration."""

    _defaults = {
        "debug": {"type": bool, "default": False, "desc": "Debug mode"},
        "log_backend": {"type": str, "default": None, "desc": "Log backend"},
        "log_file": {"type": str, "default": "", "desc": "Path to log file"},
        "log_level": {"type": str, "default": 0, "desc": "Log level"},
        "net_timeout": {
            "type": int,
            "default": 120,
            "desc": "Global network timeout for read/write operations, in seconds.",
        },
        "net_retry_interval": {
            "type": int,
            "default": 30,
            "desc": "Global network retry interval for read/write operations, in seconds.",
        },
        "arches": {
            "type": list,
            "default": ["x86_64"],
            "desc": "Compose architectures.",
        },
        "pungi_koji": {
            "type": str,
            "default": "pungi-koji",
            "desc": "Name or full-path to pungi-koji binary.",
        },
        "pungi_config_validate": {
            "type": str,
            "default": "",
            "desc": "Name or full-path to pungi-config-validate binary. "
            "If set to empty string, no validation is done.",
        },
        "pungi_timeout": {
            "type": int,
            "default": 3600,
            "desc": "Time in seconds after which the local pungi-koji is "
            "killed and compose is marked as failed",
        },
        "post_script_timeout": {
            "type": int,
            "default": 600,
            "desc": "Time in seconds after which any post compose script is killed.",
        },
        "mergerepo_timeout": {
            "type": int,
            "default": 1800,
            "desc": "Time in seconds after which the mergerepo_c is "
            "killed and compose is marked as failed",
        },
        "pungi_conf_path": {
            "type": str,
            "default": "/etc/odcs/pungi.conf",
            "desc": "Full path to the pungi.conf jinja2 template.",
        },
        "target_dir": {
            "type": str,
            "default": "/tmp",
            "desc": "Path to target dir to which store composes",
        },
        "target_dir_url": {
            "type": str,
            "default": "http://localhost/odcs",
            "desc": "Public facing URL to target_dir.",
        },
        "extra_target_dirs": {
            "type": dict,
            "default": {},
            "desc": "Extra target_dirs to optionally store the compose on "
            "instead of the conf.target_dir. Key is the name "
            "of volume, value if path to target_dir.",
        },
        "seconds_to_live": {
            "type": int,
            "default": 24 * 60 * 60,
            "desc": "Default number of seconds for which the compose is available.",
        },
        "max_seconds_to_live": {
            "type": int,
            "default": 72 * 60 * 60,
            "desc": "Max number of seconds for which the compose is available.",
        },
        "mbs_url": {
            "type": str,
            "default": "http://localhost/module-build-service",
            "desc": "URL to MSB API.",
        },
        "num_concurrent_pungi": {
            "type": int,
            "default": 2,
            "desc": "Number of concurrent Pungi processes.",
        },
        "allowed_source_types": {
            "type": list,
            "default": ["tag", "module", "build"],
            "desc": "Allowed source types.",
        },
        "allowed_flags": {
            "type": list,
            "default": COMPOSE_FLAGS.keys(),
            "desc": "Allowed compose flags.",
        },
        "allowed_arches": {
            "type": list,
            "default": ["x86_64"],
            "desc": "Allowed compose arches.",
        },
        "allowed_results": {
            "type": list,
            "default": COMPOSE_RESULTS,
            "desc": "Allowed compose results.",
        },
        "allowed_sources": {"type": list, "default": [""], "desc": "Allowed sources."},
        "allowed_compose_types": {
            "type": list,
            "default": [""],
            "desc": "Allowed compose types.",
        },
        "auth_ldap_server": {
            "type": str,
            "default": "",
            "desc": "Server URL to query user's groups.",
        },
        "auth_ldap_groups": {
            "type": list,
            "default": [],
            "desc": "List of pairs (search base, filter pattern) to query user's groups from LDAP server.",
        },
        "allowed_clients": {
            "type": dict,
            "default": {"groups": {}, "users": {}},
            "desc": "Groups and users that are allowed to generate composes.",
        },
        "admins": {
            "type": dict,
            "default": {"groups": [], "users": []},
            "desc": "Admin groups and users.",
        },
        "auth_backend": {
            "type": str,
            "default": "",
            "desc": "Select which authentication backend is enabled and work "
            "with frond-end authentication together.",
        },
        "auth_openidc_userinfo_uri": {
            "type": str,
            "default": "",
            "desc": "UserInfo endpoint to get user information from FAS.",
        },
        "auth_openidc_required_scopes": {
            "type": list,
            "default": [],
            "desc": "Required scopes for submitting request to run new compose.",
        },
        "base_module_names": {
            "type": set,
            "default": set(["platform", "bootstrap"]),
            "desc": (
                "Set of module names which defines the product version "
                "(by their stream) of modules depending on them."
            ),
        },
        "messaging_backend": {
            "type": str,
            "default": "",
            "desc": "Messaging backend, kafka or rhmsg",
        },
        "messaging_broker_urls": {
            "type": list,
            "default": [],
            "desc": "List of messaging broker URLs.",
        },
        "messaging_cert_file": {
            "type": str,
            "default": "",
            "desc": "Path to certificate file used to authenticate ODCS by broker.",
        },
        "messaging_key_file": {
            "type": str,
            "default": "",
            "desc": "Path to private key file used to authenticate ODCS by broker.",
        },
        "messaging_ca_cert": {
            "type": str,
            "default": "",
            "desc": "Path to trusted CA certificate bundle.",
        },
        "messaging_topic_prefix": {
            "type": str,
            "default": "",
            "desc": "Prefix for MESSAGING_TOPIC.",
        },
        "messaging_topic": {
            "type": str,
            "default": "",
            "desc": "Messaging topic to which messages are sent.",
        },
        "messaging_kafka_username": {
            "type": str,
            "default": "",
            "desc": "Username for kafka authentication.",
        },
        "messaging_kafka_password": {
            "type": str,
            "default": "",
            "desc": "Password for kafka authentication.",
        },
        "oidc_base_namespace": {
            "type": str,
            "default": "https://pagure.io/odcs/",
            "desc": "Base namespace of OIDC scopes.",
        },
        "oidc_client_id": {
            "type": str,
            "default": "",
            "desc": "OIDC client ID for CTS authentication.",
        },
        "oidc_client_secret": {
            "type": str,
            "default": "",
            "desc": "OIDC client secret for CTS authentication.",
        },
        "oidc_token_url": {
            "type": str,
            "default": "",
            "desc": "URL to the OIDC token endpoint for CTS authentication.",
        },
        "sigkeys": {
            "type": list,
            "default": [],
            "desc": "Default list of sigkeys. Any package in a compose must "
            "be signed by one of those keys. Can be overriden in a "
            "compose request.",
        },
        "pulp_server_url": {"type": str, "default": "", "desc": "Server URL of Pulp."},
        "pulp_ssl_key": {
            "type": str,
            "default": "/path/to/ssl.key",
            "desc": "Private key for pulp authentication",
        },
        "pulp_ssl_cert": {
            "type": str,
            "default": "/path/to/ssl.crt",
            "desc": "Certificate for pulp authentication",
        },
        "koji_config": {"type": str, "default": None, "desc": "Koji config file."},
        "koji_profile": {"type": str, "default": None, "desc": "Koji config profile."},
        "koji_krb_ccache": {
            "type": str,
            "default": None,
            "desc": "Kerberos ccache file to use for Koji auth.",
        },
        "koji_krb_keytab": {
            "type": str,
            "default": None,
            "desc": "Kerberos keytab to use for Koji auth.",
        },
        "koji_krb_principal": {
            "type": str,
            "default": None,
            "desc": "Kerberos principal to use for Koji auth.",
        },
        "koji_tag_cache_cleanup_timeout": {
            "type": int,
            "default": 30,
            "desc": "Number of days after which the cached Koji tag data "
            'stored in the "koji_tag_cache" directory will be '
            "removed.",
        },
        "raw_config_urls": {
            "type": dict,
            "default": {},
            "desc": 'URLs to get the raw Pungi config from for "raw_config" '
            'source_type. Key is the name of the raw_config "source", '
            "value is the URL in which the %s string is replaced with, "
            '"commit_hash" value.',
        },
        "raw_config_credentials": {
            "type": dict,
            "default": {},
            "desc": "Secrets to use for a particular raw config configuration "
            "source_type.",
        },
        "raw_config_wrapper_conf_path": {
            "type": str,
            "default": "/etc/odcs/raw_config_wrapper.conf",
            "desc": "Full path to the raw_config_wrapper.conf configuration "
            "file. This file holds Pungi configuration which should "
            "import real pungi configuration from raw_config.conf "
            "in order to override some variables.",
        },
        "raw_config_schema_override": {
            "type": str,
            "default": "",
            "desc": "Full path to the JSON file defining Pungi config schema "
            'override. This file is passed to "pungi-config-validate" '
            "using the --schema-override option and can influence "
            "the raw_config validation.",
        },
        "pungi_koji_args": {
            "type": list,
            "default": [],
            "desc": "Command line arguments used to construct pungi-koji " "command.",
        },
        "raw_config_pungi_koji_args": {
            "type": dict,
            "default": {},
            "desc": "Command line argument for raw_config source type, which "
            "overwrite arguments listed PUNGI_KOJI_ARGS.",
        },
        "celery_config": {
            "type": dict,
            "default": {},
            "desc": "Configuration dict to pass to Celery.",
        },
        "celery_broker_url": {"type": str, "default": "", "desc": "Celery broker URL"},
        "celery_pulp_composes_queue": {
            "type": str,
            "default": "pulp_composes",
            "desc": "Name of the Celery queue for Pulp composes.",
        },
        "celery_pungi_composes_queue": {
            "type": str,
            "default": "pungi_composes",
            "desc": "Name of the Celery queue for Pungi composes.",
        },
        "celery_cleanup_queue": {
            "type": str,
            "default": "cleanup",
            "desc": "Name of the Celery queue for cleanup task.",
        },
        "celery_router_config": {
            "type": dict,
            "default": {
                "routing_rules": {
                    "odcs.server.celery_tasks.generate_pungi_compose": {
                        "pungi_composes": {"source_type": 3},
                    },
                    "odcs.server.celery_tasks.generate_pulp_compose": {
                        "pulp_composes": {"source_type": 4},
                    },
                },
                "cleanup_task": "odcs.server.celery_tasks.run_cleanup",
                "default_queue": "pungi_composes",
            },
            "desc": "Configuration for custom celery router.",
        },
        "runroot_extra_mounts": {
            "type": list,
            "default": [],
            "desc": "Extra mountpoint directories for odcs-mock-runroot.",
        },
    }

    def __init__(self, conf_section_obj, config_dir):
        """
        Initialize the Config object with defaults and then override them
        with runtime values.
        """
        self.ODCS_CONFIG_DIR = config_dir

        # read items from conf and set
        for key in dir(conf_section_obj):
            # skip keys starting with underscore
            if key.startswith("_"):
                continue
            # set item (lower key)
            self.set_item(key.lower(), getattr(conf_section_obj, key))

        # set item from defaults if the item is not set
        for name, values in self._defaults.items():
            if hasattr(self, name):
                continue
            self.set_item(name, values["default"])

        # Used by Flask-Login to disable the @login_required decorator
        self.login_disabled = self.auth_backend == "noauth"

    def set_item(self, key, value):
        """
        Set value for configuration item. Creates the self._key = value
        attribute and self.key property to set/get/del the attribute.
        """
        if key == "set_item" or key.startswith("_"):
            raise Exception("Configuration item's name is not allowed: %s" % key)

        # Create the empty self._key attribute, so we can assign to it.
        setattr(self, "_" + key, None)

        # Create self.key property to access the self._key attribute.
        # Use the setifok_func if available for the attribute.
        setifok_func = "_setifok_{}".format(key)
        if hasattr(self, setifok_func):
            setx = lambda self, val: getattr(self, setifok_func)(val)
        else:
            setx = lambda self, val: setattr(self, "_" + key, val)
        get_func = "_get_{}".format(key)
        if hasattr(self, get_func):
            getx = lambda self: getattr(self, get_func)()
        else:
            getx = lambda self: getattr(self, "_" + key)
        delx = lambda self: delattr(self, "_" + key)
        setattr(Config, key, property(getx, setx, delx))

        # managed/registered configuration items
        if key in self._defaults:
            # type conversion for configuration item
            convert = self._defaults[key]["type"]
            if convert in [bool, int, list, str, set, dict, float]:
                try:
                    # Do no try to convert None...
                    if value is not None:
                        value = convert(value)
                except Exception:
                    raise TypeError(
                        "Configuration value conversion failed for name: %s" % key
                    )
            # unknown type/unsupported conversion
            elif convert is not None:
                raise TypeError(
                    "Unsupported type %s for configuration item name: %s"
                    % (convert, key)
                )

        # Set the attribute to the correct value
        setattr(self, key, value)

    def _get_raw_config_urls(self):
        raw_config_urls_conf = os.path.join(
            self.ODCS_CONFIG_DIR, "raw_config_urls.conf"
        )

        if not hasattr(self, "_raw_config_urls_mtime"):
            self._raw_config_urls_mtime = 0

        if os.path.isfile(raw_config_urls_conf):
            mtime = os.path.getmtime(raw_config_urls_conf)
            if mtime > self._raw_config_urls_mtime:
                c = PyConfigParser()
                c.load_from_file(raw_config_urls_conf)
                self._setifok_raw_config_urls(c["RAW_CONFIG_URLS"])
                self._setifok_raw_config_credentials(
                    c.get("RAW_CONFIG_CREDENTIALS", {})
                )
                self._raw_config_urls_mtime = mtime

        return self._raw_config_urls

    #
    # Register your _setifok_* handlers here
    #

    def _setifok_allowed_clients(self, clients):
        if not isinstance(clients, dict):
            raise TypeError("allowed_clients must be a dict.")
        for role, role_dict in clients.items():
            if role not in ["users", "groups"]:
                raise ValueError("Unknown role %s in allowed_clients." % role)
            if not isinstance(role_dict, dict):
                raise TypeError("allowed_clients['%s'] is not a dict" % role)
            for user, user_dict in role_dict.items():
                if not isinstance(user_dict, dict):
                    raise TypeError(
                        "allowed_clients['%s']['%s'] is not a dict" % (role, user)
                    )
                for key, value in user_dict.items():
                    if not isinstance(value, (set, list)):
                        raise ValueError(
                            "allowed_clients['%s']['%s']['%s'] is not a "
                            "list" % (role, user, key)
                        )
        self._allowed_clients = clients

    def _setifok_raw_config_urls(self, raw_config_urls):
        if not isinstance(raw_config_urls, dict):
            raise TypeError("raw_config_urls must be a dict.")
        for name, url_data in raw_config_urls.items():
            if not isinstance(url_data, dict):
                raise TypeError("raw_config_urls['%s'] is not a dict." % name)
            for key in ["url", "config_filename"]:
                if key not in url_data:
                    raise ValueError(
                        "raw_config_urls['%s']['%s'] is not defined." % (name, key)
                    )
        self._raw_config_urls = raw_config_urls

    def _setifok_raw_config_credentials(self, raw_config_credentials):
        if not isinstance(raw_config_credentials, dict):
            raise TypeError("raw_config_credentials must be a dict.")
        for name, creds in raw_config_credentials.items():
            if not isinstance(creds, dict):
                raise TypeError("raw_config_credentials['%s'] is not a dict." % name)
        self._raw_config_credentials = raw_config_credentials

    def _setifok_log_backend(self, s):
        if s is None:
            self._log_backend = "console"
        elif s not in logger.supported_log_backends():
            raise ValueError("Unsupported log backend")
        self._log_backend = str(s)

    def _setifok_log_file(self, s):
        if s is None:
            self._log_file = ""
        else:
            self._log_file = str(s)

    def _setifok_log_level(self, s):
        level = str(s).lower()
        self._log_level = logger.str_to_log_level(level)

    def _setifok_target_dir(self, s):
        if not os.path.isabs(s):
            raise ValueError("Compose target dir is not an absolute path: %s" % s)
        self._target_dir = s

    def _setifok_pungi_conf_path(self, s):
        if not os.path.isfile(s):
            raise ValueError("Pungi config template doesn't exist: %s" % s)
        self._pungi_conf_path = s

    def _setifok_celery_router_config(self, celery_router_config):
        if not isinstance(celery_router_config, dict):
            raise TypeError("celery_router_config must be a dict.")

        required_config_keys = ["routing_rules", "cleanup_task", "default_queue"]

        for conf_key in required_config_keys:
            if not celery_router_config.get(conf_key):
                raise KeyError("celery_router_config is missing %s" % conf_key)

        if not isinstance(celery_router_config["routing_rules"], dict):
            raise TypeError("routing_rules must be a dict.")

        self._celery_router_config = celery_router_config

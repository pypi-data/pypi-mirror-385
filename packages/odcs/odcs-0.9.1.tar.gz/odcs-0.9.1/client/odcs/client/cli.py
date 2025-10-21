import argparse
import json
import logging
import os
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import requests.exceptions

import odcs.client.odcs

from .token_manager import TokenManager

logger = logging.getLogger(__name__)

KNOWN_ARGS = {
    "--flag": dict(
        default=[], action="append", help="Flag to pass to influence the compose."
    ),
    "--target-dir": dict(default="", help="Name of the server-side target directory."),
    "--result": dict(
        default=[],
        action="append",
        help="Results of a compose to influence the compose.",
    ),
    "--sigkey": dict(
        default=[],
        action="append",
        help="ODCS will require that all packages are signed by this "
        'signing key ID. Example: "FD431D51". You may use this option '
        "multiple times to specify multiple key IDs. ODCS will choose "
        "signed packages according to the order of the key IDs that "
        'you specify here. Use "--sigkey none" to allow unsigned '
        "packages. If you do not specify any --sigkey option, ODCS "
        "will use the default signing key list (defined on the server).",
    ),
    "--koji-event": dict(
        default=None, help="Koji event for populating package set", type=int
    ),
    "--arch": dict(
        default=[], action="append", help="Koji arch to build the compose for."
    ),
    "--module-defaults-url": dict(
        default="",
        metavar="module_defaults_url",
        help="URL to git repository with module defaults.",
    ),
    "--module-defaults-commit": dict(
        default="",
        metavar="module_defaults_commit",
        help="Git commit/branch from which to take the module defaults.",
    ),
    "--modular-tag": dict(
        default=[],
        action="append",
        metavar="modular_koji_tags",
        help="Koji tag with module builds.",
    ),
    "--lookaside-repo": dict(
        default=[],
        action="append",
        metavar="lookaside_repos",
        help="Specify lookaside repositories.",
    ),
    "--scratch-module": dict(
        default=[],
        action="append",
        metavar="scratch_modules",
        help="Scratch modules to be included in the compose with format N:S:V:C",
    ),
    "--label": dict(default=None, help="Label for raw_config compose."),
    "--no-label": dict(
        default=False,
        action="store_true",
        help="Allow raw_config compose without label.",
    ),
    "--compose-type": dict(default=None, help="Compose type for raw_config compose."),
    "--build": dict(
        default=[], action="append", help="Builds to be included in the compose."
    ),
}


def _add_arguments(parser, *args):
    for arg in args:
        try:
            parser.add_argument(arg, **KNOWN_ARGS[arg])
        except KeyError:
            raise ValueError("Unknown argument %s." % arg)
    return parser


DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "odcs.toml"
)


def _load_cfg(infra=None, env=None):
    """Load client config file.

    :param str infra:
    """

    cfg_file = os.path.join(os.path.expanduser("~"), ".config", "odcs.toml")
    if not os.path.isfile(cfg_file):
        cfg_file = DEFAULT_CONFIG_FILE
    with open(cfg_file, "rb") as f:
        conf = tomllib.load(f)

    if infra and env:
        return conf[infra][env]
    elif infra:
        return conf[infra]
    else:
        return conf


def main():
    parser = argparse.ArgumentParser(
        description="""\
    %(prog)s - Command line client.

    CONFIGURATION:
        The default configuration file is `{}`,
        and you can copy it to `~/.config/odcs.toml` to add your own configurations.

    AUTHENTICATION:

        Internal ODCS instances support both OIDC and kerberos authentication.
        If `OIDC_CLIENT_ID` and `OIDC_CLIENT_SECRET` environment variables are set,
        the client will try to authenticate using OIDC client credential flow otherwise
        it will try OIDC authorizaiton code flow (which can be disabled by setting
        environment variable NO_OIDC_AUTHZ_CODE=1) and finally it will try kerberos
        authentication if OIDC authentication doesn't work.

        If you have problems authenticating with OpenID Connect, try:

            $ rm -f ~/.cache/odcs_auth_token_*

    Example usage:
    """.format(
            DEFAULT_CONFIG_FILE
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--redhat",
        action="store_const",
        const="redhat",
        default="redhat",
        dest="infra",
        help="Deprecated, this option no longer does anything",
    )
    parser.add_argument(
        "--staging",
        action="store_const",
        const="stage",
        default="prod",
        dest="env",
        help="Use staging environment. If omitted, production environment will "
        "be used. This is an alias of `--env stage`.",
    )
    parser.add_argument(
        "-e", "--env", default="prod", help="The environment to be used."
    )
    parser.add_argument("--server", default=None, help="Use custom ODCS server.")
    parser.add_argument(
        "--token", default=None, help="OpenIDC token to use or path to token file"
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="When used, odcs client will not wait for the action to finish.",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Run without detailed log messages"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print debugging information"
    )
    parser.add_argument("--watch", action="store_true", help="Watch compose logs")

    subparsers = parser.add_subparsers(
        description="These commands you can use to operate composes with ODCS"
    )

    create_command_deprecated = """
    Deprecated: Please use create-* commands instead of the deprecated create command.
    The create command will be removed and bugs with it are not going to be fixed.
    """
    create_parser = subparsers.add_parser(
        "create",
        help="Low-level command to create a new compose (Deprecated)",
        description=create_command_deprecated,
    )
    create_parser.set_defaults(command="create")
    create_parser.add_argument(
        "source_type",
        default=None,
        choices=["tag", "module", "raw_config", "pulp", "build"],
        help="Type for the source, for example: tag.",
    )
    create_parser.add_argument(
        "source",
        default="",
        help="Source for the compose. May be a koji tag or a "
        "whitespace separated list of modules.",
    )
    create_parser.add_argument(
        "packages",
        metavar="package",
        nargs="*",
        help="Packages to be included in the compose.",
    )
    create_parser.add_argument(
        "builds",
        metavar="build",
        nargs="*",
        help="Builds to be included in the compose.",
    )
    _add_arguments(
        create_parser,
        "--result",
        "--sigkey",
        "--koji-event",
        "--arch",
        "--module-defaults-url",
        "--module-defaults-commit",
        "--modular-tag",
        "--lookaside-repo",
        "--label",
        "--compose-type",
        "--target-dir",
        "--flag",
        "--scratch-module",
    )

    create_tag_parser = subparsers.add_parser(
        "create-tag", help="Create new compose from Koji tag."
    )
    create_tag_parser.set_defaults(command="create-tag")
    create_tag_parser.add_argument("tag", default="", help="Koji tag name.")
    create_tag_parser.add_argument(
        "packages",
        metavar="package",
        nargs="*",
        help=(
            "Koji packages to be included in the compose. If you specify no packages, "
            "ODCS will simply include all packages in the tag."
        ),
    )
    _add_arguments(
        create_tag_parser,
        "--sigkey",
        "--koji-event",
        "--arch",
        "--module-defaults-url",
        "--module-defaults-commit",
        "--modular-tag",
        "--lookaside-repo",
        "--target-dir",
        "--build",
        "--flag",
        "--scratch-module",
    )

    create_module_parser = subparsers.add_parser(
        "create-module", help="Create new compose from modules."
    )
    create_module_parser.set_defaults(command="create-module")
    create_module_parser.add_argument(
        "modules",
        metavar="modules",
        nargs="*",
        help="List of modules in N:S, N:S:V or N:S:V:C format.",
    )
    create_module_parser.add_argument(
        "--base-module-br-name",
        help="The name of a base module the module buildrequires",
    )
    create_module_parser.add_argument(
        "--base-module-br-stream",
        help="The stream of a base module the module buildrequires",
    )
    create_module_parser.add_argument(
        "--base-module-br-stream-version-lte",
        type=int,
        help=(
            "The numeric value of the stream version (el8.3.1 is 80301, f33 is 33) of "
            "the buildrequired module specified by --base-module-br-name must be less "
            "than equal to the given value."
        ),
    )
    create_module_parser.add_argument(
        "--base-module-br-stream-version-gte",
        type=int,
        help=(
            "The numeric value of the stream version (el8.3.1 is 80301, f33 is 33) of "
            "the buildrequired module specified by --base-module-br-name must be greater "
            "than equal to the given value."
        ),
    )
    _add_arguments(
        create_module_parser,
        "--sigkey",
        "--arch",
        "--modular-tag",
        "--module-defaults-url",
        "--module-defaults-commit",
        "--lookaside-repo",
        "--target-dir",
        "--flag",
        "--scratch-module",
    )

    create_pulp_parser = subparsers.add_parser(
        "create-pulp", help="Create new compose from Pulp content_sets."
    )
    create_pulp_parser.set_defaults(command="create-pulp")
    create_pulp_parser.add_argument(
        "content_sets",
        metavar="content_set",
        nargs="+",
        help="Content sets to be included in the compose.",
    )
    _add_arguments(create_pulp_parser, "--target-dir", "--flag")

    create_raw_config_parser = subparsers.add_parser(
        "create-raw-config", help="Create new compose from Pungi raw configuration."
    )
    create_raw_config_parser.set_defaults(command="create-raw-config")
    create_raw_config_parser.add_argument(
        "raw_config_name", help="Name of raw_config compose as defined in ODCS Server."
    )
    create_raw_config_parser.add_argument(
        "raw_config_commit", help="Commit or branch name to get raw_config from."
    )
    _add_arguments(
        create_raw_config_parser,
        "--sigkey",
        "--label",
        "--no-label",
        "--compose-type",
        "--koji-event",
        "--target-dir",
        "--build",
    )

    create_build_parser = subparsers.add_parser(
        "create-build", help="Create new compose from Koji builds."
    )
    create_build_parser.set_defaults(command="create-build")
    create_build_parser.add_argument(
        "builds", metavar="NVR", nargs="+", help="Koji builds NVRs."
    )
    _add_arguments(create_build_parser, "--sigkey", "--flag", "--target-dir", "--arch")

    wait_parser = subparsers.add_parser("wait", help="wait for a compose to finish")
    wait_parser.set_defaults(command="wait")
    wait_parser.add_argument("compose_id", default=None, help="ODCS compose id")
    wait_parser.add_argument("--watch", action="store_true", help="Watch compose logs")

    delete_parser = subparsers.add_parser(
        "delete",
        help="delete compose",
        description=(
            "Cancel compose in wait state or mark finished compose as expired "
            "for ODCS backends to remove compose data later from ODCS storage. "
            "Note that compose metadata stored in database won't be removed and always "
            "accessable via 'odcs get' command."
        ),
    )
    delete_parser.set_defaults(command="delete")
    delete_parser.add_argument("compose_id", default=None, help="ODCS compose id")

    renew_parser = subparsers.add_parser(
        "renew",
        help="renew compose",
        description=(
            "Extends the compose expiration time or regenerates expired/failed compose "
            "or regenerates compose with a new label. "
            "The regenerated compose will have the same package versions as the original compose."
        ),
    )
    renew_parser.set_defaults(command="renew")
    renew_parser.add_argument("compose_id", default=None, help="ODCS compose id")
    renew_parser.add_argument(
        "--label", default=None, help="New label of regenerated compose"
    )
    renew_parser.add_argument(
        "--seconds-to-live",
        default=None,
        help="Number of seconds to extends the compose expiration time",
    )

    get_parser = subparsers.add_parser("get", help="get compose info")
    get_parser.set_defaults(command="get")
    get_parser.add_argument("compose_id", default=None, help="ODCS compose id")

    about_parser = subparsers.add_parser(
        "about", help="Get information about ODCS server"
    )
    about_parser.set_defaults(command="about")

    args = parser.parse_args()

    if not hasattr(args, "command"):
        parser.print_help()
        sys.exit(0)

    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    cfg = _load_cfg(args.infra, args.env)
    if args.server is None:
        odcs_url = cfg["url"]
    else:
        odcs_url = args.server

    id_provider = cfg["id_provider"]

    if "localhost" in odcs_url:
        client = odcs.client.odcs.ODCS(
            odcs_url,
            auth_mech=odcs.client.odcs.AuthMech.Anonymous,
        )
    else:
        token_manager = TokenManager(
            cfg.get("oidc_authz_code_client_id"),
            os.path.join(id_provider, "auth"),
            os.path.join(id_provider, "token"),
        )
        try:
            # Check whether OIDC auth working, if not, fall back to krb auth.
            token = token_manager.access_token
        except Exception as e:
            logger.debug("Unable to get OIDC access token", exc_info=e)
            token = None

        if token:
            client = odcs.client.odcs.ODCS(
                odcs_url,
                auth_mech=odcs.client.odcs.AuthMech.OpenIDC,
                openidc_token=token_manager,
            )
        else:
            logger.debug("Using kerberos authentication")
            client = odcs.client.odcs.ODCS(
                odcs_url,
                auth_mech=odcs.client.odcs.AuthMech.Kerberos,
            )

    request_args = {}
    if getattr(args, "flag", False):
        request_args["flags"] = args.flag
    if getattr(args, "arch", False):
        request_args["arches"] = args.arch
    if getattr(args, "lookaside_repo", False):
        request_args["lookaside_repos"] = args.lookaside_repo
    if getattr(args, "label", False):
        request_args["label"] = args.label
    if getattr(args, "no_label", False):
        if "flags" in request_args:
            request_args["flags"].append("no_label")
        else:
            request_args["flags"] = ["no_label"]
    if getattr(args, "compose_type", False):
        request_args["compose_type"] = args.compose_type
    if getattr(args, "target_dir", False):
        request_args["target_dir"] = args.target_dir

    otel_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if otel_endpoint:
        from opentelemetry import context, trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )
        from opentelemetry.trace.propagation.tracecontext import (
            TraceContextTextMapPropagator,
        )

        provider = TracerProvider(
            resource=Resource(attributes={"service.name": "odcs-client"})
        )
        if "console" == otel_endpoint:
            # This is for debugging the tracing locally.
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        else:
            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer(__name__)
        carrier = {}
        traceparent = os.environ.get("TRACEPARENT")
        ctx = None
        if traceparent:
            ctx = TraceContextTextMapPropagator().extract(
                carrier={"traceparent": traceparent}
            )
        with tracer.start_as_current_span("odcs-client", context=ctx) as span:
            TraceContextTextMapPropagator().inject(carrier)
            span.set_attribute("command", " ".join(sys.argv))

        ctx = TraceContextTextMapPropagator().extract(carrier)
        context.attach(ctx)
        RequestsInstrumentor().instrument(tracer_provider=provider)

    try:
        args.sigkey = [key.replace("none", "") for key in getattr(args, "sigkey", [])]
        if args.command == "create":
            print(create_command_deprecated, file=sys.stderr)
            result = client.new_compose(
                source=args.source,
                source_type=args.source_type,
                packages=args.packages,
                results=args.result,
                sigkeys=args.sigkey,
                koji_event=args.koji_event,
                builds=args.builds,
                modular_koji_tags=args.modular_tag,
                module_defaults_url=args.module_defaults_url,
                module_defaults_commit=args.module_defaults_commit,
                scratch_modules=args.scratch_module,
                **request_args,
            )
        elif args.command == "create-tag":
            source = odcs.client.odcs.ComposeSourceTag(
                args.tag,
                args.packages,
                args.build,
                args.sigkey,
                args.koji_event,
                args.modular_tag,
                args.module_defaults_url,
                args.module_defaults_commit,
                args.scratch_module,
            )
            result = client.request_compose(source, **request_args)
        elif args.command == "create-module":
            if not args.modules and not args.scratch_module:
                create_module_parser.error("Please give a module or --scratch-module")
            if (
                len(args.modules) + len(args.scratch_module) > 1
                and not (
                    args.base_module_br_stream
                    or args.base_module_br_stream_version_lte
                    or args.base_module_br_stream_version_gte
                    or args.modular_tag
                )
                and args.infra == "redhat"
            ):
                print(
                    "WARNING: Please add --base-module-X or --modular-tag option to the arguments to ensure all composed modules are built for the same release."
                )
            source = odcs.client.odcs.ComposeSourceModule(
                args.modules,
                args.sigkey,
                args.module_defaults_url,
                args.module_defaults_commit,
                args.scratch_module,
                base_module_br_name=args.base_module_br_name,
                base_module_br_stream=args.base_module_br_stream,
                base_module_br_stream_version_lte=args.base_module_br_stream_version_lte,
                base_module_br_stream_version_gte=args.base_module_br_stream_version_gte,
                modular_koji_tags=args.modular_tag,
            )
            result = client.request_compose(source, **request_args)
        elif args.command == "create-pulp":
            source = odcs.client.odcs.ComposeSourcePulp(args.content_sets)
            result = client.request_compose(source, **request_args)
        elif args.command == "create-raw-config":
            source = odcs.client.odcs.ComposeSourceRawConfig(
                args.raw_config_name,
                args.raw_config_commit,
                args.koji_event,
                sigkeys=args.sigkey,
                builds=args.build,
            )
            result = client.request_compose(source, **request_args)
        elif args.command == "create-build":
            source = odcs.client.odcs.ComposeSourceBuild(args.builds, args.sigkey)
            result = client.request_compose(source, **request_args)
        elif args.command == "wait":
            result = client.get_compose(args.compose_id)
        elif args.command == "delete":
            args.no_wait = True
            result = client.delete_compose(args.compose_id)
        elif args.command == "renew":
            result = client.renew_compose(
                args.compose_id, label=args.label, seconds_to_live=args.seconds_to_live
            )
        elif args.command == "get":
            result = client.get_compose(args.compose_id)
        elif args.command == "about":
            result = client.about()
        else:
            print("Unknown command %s" % args.command)
    except requests.exceptions.HTTPError:
        # error message gets printed in ODCS class.
        sys.exit(-1)

    if args.no_wait or args.command == "about":
        print(json.dumps(result, indent=4, sort_keys=True))
    else:
        if result["state_name"] in ["wait", "generating"]:
            if not args.quiet:
                print(
                    "Waiting for command %s on compose %d to finish."
                    % (args.command, result["id"])
                )
            try:
                result = client.wait_for_compose(
                    result["id"], 3600, watch_logs=args.watch
                )
            except (KeyboardInterrupt, SystemExit):
                pass

        print(json.dumps(result, indent=4, sort_keys=True))
        if result["state_name"] == "failed":
            sys.exit(1)

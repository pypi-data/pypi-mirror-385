from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields


spec = APISpec(
    title="On Demand Compose Service (ODCS)",
    version="v1",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)


class ComposeSchema(Schema):
    arches = fields.String(
        metadata={"description": "White-space separated list of arches to build for."}
    )
    base_module_br_name = fields.String(
        metadata={
            "description": """When requesting a module compose with just N:S[:V], it’s possible to specify base
                module name to limit which composes can be returned. This will usually be platform."""
        }
    )
    base_module_br_stream = fields.String(
        metadata={
            "description": "When base_module_br_name is specified, the stream for the base module should be specified as well."
        }
    )
    base_module_br_stream_version_gte = fields.Integer(
        metadata={
            "description": "When base_module_br_name is specified, this is the lower bound for stream version."
        }
    )
    base_module_br_stream_version_lte = fields.Integer(
        metadata={
            "description": "When base_module_br_name is specified, this is the upper bound for stream version."
        }
    )
    builds = fields.String(
        metadata={
            "description": "White-space separated list of builds (NVR) to include in the compose or null"
        }
    )
    compose_type = fields.String(
        metadata={
            "description": "Type of the compose when generating raw_config compose. Can be `test`, `nightly`, `ci`, `production`."
        }
    )
    flags = fields.List(
        fields.String(),
        metadata={
            "description": """Flags influencing the way how compose is generated.
- `no_deps` - Compose will contain only the requested packages/modules without pulling-in their RPM-level or Module-level dependencies.
- `no_inheritance` - Only packages/modules directly tagged in the requested Koji tag will be added to the module.
    Inherited tags will be ignored.
- `include_unpublished_pulp_repos` - Even unpublished Pulp repositories will be included in the resulting compose.
- `ignore_absent_pulp_repos` - Ignore non-existing content sets in the source of Pulp compose.
    The source field on the compose will be updated to match what was actually used in the compose.
- `check_deps` - Compose will fail if the RPM-level dependencies between packages in the compose are not satisfied.
- `include_done_modules` - Compose can include also modules which are in the done state.
    By default, only modules in ready state are allowed to be included in a composes.
- `no_reuse` - Compose will be generated directly instead of trying to reuse old one.
- `use_only_compatible_arch` - When this flag is set, architecture hardcoded in URL returned from Pulp will
    be replaced with $basearch variable. The repository definition will also define skip_if_unavailable = 1.
    This could be useful when multiple content sets are included in the repofile to completly ignore packages
    from repositories for incompatible archictures."""
        },
    )
    id = fields.Integer(metadata={"description": "The ID of ODCS compose."})
    koji_event = fields.Integer(
        metadata={
            "description": """The Koji event defining the point in Koji history when the compose was generated.
                It can be null if source type does not relate to Koji tag."""
        }
    )
    koji_task_id = fields.Integer()
    label = fields.String(
        metadata={"description": "Compose label when generating raw_config compose."}
    )
    lookaside_repos = fields.String(
        metadata={
            "description": "white-space separated lookaside repository URLs or null."
        }
    )
    modular_koji_tags = fields.String(
        metadata={
            "description": "white-space separated list of koji tags with modules which should appear in the resulting compose or null."
        }
    )
    module_defaults_url = fields.String(
        metadata={"description": "URL on which the module defaults can be found."}
    )
    modules = fields.String(
        metadata={
            "description": """White-space separated list of strings. List of non-scratch module builds
                defined as N:S:V:C format which will be included in the compose."""
        }
    )
    multilib_arches = fields.String(
        metadata={
            "description": """White-space separated list of architectures for which the multilib should be enabled.
                This must be subset of arches. When architecture is listed in the multilib_arches, even the packages from
                binary compatible archictures will end up in a resulting compose for this architecture. For example, if
                x86_64 is in multilib_arches, then even the i686 packages will appear in the resulting compose for x86_64 architecture."""
        }
    )
    multilib_method = fields.Integer(
        metadata={
            "description": """Number defining the way how are the multilib packages identified:
- `0 (none)` - Multilib is disabled.
- `1 (runtime)` - Packages whose name ends with “-devel” or “-static” suffix will be considered as multilib.
- `2 (devel)` - Packages that install some shared object file “.so.” will be considered as multilib.
- `4 (all)` - All packages will be considered as multilib packages."""
        }
    )
    owner = fields.String(
        metadata={"description": "The name of owner (requester) of the compose."}
    )
    packages = fields.String(
        metadata={
            "description": """White-space separated list of names of RPMs (packages) which should appear in the compose.
                The list of packages to choose from is defined by the content of Koji builds defined in builds.
                If null, all packages from builds will be included in a compose."""
        }
    )
    parent_pungi_compose_ids = fields.String(
        metadata={"description": "Pungi compose IDs of parent composes."}
    )
    pungi_compose_id = fields.String(
        metadata={
            "description": "Compose id as generated by Pungi for its ComposeInfo metadata."
        }
    )
    removed_by = fields.String(
        metadata={
            "description": "The name of user who removed (or cancelled) the compose manually."
        }
    )
    respin_of = fields.String(
        metadata={"description": "Pungi compose IDs of compose this compose respins."}
    )
    result_repo = fields.String(
        metadata={
            "description": """The URL to top directory where per-architecture repositories are stored.
                Only set for composes which generate such repositories on ODCS server."""
        }
    )
    result_repofile = fields.String(
        metadata={
            "description": """The URL to .repo file which points to resulting compose.
                Only set for composes which generate such single repository."""
        }
    )
    results = fields.List(fields.String())
    scratch_build_tasks = fields.String(
        metadata={
            "description": "White-space separated list of RPM scratch builds to include in a compose."
        }
    )
    scratch_modules = fields.String(
        metadata={
            "description": "White-space separated list of scratch modules (N:S:V:C) to include in a compose."
        }
    )
    sigkeys = fields.String(
        metadata={
            "description": "White-space separated list sigkeys to define the key using which the package in compose must be signed."
        }
    )
    source = fields.String(
        metadata={
            "description": "Based on the source_type, defines the sources of RPMs for resulting compose. See source_type for more info."
        }
    )
    source_type = fields.Integer(
        metadata={
            "description": """Number defining the type of source giving it particular meaning:
- `1 (tag)` - The source is name of Koji tag to take the builds from.
    Additional Koji builds can be added by when the builds option is set.
- `2 (module)` - The source is the list of modules in N:S, N:S:V or N:S:V:C format. When using N:S format,
    ODCS queries MBS to find the latest build of the module for that stream. ODCS will query MBS for the
    latest module in the ready state unless the user sets the include_done_modules flag. When using N:S:V:C,
    the module can be even in the done state in the MBS.
- `3 (repo)` - The source is full path to repository from which the packages are taken.
    This is often disabled source type by deployed ODCS servers.
- `4 (pulp)` - The source is the list of Pulp content-sets. Repositories defined by these content-sets will be included in the compose.
- `5 (raw_config)` - The source is string in the name#commit hash format. The name must match one of the
    raw config locations defined in ODCS server config as raw_config_urls. The commit is commit hash defining
    the version of raw config to use. This config is then used as input config for Pungi.
- `6 (build)` - The source is set to empty string. The list of Koji builds included in a compose is defined by the builds attribute.
- `7 (pungi_compose)` - The source is URL to variant repository of external compose generated by the Pungi.
    For example https://kojipkgs.fedoraproject.org/compose/rawhide/latest-Fedora-Rawhide/compose/Server/.
    The generated compose will contain the same set of RPMs as the given external compose variant.
    The packages will be taken from the configured Koji instance."""
        }
    )
    state = fields.Integer(
        metadata={
            "description": """Number defining the state the compose is currently in:
- `0 (wait)` - Compose is waiting in a queue to be generated.
- `1 (generating)` - Compose is being generated by one of the backends.
- `2 (done)` - Compose is generated.
- `3 (removed)` - Compose has been removed.
- `4 (failed)` - Compose generation has failed."""
        }
    )
    state_name = fields.String(
        metadata={
            "description": "Name of the state the compose is currently in. See state for more info."
        }
    )
    state_reason = fields.String(metadata={"description": "Reason of state change."})
    target_dir = fields.String(
        metadata={
            "description": """Name of the target directory for the compose. No value or the default value means
                that default target directory is used. This default target directory is always served using the
                ODCS Frontend. Other possible values depend on the ODCS server configuration."""
        }
    )
    time_done = fields.DateTime(
        metadata={
            "description": "The date and time on which the compose has been done - either moved to failed or done state."
        }
    )
    time_removed = fields.DateTime(
        metadata={
            "description": "The date and time on which the compose has been removed from ODCS storage (either cancelled or expired)."
        }
    )
    time_started = fields.DateTime(
        metadata={
            "description": "The date and time on which the compose was started by a backend."
        }
    )
    time_submitted = fields.DateTime(
        metadata={
            "description": "The date and time on which the compose request has been submitted by owner."
        }
    )
    time_to_expire = fields.DateTime(
        metadata={
            "description": """The date and time on which the compose is planned to expire.
                After this time, the compose is removed from ODCS storage."""
        }
    )
    toplevel_url = fields.String(metadata={"description": "URL of the compose."})


class MetaSchema(Schema):
    """Schema for paginated response."""

    first = fields.URL()
    last = fields.URL()
    next = fields.URL()
    pre = fields.URL()
    page = fields.Integer()
    pages = fields.Integer()
    per_page = fields.Integer()
    total = fields.Integer()


class ComposeListSchema(Schema):
    items = fields.List(fields.Nested(ComposeSchema))
    meta = fields.Nested(MetaSchema)


class ComposeDeleteSchema(Schema):
    status = fields.Integer()
    message = fields.String()


class HTTPErrorSchema(Schema):
    """Schema for 401, 403, 404 error response."""

    error = fields.String()
    message = fields.String()
    status = fields.Integer()

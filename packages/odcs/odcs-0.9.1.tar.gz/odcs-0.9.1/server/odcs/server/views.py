# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
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

import datetime
import os

from flask.views import MethodView, View
from flask import render_template, request, jsonify, g, Response, send_from_directory
from prometheus_client import CONTENT_TYPE_LATEST

from odcs.server import app, db, log, conf, version
from odcs.server.errors import NotFound, Forbidden
from odcs.server.models import Compose, Metrics
from odcs.common.types import (
    COMPOSE_RESULTS,
    COMPOSE_FLAGS,
    COMPOSE_STATES,
    PUNGI_SOURCE_TYPE_NAMES,
    PungiSourceType,
    MULTILIB_METHODS,
)
from odcs.server.api_utils import (
    pagination_metadata,
    filter_composes,
    validate_json_data,
    raise_if_input_not_allowed,
    cors_header,
)
from odcs.server.auth import requires_role, login_required, has_role
from odcs.server.auth import require_scopes

if conf.celery_broker_url:
    try:
        from odcs.server.celery_tasks import celery_app, schedule_compose

        CELERY_AVAILABLE = True
    except ImportError as e:
        log.exception(
            "Cannot import celery_tasks. The Celery support is turned off. %s " % e
        )
        CELERY_AVAILABLE = False
else:
    log.warning(
        "conf.celery_broker_url is not configured. The Celery support is turned off."
    )
    CELERY_AVAILABLE = False

try:
    from . import openapi
except ImportError:
    log.warning("Can't generate OpenAPI specification due to missing openapi library")
    openapi = None


app.openapispec = openapi.spec if openapi else None


def _get_traceparent():
    """Get traceparent for using in backend tracing."""
    if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        from opentelemetry.trace.propagation.tracecontext import (
            TraceContextTextMapPropagator,
        )

        carrier = {}
        TraceContextTextMapPropagator().inject(carrier=carrier)
        return carrier["traceparent"]
    else:
        return None


def _get_compose_owner():
    if conf.auth_backend == "noauth":
        log.warning(
            "Cannot determine the owner of compose, because "
            "'noauth' auth_backend is used."
        )
        return "unknown"
    else:
        return g.user.username


def _get_seconds_to_live(request_data, raw_config_key=None):
    default_stl = conf.raw_config_urls.get(raw_config_key, {}).get(
        "seconds_to_live", conf.seconds_to_live
    )
    max_stl = conf.raw_config_urls.get(raw_config_key, {}).get(
        "max_seconds_to_live", conf.max_seconds_to_live
    )

    seconds_to_live = request_data.get("seconds_to_live")
    # Fallback to old name of this variable to keep backward compatibility.
    if seconds_to_live is None:
        seconds_to_live = request_data.get("seconds-to-live")

    if seconds_to_live:
        try:
            return min(int(seconds_to_live), max_stl)
        except ValueError:
            err = "Invalid seconds_to_live specified in request: %s" % request_data
            log.error(err)
            raise ValueError(err)
    else:
        return default_stl


def _run_schedule_compose(compose):
    """Call schedule_compose with error handling.

    :param Compose compose: instance of odcs.server.models.Compose
    """
    try:
        schedule_compose(compose)
    except Exception as e:
        reason = (
            "Can not schedule compose %d probably due to celery broker issue - %s"
            % (compose.id, str(e))
        )
        compose.transition(COMPOSE_STATES["failed"], reason)
        raise RuntimeError(reason)


class ComposesListAPI(MethodView):
    @cors_header()
    def get(self):
        """Return metadata of composes.

        ---
        summary: List composes
        description: List composes
        parameters:
          - name: owner
            description: Return only composes owned by this person
            in: query
            schema:
              type: string
            required: false
          - name: source_type
            description: Return only composes of this source_type
            in: query
            schema:
              type: number
            required: false
          - name: source
            description: Return only composes built from this source
            in: query
            schema:
              type: string
            required: false
          - name: state
            description: Return only composes in this state
            in: query
            schema:
              type: number
            required: false
          - name: order_by
            description: |
              Order the composes by the given field. If ``-`` prefix is used,
              the order will be descending. The default value is ``-id``.
              Available fields are:
              - id
              - owner
              - source_type
              - koji_event
              - state
              - time_to_expire
              - time_done
              - time_removed
            in: query
            schema:
              type: string
            required: false
        responses:
          200:
            content:
              application/json:
                schema: ComposeListSchema
          404:
            description: Compose not found.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        p_query = filter_composes(request)

        json_data = {
            "meta": pagination_metadata(p_query, request.args),
            "items": [item.json() for item in p_query.items],
        }

        return jsonify(json_data), 200

    @login_required
    @require_scopes("new-compose")
    @requires_role("allowed_clients")
    def post(self):
        """Create new ODCS compose.

        ---
        summary: Create compose
        description: Create new ODCS compose
        requestBody:
          content:
            application/json:
              schema:
                type: object
                properties:
                  seconds_to_live:
                    type: integer
                    description: Number of seconds before the compose expires.
                  flags:
                    type: array of string
                    description: List of compose flags defined as strings.
                  arches:
                    type: array of string
                    description: List of arches the compose should be generated for.
                  multilib_arches:
                    type: array of string
                    description: List of multilib arches.
                  multilib_method:
                    type: array of string
                    description: List defining the multilib method.
                  lookaside_repos:
                    type: array of string
                    description: List of lookaside_repos.
                  label:
                    type: string
                    description: String defining the label.
                  compose_type:
                    type: string
                    description: String defining the compose_type.
                  target_dir:
                    type: string
                    description: String defining the target_dir.
                  parent_pungi_compose_ids:
                    type: array of number
                    description: |
                      Pungi compose IDs of parent composes associated with this compose. They will be
                      stored with this compose in the Compose Tracking Service.
                  respin_of:
                    type: string
                    description: |
                      Pungi compose ID of compose this compose respins.
                      It will be stored with this compose in the Compose Tracking Service.
                  source:
                    type: object
                    description: The JSON object defining the source of compose.
                    properties:
                      type:
                        type: string
                        description: String defining the source type.
                      source:
                        type: string
                        description: String defining the source.
                      packages:
                        type: array of string
                        description: List defining the packages.
                      builds:
                        type: array of string
                        description: List defining the builds.
                      sigkeys:
                        type: array of string
                        description: List defining the sigkeys.
                      koji_event:
                        type: number
                        description: Number defining the koji_event.
                      modular_koji_tags:
                        type: array of string
                        description: List defining the modular_koji_tags.
                      scratch_modules:
                        type: array of string
                        description: List defining the scratch_modules.
                      scratch_build_tasks:
                        type: array of string
                        description: List defining the scratch_build_tasks.
                      modules:
                        type: array of string
                        description: List defining the modules.
                      base_module_br_name:
                        type: string
                        description: String defining the base_module_br_name.
                      base_module_br_stream:
                        type: string
                        description: String defining the base_module_br_stream.
                      base_module_br_stream_version_lte:
                        type: string
                        description: Number defining the base_module_br_stream_version_lte.
                      base_module_br_stream_version_gte:
                        type: string
                        description: Number defining the base_module_br_stream_version_gte.
        responses:
          200:
            description: Compose request created and updated ComposeInfo returned.
            content:
              application/json:
                schema: ComposeSchema
          400:
            description: Request not in valid format.
            content:
              application/json:
                schema: HTTPErrorSchema
          401:
            description: User is unathorized.
            content:
              text/html:
                schema:
                  type: string
          403:
            description: User is not allowed to add compose.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        data = request.get_json(force=True)
        if not data:
            raise ValueError("No JSON POST data submitted")

        validate_json_data(data)

        source_data = data.get("source", None)
        if not isinstance(source_data, dict):
            err = "Invalid source configuration provided: %s" % str(data)
            log.error(err)
            raise ValueError(err)

        needed_keys = ["type"]
        for key in needed_keys:
            if key not in source_data:
                err = "Missing %s in source configuration, received: %s" % (
                    key,
                    str(source_data),
                )
                log.error(err)
                raise ValueError(err)

        source_type = source_data["type"]
        if source_type not in PUNGI_SOURCE_TYPE_NAMES:
            err = 'Unknown source type "%s"' % source_type
            log.error(err)
            raise ValueError(err)

        source_type = PUNGI_SOURCE_TYPE_NAMES[source_type]

        source = []
        if "source" in source_data and source_data["source"] != "":
            # Use list(set()) here to remove duplicate sources.
            source = list(set(source_data["source"].split(" ")))

        modules = None
        if "modules" in source_data:
            modules = " ".join(source_data["modules"])

        scratch_modules = None
        if "scratch_modules" in source_data:
            scratch_modules = " ".join(source_data["scratch_modules"])

        if (
            not source
            and source_type != PungiSourceType.BUILD
            and not (source_type == PungiSourceType.MODULE and scratch_modules)
        ):
            err = "No source provided for %s" % source_type
            log.error(err)
            raise ValueError(err)

        # Validate `source` based on `source_type`.
        raw_config_key = None
        if source_type == PungiSourceType.RAW_CONFIG:
            if len(source) > 1:
                raise ValueError(
                    'Only single source is allowed for "raw_config" ' "source_type"
                )

            source_name_hash = source[0].split("#")
            if (
                len(source_name_hash) != 2
                or not source_name_hash[0]
                or not source_name_hash[1]
            ):
                raise ValueError(
                    'Source must be in "source_name#commit_hash" format for '
                    '"raw_config" source_type.'
                )

            source_name, source_hash = source_name_hash
            if source_name not in conf.raw_config_urls:
                raise ValueError(
                    'Source "%s" does not exist in server configuration.' % source_name
                )
            raw_config_key = source_name
        elif source_type == PungiSourceType.MODULE:
            for module_str in source:
                nsvc = module_str.split(":")
                if len(nsvc) < 2:
                    raise ValueError(
                        'Module definition must be in "n:s", "n:s:v" or '
                        '"n:s:v:c" format, but got %s' % module_str
                    )
                if nsvc[0] in conf.base_module_names:
                    raise ValueError(
                        "ODCS currently cannot create compose with base "
                        "modules, but %s was requested." % nsvc[0]
                    )

        seconds_to_live = _get_seconds_to_live(data, raw_config_key)

        source = " ".join(source)

        packages = None
        if "packages" in source_data:
            packages = " ".join(source_data["packages"])

        builds = None
        if "builds" in source_data:
            if not isinstance(source_data["builds"], list):
                raise ValueError("builds should be a list")
            builds = " ".join(source_data["builds"])

        sigkeys = ""
        if "sigkeys" in source_data:
            sigkeys = " ".join(source_data["sigkeys"])
        else:
            sigkeys = " ".join(conf.sigkeys)

        koji_event = source_data.get("koji_event", None)

        flags = 0
        if "flags" in data:
            for name in data["flags"]:
                if name not in COMPOSE_FLAGS:
                    raise ValueError("Unknown flag %s", name)
                flags |= COMPOSE_FLAGS[name]

        results = COMPOSE_RESULTS["repository"]
        if "results" in data:
            for name in data["results"]:
                if name not in COMPOSE_RESULTS:
                    raise ValueError("Unknown result %s", name)
                results |= COMPOSE_RESULTS[name]

        arches = None
        if "arches" in data:
            arches = " ".join(data["arches"])
        else:
            arches = " ".join(conf.arches)

        multilib_arches = ""
        if "multilib_arches" in data:
            multilib_arches = " ".join(data["multilib_arches"])

        lookaside_repos = ""
        if "lookaside_repos" in data:
            lookaside_repos = " ".join(data["lookaside_repos"])

        parent_pungi_compose_ids = None
        if "parent_pungi_compose_ids" in data:
            parent_pungi_compose_ids = " ".join(data["parent_pungi_compose_ids"])

        respin_of = data.get("respin_of", None)

        multilib_method = MULTILIB_METHODS["none"]
        if "multilib_method" in data:
            for name in data["multilib_method"]:
                if name not in MULTILIB_METHODS:
                    raise ValueError('Unknown multilib method "%s"' % name)
                multilib_method |= MULTILIB_METHODS[name]

        modular_koji_tags = None
        if "modular_koji_tags" in source_data:
            modular_koji_tags = " ".join(source_data["modular_koji_tags"])

        module_defaults_url = None
        if "module_defaults_url" in source_data:
            module_defaults_url = source_data["module_defaults_url"]

        module_defaults_commit = None
        if "module_defaults_commit" in source_data:
            module_defaults_commit = source_data["module_defaults_commit"]

        module_defaults = None
        # The "^" operator is logical XOR.
        if bool(module_defaults_url) ^ bool(module_defaults_commit):
            raise ValueError(
                'The "module_defaults_url" and "module_defaults_commit" '
                "must be used together."
            )
        elif module_defaults_url and module_defaults_commit:
            module_defaults = "%s %s" % (module_defaults_url, module_defaults_commit)

        scratch_build_tasks = None
        if "scratch_build_tasks" in source_data:
            scratch_build_tasks = " ".join(source_data["scratch_build_tasks"])

        base_module_br_name = source_data.get("base_module_br_name", None)
        base_module_br_stream = source_data.get("base_module_br_stream", None)
        base_module_br_stream_version_lte = source_data.get(
            "base_module_br_stream_version_lte"
        )
        base_module_br_stream_version_gte = source_data.get(
            "base_module_br_stream_version_gte"
        )

        label = data.get("label", None)
        compose_type = data.get("compose_type", "test")

        target_dir = data.get("target_dir")
        if target_dir and target_dir != "default":
            if target_dir not in conf.extra_target_dirs:
                raise ValueError('Unknown "target_dir" "%s"' % target_dir)
            target_dir = conf.extra_target_dirs[target_dir]
        else:
            target_dir = conf.target_dir

        raise_if_input_not_allowed(
            source_types=source_type,
            sources=source,
            results=results,
            flags=flags,
            arches=arches,
            compose_types=compose_type,
            target_dirs=target_dir,
            raw_config_keys=raw_config_key,
        )

        compose = Compose.create(
            db.session,
            _get_compose_owner(),
            source_type,
            source,
            results,
            seconds_to_live,
            packages,
            flags,
            sigkeys,
            koji_event,
            arches,
            multilib_arches=multilib_arches,
            multilib_method=multilib_method,
            builds=builds,
            lookaside_repos=lookaside_repos,
            modular_koji_tags=modular_koji_tags,
            module_defaults_url=module_defaults,
            label=label,
            compose_type=compose_type,
            target_dir=target_dir,
            scratch_modules=scratch_modules,
            parent_pungi_compose_ids=parent_pungi_compose_ids,
            scratch_build_tasks=scratch_build_tasks,
            modules=modules,
            respin_of=respin_of,
            base_module_br_name=base_module_br_name,
            base_module_br_stream=base_module_br_stream,
            base_module_br_stream_version_lte=base_module_br_stream_version_lte,
            base_module_br_stream_version_gte=base_module_br_stream_version_gte,
            traceparent=_get_traceparent(),
        )
        db.session.add(compose)
        # Flush is needed, because we use `before_commit` SQLAlchemy event to
        # send message and before_commit can be called before flush and
        # therefore the compose ID won't be set.
        db.session.flush()
        db.session.commit()

        if CELERY_AVAILABLE and conf.celery_broker_url:
            _run_schedule_compose(compose)

        return jsonify(compose.json()), 200


class ComposeDetailAPI(MethodView):
    @cors_header()
    def get(self, id):
        """Returns metadata of compose with specified id.

        ---
        summary: Get compose
        description: |
          Get single compose by compose id. It returns compose in json format, for example:

              {
                  "arches": "x86_64",
                  "builds": null,
                  "flags": [],
                  "id": 470,
                  "koji_event": null,
                  "lookaside_repos": "",
                  "modular_koji_tags": null,
                  "module_defaults_url": null,
                  "multilib_arches": "",
                  "multilib_method": 0,
                  "owner": "osbs@service",
                  "packages": null,
                  "removed_by": null,
                  "result_repo": "https://localhost/latest-odcs-470-1/...",
                  "result_repofile": "https://localhost/.../odcs-470.repo",
                  "sigkeys": "",
                  "source": "flatpak-common:f30:3020190718103837:548d4c8d",
                  "source_type": 2,
                  "state": 2,
                  "state_name": "done",
                  "state_reason": "Compose is generated successfully",
                  "time_done": "2019-07-23T11:26:26Z",
                  "time_removed": null,
                  "time_submitted": "2019-07-23T11:24:54Z",
                  "time_to_expire": "2019-07-24T11:24:54Z",
                  "time_started": "2019-07-23T11:25:01Z"
              }
        parameters:
          - name: id
            description: Compose ID
            in: path
            schema:
              type: number
            required: true
        responses:
          200:
            content:
              application/json:
                schema: ComposeSchema
          404:
            description: Compose not found.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        compose = Compose.query.filter_by(id=id).first()
        if compose:
            return jsonify(compose.json(True)), 200
        else:
            raise NotFound("No such compose found.")

    @login_required
    @require_scopes("renew-compose")
    @requires_role("allowed_clients")
    def patch(self, id):
        """Extends the compose expiration time or regenerates expired compose.

        ---
        summary: Renew compose
        description: |
          Renew a compose in one of the following ways:
            - Create a new compose with same options when
                - the compose is failed or removed(expired)
                - or defined label but different with original value
                - or defined sigkeys but different with original value
                - or defined source["builds"] and/or source["modules"]
            - Extends the compose expiration time
        parameters:
          - name: id
            description: Compose ID
            in: path
            schema:
              type: number
            required: true
        requestBody:
          content:
            application/json:
              schema:
                type: object
                properties:
                  label:
                    type: string
                    description: |
                      Optional string defining the `label`.
                      If not defined, original `label` will be used.
                  seconds_to_live:
                    type: number
                    description: |
                      Optional number of seconds before the compose expires.
                      If not defined, the default value from odcs config file will be used.
                  sigkeys:
                    type: array of string
                    description: |
                      Optional list defining the `sigkeys`.
                      If not defined, original `sigkeys` will be used.
                  source:
                    type: object
                    description: Optional JSON object allowing to override the source of compose.
                    properties:
                      builds:
                        type: array of string
                        description: |
                          Optional list of `builds` to be included in the compose.
                          If defined, a new compose will be created.
                      modules:
                        type: array of string
                        description: |
                          Optional list of `modules` to be included in the compose.
                          If defined, a new compose will be created.
        responses:
          200:
            description: Compose renewed.
            content:
              application/json:
                schema: ComposeSchema
          400:
            description: Invalid seconds_to_live specified
            content:
              application/json:
                schema: HTTPErrorSchema
          401:
            description: User is unathorized.
            content:
              text/html:
                schema:
                  type: string
          403:
            description: User is not allowed to edit compose.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Compose not found.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        if request.data:
            data = request.get_json(force=True)
        else:
            data = {}
        validate_json_data(data)

        old_compose = Compose.query.filter(
            Compose.id == id,
            Compose.state.in_(
                [
                    COMPOSE_STATES["removed"],
                    COMPOSE_STATES["done"],
                    COMPOSE_STATES["failed"],
                ]
            ),
        ).first()

        if not old_compose:
            err = "No compose with id %s found" % id
            log.error(err)
            raise NotFound(err)

        # Backward compatibility for old composes which don't have
        # the compose_type set - we treat them as "test" composes
        # when regenerating them.
        compose_type = old_compose.compose_type or "test"

        sigkeys = ""
        if "sigkeys" in data:
            sigkeys = " ".join(data["sigkeys"])
        else:
            sigkeys = old_compose.sigkeys

        label = data.get("label", None) or old_compose.label

        source_data = data.get("source", {})

        modules = None
        if "modules" in source_data:
            modules = " ".join(source_data["modules"])

        builds = None
        if "builds" in source_data:
            if not isinstance(source_data["builds"], list):
                raise ValueError("builds should be a list")
            builds = " ".join(source_data["builds"])

        # Get the raw_config_key if this compose is RAW_CONFIG.
        raw_config_key = None
        if old_compose.source_type == PungiSourceType.RAW_CONFIG:
            raw_config_key = old_compose.source.split("#")[0]

        seconds_to_live = _get_seconds_to_live(data, raw_config_key)

        raise_if_input_not_allowed(
            source_types=old_compose.source_type,
            sources=old_compose.source,
            results=old_compose.results,
            flags=old_compose.flags,
            arches=old_compose.arches,
            compose_types=compose_type,
            raw_config_keys=raw_config_key,
        )

        has_to_create_a_copy = (
            old_compose.state in (COMPOSE_STATES["removed"], COMPOSE_STATES["failed"])
            or label != old_compose.label
            or sigkeys != old_compose.sigkeys
            or modules is not None
            or builds is not None
        )
        if has_to_create_a_copy:
            log.info("%r: Going to regenerate the compose", old_compose)
            compose = Compose.create_copy(
                db.session,
                old_compose,
                _get_compose_owner(),
                seconds_to_live,
                sigkeys=sigkeys,
                traceparent=_get_traceparent(),
                label=label,
            )
            if modules:
                compose.modules = modules
            if builds:
                compose.builds = builds

            compose.respin_of = old_compose.pungi_compose_id
            db.session.add(compose)
            # Flush is needed, because we use `before_commit` SQLAlchemy
            # event to send message and before_commit can be called before
            # flush and therefore the compose ID won't be set.
            db.session.flush()
            db.session.commit()

            if CELERY_AVAILABLE and conf.celery_broker_url:
                _run_schedule_compose(compose)

            return jsonify(compose.json()), 200
        else:
            # Otherwise, just extend expiration to make it usable for longer
            # time.
            extend_from = datetime.datetime.utcnow()
            old_compose.extend_expiration(extend_from, seconds_to_live)
            log.info(
                "Extended time_to_expire for compose %r to %s",
                old_compose,
                old_compose.time_to_expire,
            )
            # As well as extending those composes that reuse this this compose,
            # and the one this compose reuses.
            reused_compose = old_compose.get_reused_compose()
            if reused_compose:
                reused_compose.extend_expiration(extend_from, seconds_to_live)
            for c in old_compose.get_reusing_composes():
                c.extend_expiration(extend_from, seconds_to_live)
            db.session.commit()
            return jsonify(old_compose.json()), 200

    @login_required
    @require_scopes("delete-compose")
    def delete(self, id):
        """Delete compose.

        ---
        summary: Delete compose
        description: |
          Cancels waiting compose or marks finished compose as expired to be
          removed later from ODCS storage. The compose metadata are still stored
          in the ODCS database, only the composed files stored in ODCS storage
          are removed.

          Users are allowed to cancel their own composes. Deleting is limited to
          admins. Admins can also cancel any compose.
        parameters:
          - name: id
            description: ID of compose to be deleted.
            in: path
            schema:
              type: number
            required: true
        responses:
          202:
            description: Compose has been canceled or marked as expired.
            content:
              application/json:
                schema: ComposeDeleteSchema
          400:
            description: Compose is not in `wait`, `done` or `failed` state.
            content:
              application/json:
                schema: HTTPErrorSchema
          401:
            description: User is unathorized.
            content:
              text/html:
                schema:
                  type: string
          403:
            description: User doesn't own the compose to be cancelled or is not admin.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Compose not found.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        compose = Compose.query.filter_by(id=id).first()
        if not compose:
            raise NotFound("No such compose found.")

        is_admin = has_role("admins")

        # First try to cancel the compose
        if CELERY_AVAILABLE and compose.state == COMPOSE_STATES["wait"]:
            if not is_admin and compose.owner != g.user.username:
                raise Forbidden(
                    "Compose (id=%s) can not be canceled, it's owned by someone else."
                )

            # Revoke the task
            if compose.celery_task_id:
                celery_app.control.revoke(compose.celery_task_id)
            # Change compose status to failed
            compose.transition(
                COMPOSE_STATES["failed"], "Canceled by %s" % g.user.username
            )
            message = "Compose (id=%s) has been canceled" % id
            response = jsonify({"status": 202, "message": message})
            response.status_code = 202
            return response

        # Compose was not eligible for cancellation, try to delete it instead.
        # Only admins can do this.
        if not is_admin:
            raise Forbidden("User %s is not in role admins." % g.user.username)

        # can remove compose that is in state of 'done' or 'failed'
        deletable_states = {n: COMPOSE_STATES[n] for n in ["done", "failed"]}
        if compose.state not in deletable_states.values():
            raise ValueError(
                "Compose (id=%s) can not be removed, its state need to be in %s."
                % (id, list(deletable_states.keys()))
            )

        # change compose.time_to_expire to now, so backend will
        # delete this compose as it's an expired compose now
        compose.time_to_expire = datetime.datetime.utcnow()
        try:
            compose.removed_by = g.user.username
        except AttributeError:
            compose.removed_by = "anonymous"
            log.info(
                "User info could not found, it is removed by %s" % compose.removed_by
            )

        db.session.add(compose)
        db.session.commit()
        message = (
            "The delete request for compose (id=%s) has been accepted and will be"
            " processed by backend later." % compose.id
        )
        response = jsonify({"status": 202, "message": message})
        response.status_code = 202
        return response


class MetricsAPI(MethodView):
    @cors_header()
    def get(self):
        """Returns the Prometheus metrics.

        ---
        summary: Metrics
        description: Returns the Prometheus metrics.
        responses:
          200:
            content:
              text/plain:
                schema:
                  type: string
        """
        m = Metrics.query.order_by(Metrics.id.desc()).first()
        if m:
            content = m.metrics
        else:
            content = ""
        return Response(content, content_type=CONTENT_TYPE_LATEST)


class AboutAPI(MethodView):
    @cors_header()
    def get(self):
        """Returns information about this ODCS instance in JSON format.

        ---
        summary: About
        description: Returns information about this ODCS instance in JSON format.
        responses:
          200:
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    version:
                      description: The ODCS server version.
                      type: string
                    auth_backend:
                      description: |
                        The name of authorization backend this server is configured with.
                        - ``noauth`` - No authorization is required.
                        - ``kerberos`` - Kerberos authorization is required.
                        - ``openidc`` - OpenIDC authorization is required.
                        - ``kerberos_or_ssl`` - Kerberos or SSL authorization is required.
                        - ``ssl`` - SSL authorization is required.
                      type: string
                      enum:
                        - noauth
                        - kerberos
                        - openidc
                        - kerberos_or_ssl
                        - ssl
                    allowed_clients:
                      type: object
                    raw_config_urls:
                      type: object
                    sigkeys:
                      type: array of string
        """
        json = {"version": version}
        config_items = ["auth_backend", "allowed_clients", "raw_config_urls", "sigkeys"]
        for item in config_items:
            config_item = getattr(conf, item)
            # All config items have a default, so if doesn't exist it is
            # an error
            if config_item is None:
                raise ValueError('An invalid config item of "%s" was specified' % item)
            json[item] = config_item
        return jsonify(json), 200


class Index(View):
    methods = ["GET"]

    def dispatch_request(self):
        return render_template("index.html", target_dir_url=conf.target_dir_url)


class Favicon(View):
    methods = ["GET"]

    def dispatch_request(self):
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )


class APIDoc(View):
    methods = ["GET"]

    def dispatch_request(self):
        return render_template("apidoc.html")


def register_api_v1():
    """Registers version 1 of ODCS API."""
    api_v1 = {
        "composes": {
            "url": "/api/1/composes/",
            "options": {"methods": ["GET", "POST"]},
            "view_class": ComposesListAPI,
        },
        "composedetail": {
            "url": "/api/1/composes/<int:id>",
            "options": {"methods": ["GET", "PATCH", "DELETE"]},
            "view_class": ComposeDetailAPI,
        },
        "about": {
            "url": "/api/1/about/",
            "options": {"methods": ["GET"]},
            "view_class": AboutAPI,
        },
        "metrics": {
            "url": "/api/1/metrics/",
            "options": {"methods": ["GET"]},
            "view_class": MetricsAPI,
        },
    }

    for key, val in api_v1.items():
        view_func = val["view_class"].as_view(key)
        app.add_url_rule(
            val["url"], endpoint=key, view_func=view_func, **val["options"]
        )
        if app.openapispec:
            with app.test_request_context():
                app.openapispec.path(view=view_func)


app.add_url_rule("/", view_func=Index.as_view("index"))
app.add_url_rule("/favicon.ico", view_func=Favicon.as_view("favicon"))
app.add_url_rule("/api/1/", view_func=APIDoc.as_view("apidoc"))
register_api_v1()

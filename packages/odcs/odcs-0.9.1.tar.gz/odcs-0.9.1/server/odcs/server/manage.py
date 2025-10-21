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

import logging
import os
import ssl
import sys
import time

import click
import flask_migrate

from flask.cli import FlaskGroup
from itertools import chain
from werkzeug.serving import run_simple

from odcs.server import app, conf, db
from odcs.server.utils import log_errors


def _establish_ssl_context():
    if not conf.ssl_enabled:
        return None
    # First, do some validation of the configuration
    attributes = (
        "ssl_certificate_file",
        "ssl_certificate_key_file",
        "ssl_ca_certificate_file",
    )

    for attribute in attributes:
        value = getattr(conf, attribute, None)
        if not value:
            raise ValueError("%r could not be found" % attribute)
        if not os.path.exists(value):
            raise OSError("%s: %s file not found." % (attribute, value))

    # Then, establish the ssl context and return it
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_ctx.load_cert_chain(conf.ssl_certificate_file, conf.ssl_certificate_key_file)
    ssl_ctx.verify_mode = ssl.CERT_OPTIONAL
    ssl_ctx.load_verify_locations(cafile=conf.ssl_ca_certificate_file)
    return ssl_ctx


@click.group(cls=FlaskGroup, create_app=lambda *args, **kwargs: app)
def cli():
    """Manage ODCS application"""


migrations_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "migrations")
flask_migrate.Migrate(app, db, directory=migrations_dir)


@cli.command()
@click.option("-h", "--host", default=conf.host, help="Bind to this address")
@click.option("-p", "--port", type=int, default=conf.port, help="Listen on this port")
@click.option("-d", "--debug", is_flag=True, default=conf.debug, help="Debug mode")
def runssl(host, port, debug):
    """Runs the Flask app with the HTTPS settings configured in config.py"""
    logging.info("Starting ODCS frontend")

    ssl_ctx = _establish_ssl_context()
    run_simple(host, port, app, use_debugger=debug, ssl_context=ssl_ctx)


@cli.command()
@click.option(
    "-i",
    "--interval",
    type=int,
    default=0,
    help="Run cleanup every {interval} minutes, it only runs once by default.",
)
def cleanup(interval):
    """Run cleanup tasks."""
    from odcs.server.celery_tasks import (
        reschedule_waiting_composes,
        fail_lost_generating_composes,
        cleanup_generating_composes,
        run_cleanup,
        celery_app,
    )

    while True:
        with log_errors("Error while marking lost generating composes as failed"):
            logging.info("Marking lost generating composes as failed ...")
            fail_lost_generating_composes()
        with log_errors("Error while rescheduling waiting composes"):
            logging.info("Rescheduling waiting composes ...")
            reschedule_waiting_composes()
        with log_errors("Error while cleanup generating composes"):
            logging.info("Cleanup generating composes ...")
            cleanup_generating_composes()

        skip = False
        inspection = celery_app.control.inspect()
        for i in chain(
            (inspection.active() or {}).values(),
            (inspection.reserved() or {}).values(),
        ):
            for t in i:
                if "run_cleanup" in t["name"]:
                    skip = True
                    break
        if skip:
            logging.info(
                "Skip sending run_cleanup task as it's already in the task queue."
            )
        else:
            logging.info("Send run_cleanup task to remove expired composes")
            run_cleanup.delay()

        if interval:
            time.sleep(interval * 60)
        else:
            break


@cli.command()
def openapispec():
    """Dump OpenAPI specification"""
    import json

    if app.openapispec:
        print(json.dumps(app.openapispec.to_dict(), indent=2))
    else:
        logging.error("Can't generate OpenAPI specification.")
        sys.exit(1)


@cli.command()
@click.option(
    "-i",
    "--interval",
    type=int,
    default=30,
    help="Collect metrics every {interval} seconds, default 30 seconds.",
)
def metrics(interval):
    """Collect metrics."""
    from odcs.server.metrics import MetricsCollector

    collector = MetricsCollector()
    collector.run(interval)


if __name__ == "__main__":
    cli()

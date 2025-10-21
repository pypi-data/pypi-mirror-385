# -*- coding: utf-8 -*-

# Copyright (c) 2020  Red Hat, Inc.
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

import time
from sqlalchemy import func
from prometheus_client import CollectorRegistry, Gauge, Counter, generate_latest

from odcs.common.types import COMPOSE_STATES, PUNGI_SOURCE_TYPE_NAMES
from odcs.server.models import Compose, Metrics
from odcs.server import log, conf, db

try:
    from odcs.server.celery_tasks import celery_app
    from celery.utils.objects import FallbackContext
    import amqp.exceptions

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False


class MetricsCollector:
    """Collect following metrics:

    - celery_workers_expected - Number of expected workers.
    - celery_workers_totals - Number of alive workers.
    - celery_workers[worker_name] - 1 if worker is online, 0 if offline.
    - celery_queue_length[queue_name] - Number of tasks waiting in the queue.
    - celery_queue_worker[queue_name] - Number of workers consume tasks from the queue.
    - composes_total - Total number of composes per source_type and state.
    - raw_config_composes_count_total - Total number of raw_config composes per source.
    - raw_config_composes - Count of raw config composes broken down by state. Removed composes are not counted.
    """

    def __init__(self):
        super(MetricsCollector, self).__init__()
        self.registry = CollectorRegistry()
        self.workers_expected = Gauge(
            "celery_workers_expected",
            "Number of expected workers",
            registry=self.registry,
        )
        self.workers_expected.set(conf.expected_backend_number)

        self.workers_total = Gauge(
            "celery_workers_totals", "Number of alive workers", registry=self.registry
        )
        self.workers_total.set(0)

        self.workers = Gauge(
            "celery_workers",
            "Number of alive workers",
            ["worker_name"],
            registry=self.registry,
        )
        self.worker_names = set()

        self.queue_length = Gauge(
            "celery_queue_length",
            "Number of tasks in the queue.",
            ["queue_name"],
            registry=self.registry,
        )

        # Get all the possible queue names from the config.
        self.queues = [conf.celery_cleanup_queue]
        for rules in conf.celery_router_config["routing_rules"].values():
            self.queues += rules.keys()
        # Initialize the queue length to 0.
        for queue in self.queues:
            self.queue_length.labels(queue).set(0)

        # Get the Celery connetion.
        self.connection = celery_app.connection_or_acquire()
        if isinstance(self.connection, FallbackContext):
            self.connection = self.connection.fallback()

        self.queue_worker = Gauge(
            "celery_queue_worker",
            "Number of workers consume tasks from the queue.",
            ["queue_name"],
            registry=self.registry,
        )

        self.composes_total = Gauge(
            "composes_total",
            "Total number of composes",
            ["source_type", "state"],
            registry=self.registry,
        )
        self.raw_config_composes_count_data = {}
        self.raw_config_composes_count = Counter(
            "raw_config_composes_count",
            "Total number of raw_config composes per source",
            ["source"],
            registry=self.registry,
        )
        self.raw_config_composes = Gauge(
            "raw_config_composes",
            "Count of raw config composes broken down by state. Removed composes are not counted.",
            ["source", "state"],
            registry=self.registry,
        )

    def update_worker_metrics(self):
        log.info("[metrics] Getting number of workers.")
        try:
            celery_ping = celery_app.control.ping(timeout=15)
        except Exception:  # pragma: no cover
            log.exception("[metrics] Error pinging workers.")
            return

        # Set total number of workers.
        self.workers_total.set(len(celery_ping))

        # Set all known workers to 0 to mark them offline.
        for workers in celery_ping:
            self.worker_names |= set(workers.keys())
        for worker_name in self.worker_names:
            self.workers.labels(worker_name).set(0)

        # Set online workers to 1.
        for workers in celery_ping:
            for worker_name in workers.keys():
                self.workers.labels(worker_name).set(1)

    def update_queue_metrics(self):
        for queue in self.queues:
            try:
                log.info("[metrics] Getting %s queue length." % queue)
                length = self.connection.default_channel.queue_declare(
                    queue=queue, passive=True
                ).message_count
                self.queue_length.labels(queue).set(length)
            except amqp.exceptions.ChannelError:
                # Queue not created yet.
                pass
            except Exception:  # pragma: no cover
                log.exception("[metrics] Error getting queue length.")

    def update_queue_worker_metrics(self):
        log.info("[metrics] Getting queue worker number.")
        try:
            active_queues = celery_app.control.inspect().active_queues()
        except Exception:  # pragma: no cover
            log.exception("[metrics] Error inspect active queues.")
            return

        # Initialize the queue worker to 0.
        for queue in self.queues:
            self.queue_worker.labels(queue).set(0)

        if active_queues:
            for queues in active_queues.values():
                for q in queues:
                    self.queue_worker.labels(q["name"]).inc()

    def update_composes_total(self):
        """
        Updates `composes_total` metric with number of composes for each state
        and source_type.
        """
        for state in COMPOSE_STATES:
            for source_type in PUNGI_SOURCE_TYPE_NAMES:
                count = Compose.query.filter(
                    Compose.source_type == PUNGI_SOURCE_TYPE_NAMES[source_type],
                    Compose.state == COMPOSE_STATES[state],
                ).count()

                self.composes_total.labels(source_type, state).set(count)

    def update_raw_config_composes_count(self):
        """
        Updates `raw_config_composes_count_total` metrics with number of
        raw_config composes for each `Compose.source`. For raw_config composes,
        the Compose.source is stored in the `raw_config_key#commit_or_branch`
        format. If particular `Compose.source` is generated only few times
        (less than 5), it is grouped by the `raw_config_key` and particular
        `commit_or_branch` is replaced with "other_commits_or_branches" string.

        This is needed to handle the situation when particular raw_config
        compose is generated just once using particular commit hash (and not a
        branch name). These single composes are not that important in the
        metrics and therefore we group them like that.
        """
        composes = (
            Compose.query.with_entities(Compose.source, func.count(Compose.source))
            .filter(Compose.source_type == PUNGI_SOURCE_TYPE_NAMES["raw_config"])
            .group_by(Compose.source)
            .all()
        )

        sources = {}
        for source, count in composes:
            if count < 5:
                name = "%s#other_commits_or_branches" % source.split("#")[0]
                if name not in sources:
                    sources[name] = 0
                sources[name] += count
            else:
                sources[source] = count

        for source, count in sources.items():
            increment = count - self.raw_config_composes_count_data.get(source, 0)
            self.raw_config_composes_count_data[source] = count
            if increment >= 0:
                self.raw_config_composes_count.labels(source).inc(increment)
            else:
                log.error(
                    "Count of raw config composes for %s went down from %d to %d",
                    source,
                    self.raw_config_composes_count_data.get(source, 0),
                    count,
                )

    def update_raw_config_types(self):
        composes = (
            Compose.query.with_entities(
                Compose.source, Compose.state, func.count(Compose.source)
            )
            .filter(
                Compose.source_type == PUNGI_SOURCE_TYPE_NAMES["raw_config"],
                Compose.state != COMPOSE_STATES["removed"],
            )
            .group_by(Compose.state, Compose.source)
            .all()
        )

        composes_by_source_by_state = {}
        for source, state, count in composes:
            composes_by_source_by_state.setdefault(source, {})[state] = count

        for source in composes_by_source_by_state:
            for state_name, state_val in COMPOSE_STATES.items():
                if state_name == "removed":
                    continue
                count = composes_by_source_by_state[source].get(state_val, 0)
                self.raw_config_composes.labels(source, state_name).set(count)

    def update_compose_metrics(self):
        log.info("[metrics] Getting compose counts.")
        self.update_composes_total()
        self.update_raw_config_composes_count()
        self.update_raw_config_types()

    def run(self, interval=30):
        while True:
            self.update_compose_metrics()
            if CELERY_AVAILABLE:
                self.update_worker_metrics()
                self.update_queue_metrics()
                self.update_queue_worker_metrics()

            metrics = generate_latest(self.registry)
            db.session.merge(Metrics(id=1, metrics=metrics.decode("utf-8")))
            db.session.commit()

            time.sleep(interval)

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
# Written by Chenxiong Qi <cqi@redhat.com>

import json
from logging import getLogger

from odcs.server import conf

log = getLogger(__name__)

__all__ = ("publish",)


def publish(msgs):
    """Start to send messages to message broker

    :param list[dict] msgs: List of messages to be sent.
    """
    backend = _get_messaging_backend()
    if backend is not None:
        backend(msgs)


def _kafka_send_msg(msgs):
    """Send messages to Kafka.

    :param list[dict] msgs: List of messages to be sent.
    :raises Exception: If Kafka operations fail
    """
    from kafka import KafkaProducer

    config = {
        "bootstrap_servers": conf.messaging_broker_urls,
        "compression_type": "snappy",
        "security_protocol": "SASL_SSL",
        "sasl_mechanism": "SCRAM-SHA-512",
        "sasl_plain_username": conf.messaging_kafka_username,
        "sasl_plain_password": conf.messaging_kafka_password,
        "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
    }

    producer = None
    try:
        producer = KafkaProducer(**config)

        # Send all messages first, then flush once for better performance
        for msg in msgs:
            log.info("Sending message to Kafka topic %s, %s", conf.messaging_topic, msg)
            producer.send(conf.messaging_topic, msg)

        # Single flush for all messages - more efficient than flushing each message
        producer.flush()

    except Exception as e:
        log.error("Failed to send messages to Kafka: %s", str(e))
        raise
    finally:
        # Ensure producer is always closed, even on exceptions
        if producer is not None:
            try:
                producer.close()
            except Exception as e:
                log.warning("Error closing Kafka producer: %s", str(e))


def _umb_send_msg(msgs):
    """Send message to Unified Message Bus"""

    import proton
    from rhmsg.activemq.producer import AMQProducer

    config = {
        "urls": conf.messaging_broker_urls,
        "certificate": conf.messaging_cert_file,
        "private_key": conf.messaging_key_file,
        "trusted_certificates": conf.messaging_ca_cert,
    }
    with AMQProducer(**config) as producer:
        producer.through_topic(conf.messaging_topic)

        for msg in msgs:
            outgoing_msg = proton.Message()
            outgoing_msg.body = json.dumps(msg)
            producer.send(outgoing_msg)


def _get_messaging_backend():
    if conf.messaging_backend == "kafka":
        return _kafka_send_msg
    elif conf.messaging_backend == "rhmsg":
        return _umb_send_msg
    elif conf.messaging_backend:
        raise ValueError("Unknown messaging backend {0}".format(conf.messaging_backend))
    else:
        return None

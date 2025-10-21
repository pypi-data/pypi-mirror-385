# -*- coding: utf-8 -*-
# Copyright (c) 2025  Red Hat, Inc.
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
# Written by Claude Code Assistant

import json
import unittest
from unittest.mock import patch, MagicMock, call

from odcs.server import conf
from odcs.server.messaging import _kafka_send_msg


class TestKafkaMessaging(unittest.TestCase):
    """Test Kafka messaging functionality."""

    def setUp(self):
        """Set up common test configuration."""
        self.config_patches = {
            "messaging_broker_urls": ["localhost:9092"],
            "messaging_kafka_username": "test_user",
            "messaging_kafka_password": "test_password",
            "messaging_topic": "test_topic",
        }
        self.patch_objects = []

        # Start all config patches
        for attr, value in self.config_patches.items():
            patcher = patch.object(conf, attr, value)
            self.patch_objects.append(patcher)
            patcher.start()

    def tearDown(self):
        """Clean up patches."""
        for patcher in self.patch_objects:
            patcher.stop()

    @patch("kafka.KafkaProducer")
    def test_kafka_send_msg_single_message(self, mock_kafka_producer):
        """Test sending a single message via Kafka."""
        # Setup mock producer
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        # Test data
        msgs = [{"event": "test", "data": "test_data"}]

        # Call the function
        _kafka_send_msg(msgs)

        # Verify KafkaProducer was created with correct config
        expected_config = {
            "bootstrap_servers": ["localhost:9092"],
            "compression_type": "snappy",
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "SCRAM-SHA-512",
            "sasl_plain_username": "test_user",
            "sasl_plain_password": "test_password",
            "value_serializer": mock_kafka_producer.call_args[1]["value_serializer"],
        }
        mock_kafka_producer.assert_called_once_with(**expected_config)

        # Verify message was sent
        mock_producer_instance.send.assert_called_once_with("test_topic", msgs[0])
        mock_producer_instance.flush.assert_called_once()
        mock_producer_instance.close.assert_called_once()

    @patch("kafka.KafkaProducer")
    def test_kafka_send_msg_multiple_messages(self, mock_kafka_producer):
        """Test sending multiple messages via Kafka."""
        # Setup mock producer
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        # Test data
        msgs = [
            {"event": "test1", "data": "test_data1"},
            {"event": "test2", "data": "test_data2"},
            {"event": "test3", "data": "test_data3"},
        ]

        # Call the function
        _kafka_send_msg(msgs)

        # Verify KafkaProducer was created
        mock_kafka_producer.assert_called_once()

        # Verify all messages were sent
        expected_calls = [call("test_topic", msg) for msg in msgs]
        mock_producer_instance.send.assert_has_calls(expected_calls)

        # Verify flush was called only once (performance improvement)
        mock_producer_instance.flush.assert_called_once()

        # Verify producer was closed
        mock_producer_instance.close.assert_called_once()

    def test_kafka_send_msg_empty_list(self):
        """Test sending empty message list via Kafka - should exit early."""
        with patch("kafka.KafkaProducer") as mock_kafka_producer:
            # Test data
            msgs = []

            # Call the function
            _kafka_send_msg(msgs)

            # Verify KafkaProducer was NOT created (early exit)
            mock_kafka_producer.send.assert_not_called()

    def test_kafka_send_msg_multiple_brokers(self):
        """Test Kafka configuration with multiple broker URLs."""
        # Override the default broker config for this test
        with patch.object(
            conf, "messaging_broker_urls", ["server1:9092", "server2:9092"]
        ):
            with patch("kafka.KafkaProducer") as mock_kafka_producer:
                # Setup mock producer
                mock_producer_instance = MagicMock()
                mock_kafka_producer.return_value = mock_producer_instance

                # Test data
                msgs = [{"event": "test", "data": "test_data"}]

                # Call the function
                _kafka_send_msg(msgs)

                # Verify KafkaProducer was created with multiple brokers
                call_args = mock_kafka_producer.call_args[1]
                self.assertEqual(
                    call_args["bootstrap_servers"], ["server1:9092", "server2:9092"]
                )

    @patch("kafka.KafkaProducer")
    def test_kafka_value_serializer(self, mock_kafka_producer):
        """Test the JSON value serializer function."""
        # Setup mock producer
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        # Test data
        test_message = {"event": "test", "data": {"nested": "value"}}
        msgs = [test_message]

        # Call the function
        _kafka_send_msg(msgs)

        # Get the serializer function from the mock call
        call_args = mock_kafka_producer.call_args[1]
        serializer = call_args["value_serializer"]

        # Test the serializer
        result = serializer(test_message)
        expected = json.dumps(test_message).encode("utf-8")
        self.assertEqual(result, expected)

        # Test serializer with various data types
        test_cases = [
            {"string": "value"},
            {"number": 123},
            {"boolean": True},
            {"null": None},
            {"array": [1, 2, 3]},
            {"nested": {"deep": {"value": "test"}}},
        ]

        for test_case in test_cases:
            result = serializer(test_case)
            expected = json.dumps(test_case).encode("utf-8")
            self.assertEqual(result, expected)

    @patch("kafka.KafkaProducer")
    def test_kafka_send_msg_producer_exception(self, mock_kafka_producer):
        """Test handling of KafkaProducer exceptions."""
        # Setup mock producer to raise exception
        mock_kafka_producer.side_effect = Exception("Kafka connection failed")

        # Test data
        msgs = [{"event": "test", "data": "test_data"}]

        # Verify exception is propagated
        with self.assertRaises(Exception) as context:
            _kafka_send_msg(msgs)

        self.assertIn("Kafka connection failed", str(context.exception))

    @patch("kafka.KafkaProducer")
    def test_kafka_send_msg_send_exception(self, mock_kafka_producer):
        """Test handling of send() method exceptions."""
        # Setup mock producer
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance
        mock_producer_instance.send.side_effect = Exception("Send failed")

        # Test data
        msgs = [{"event": "test", "data": "test_data"}]

        # Verify exception is propagated
        with self.assertRaises(Exception) as context:
            _kafka_send_msg(msgs)

        self.assertIn("Send failed", str(context.exception))

        # Verify producer close IS called even when send() fails (due to finally block)
        mock_producer_instance.close.assert_called_once()

    @patch("kafka.KafkaProducer")
    def test_kafka_send_msg_flush_exception(self, mock_kafka_producer):
        """Test handling of flush() method exceptions."""
        # Setup mock producer
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance
        mock_producer_instance.flush.side_effect = Exception("Flush failed")

        # Test data
        msgs = [{"event": "test", "data": "test_data"}]

        # Verify exception is propagated
        with self.assertRaises(Exception) as context:
            _kafka_send_msg(msgs)

        self.assertIn("Flush failed", str(context.exception))

        # Verify send was called and close was called (due to finally block)
        mock_producer_instance.send.assert_called_once()
        mock_producer_instance.close.assert_called_once()

    @patch("kafka.KafkaProducer")
    def test_kafka_configuration_values(self, mock_kafka_producer):
        """Test that all Kafka configuration values are correctly set."""
        # Setup mock producer
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        # Test data
        msgs = [{"event": "test", "data": "test_data"}]

        # Call the function
        _kafka_send_msg(msgs)

        # Verify all configuration parameters
        call_args = mock_kafka_producer.call_args[1]

        self.assertEqual(call_args["bootstrap_servers"], ["localhost:9092"])
        self.assertEqual(call_args["compression_type"], "snappy")
        self.assertEqual(call_args["security_protocol"], "SASL_SSL")
        self.assertEqual(call_args["sasl_mechanism"], "SCRAM-SHA-512")
        self.assertEqual(call_args["sasl_plain_username"], "test_user")
        self.assertEqual(call_args["sasl_plain_password"], "test_password")
        self.assertIn("value_serializer", call_args)

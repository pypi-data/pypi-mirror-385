# -*- coding: utf-8 -*-
#
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

import unittest

from mock import patch, call
import time
import subprocess

from odcs.server.utils import execute_cmd
from odcs.server.utils import clone_repo


class TestUtilsExecuteCmd(unittest.TestCase):
    def setUp(self):
        super(TestUtilsExecuteCmd, self).setUp()

    def tearDown(self):
        super(TestUtilsExecuteCmd, self).tearDown()

    def test_execute_cmd_timeout_called(self):
        start_time = time.time()
        with self.assertRaisesRegex(RuntimeError, "Compose has taken more time.*"):
            execute_cmd(["/usr/bin/sleep", "5"], timeout=1)
        stop_time = time.time()

        self.assertTrue(stop_time - start_time < 2)

    @patch("odcs.server.utils._kill_process_group")
    def test_execute_cmd_timeout_not_called(self, killpg):
        execute_cmd(["/usr/bin/true"], timeout=1)
        time.sleep(2)
        killpg.assert_not_called()


GIT_COMMAND = [
    "git",
    "-c",
    "credential.useHttpPath=true",
    "-c",
    "credential.helper=!odcs-credential-helper",
]


class TestCloneRepo(unittest.TestCase):
    def setUp(self):
        super(TestCloneRepo, self).setUp()
        self.dest = "/tmp/test_clone_repo"

    @patch("odcs.server.utils.execute_cmd")
    def test_clone_repo(self, ec):
        clone_repo("git://localhost/test.git", self.dest)

        self.assertEqual(
            ec.mock_calls,
            [
                call(
                    GIT_COMMAND + ["clone", "git://localhost/test.git", self.dest],
                    env=None,
                    stderr=subprocess.PIPE,
                ),
            ],
        )

    @patch("odcs.server.utils.execute_cmd")
    def test_clone_repo_branch(self, ec):
        clone_repo("git://localhost/test.git", self.dest, branch="main")

        self.assertEqual(
            ec.mock_calls,
            [
                call(
                    GIT_COMMAND
                    + ["clone", "-b", "main", "git://localhost/test.git", self.dest],
                    env=None,
                    stderr=subprocess.PIPE,
                ),
            ],
        )

    @patch("odcs.server.utils.execute_cmd")
    def test_clone_repo_commit(self, ec):
        clone_repo("git://localhost/test.git", self.dest, commit="hash")

        self.assertEqual(
            ec.mock_calls,
            [
                call(
                    GIT_COMMAND + ["clone", "git://localhost/test.git", self.dest],
                    env=None,
                    stderr=subprocess.PIPE,
                ),
                call(
                    ["git", "checkout", "hash"], cwd=self.dest, stderr=subprocess.PIPE
                ),
            ],
        )

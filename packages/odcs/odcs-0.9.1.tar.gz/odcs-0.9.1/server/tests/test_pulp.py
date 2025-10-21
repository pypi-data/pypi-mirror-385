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

from mock import patch

from . import mock_pungi  # noqa: F401

from odcs.server.pulp import Pulp
from odcs.server.pungi import PungiSourceType
from odcs.server import db
from odcs.server.models import Compose

from .utils import ModelsBaseTest


@patch("odcs.server.pulp.Pulp._rest_post")
class TestPulp(ModelsBaseTest):
    def test_pulp_request(self, pulp_rest_post):
        c = Compose.create(db.session, "me", PungiSourceType.PULP, "foo-1", 0, 3600)
        db.session.commit()

        pulp_rest_post.return_value = []

        pulp = Pulp("http://localhost/", "user", "pass", c)
        pulp.get_repos_from_content_sets(["foo-1", "foo-2"])
        pulp_rest_post.assert_called_once_with(
            "repositories/search/",
            {
                "criteria": {
                    "fields": ["notes", "id"],
                    "filters": {
                        "notes.include_in_download_service": "True",
                        "notes.content_set": {"$in": ["foo-1", "foo-2"]},
                    },
                }
            },
        )

    def test_pulp_request_include_inpublished(self, pulp_rest_post):
        c = Compose.create(db.session, "me", PungiSourceType.PULP, "foo-1", 0, 3600)
        db.session.commit()

        pulp_rest_post.return_value = []

        pulp = Pulp("http://localhost/", "user", "pass", c)
        pulp.get_repos_from_content_sets(["foo-1", "foo-2"], True)
        pulp_rest_post.assert_called_once_with(
            "repositories/search/",
            {
                "criteria": {
                    "fields": ["notes", "id"],
                    "filters": {"notes.content_set": {"$in": ["foo-1", "foo-2"]}},
                }
            },
        )

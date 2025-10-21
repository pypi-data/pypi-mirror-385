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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
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
#            Jan Kaluza <jkaluza@redhat.com>

import json
import requests
import requests.exceptions
from requests.models import ProtocolError

from odcs.server import conf, log
from odcs.server.utils import retry


class Pulp(object):
    """Interface to Pulp"""

    def __init__(self, server_url, ssl_cert, ssl_key, compose):
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.server_url = server_url
        self.compose = compose
        self.rest_api_root = "{0}/pulp/api/v2/".format(self.server_url.rstrip("/"))

    @retry(wait_on=(requests.exceptions.RequestException, ProtocolError))
    def _rest_post(self, endpoint, post_data):
        query_data = json.dumps(post_data)
        try:
            r = requests.post(
                "{0}{1}".format(self.rest_api_root, endpoint.lstrip("/")),
                query_data,
                cert=(self.ssl_cert, self.ssl_key),
                timeout=conf.net_timeout,
            )
        except requests.exceptions.RequestException as e:
            # also catches ConnectTimeout, ConnectionError
            # change message of the catched exception and re-raise
            msg = "Pulp connection has failed: {}".format(e.args)
            raise requests.exceptions.RequestException(msg)

        r.raise_for_status()
        return r.json()

    @retry(wait_on=requests.exceptions.RequestException)
    def _rest_get(self, endpoint):
        try:
            r = requests.get(
                "{0}{1}".format(self.rest_api_root, endpoint),
                cert=(self.ssl_cert, self.ssl_key),
                timeout=conf.net_timeout,
            )
        except requests.exceptions.RequestException as e:
            msg = "Pulp connection has failed: {}".format(e.args)
            raise requests.exceptions.RequestException(msg)

        r.raise_for_status()
        return r.json()

    def _make_repo_info(self, raw_repo):
        """
        Convert the raw repo info returned from Pulp to a simple repo object
        for further handling

        :param dict raw_repo: the repo info returned from Pulp API endpoint.
        :return: a simple repo info used internally for further handling.
        :rtype: dict
        """
        notes = raw_repo["notes"]
        url = self.server_url.rstrip("/") + "/" + notes["relative_url"]
        return {
            "id": raw_repo["id"],
            "url": url,
            "arches": {notes["arch"]},
            "sigkeys": sorted(notes["signatures"].split(",")),
            "product_versions": notes["product_versions"],
        }

    def get_repos_from_content_sets(
        self, content_sets, include_unpublished_repos=False
    ):
        """
        Returns dictionary with URLs of all shipped repositories defined by
        the content_sets.
        The key in the returned dict is the content_set name and the value
        is the URL to repository with RPMs.

        :param list[str] content_sets: Content sets to look for.
        :param bool include_unpublished_repos: set True to include unpublished repositories.
        :rtype: dict
        :return: Dictionary in following format:
            {
                content_set_1: {
                    "url": repo_url,
                    "arches": set([repo_arch1, repo_arch2]),
                    'sigkeys': ['sigkey1', 'sigkey2', ...]
                },
                ...
            }
        """
        query_data = {
            "criteria": {
                "filters": {"notes.content_set": {"$in": content_sets}},
                "fields": ["notes", "id"],
            }
        }

        if not include_unpublished_repos:
            query_data["criteria"]["filters"][
                "notes.include_in_download_service"
            ] = "True"
        repos = self._rest_post("repositories/search/", query_data)

        per_content_set_repos = {}
        for repo in repos:
            content_set = repo["notes"]["content_set"]
            per_content_set_repos.setdefault(content_set, []).append(
                self._make_repo_info(repo)
            )
        return per_content_set_repos

    def get_repos_by_id(self, repo_ids, include_unpublished_repos=False):
        """Get repositories by id

        :param iterable[str] repo_ids: list of repository ids.
        :param bool include_unpublished_repos: whether the unpublished
            repositories are included in the returned result.
        """
        repos = {}
        for repo_id in repo_ids:
            try:
                repo = self._rest_get("repositories/{}/".format(repo_id))
            except requests.exceptions.HTTPError as e:
                if e.response.status_code != 404:
                    raise
                error_message = e.response.json()["error_message"]
                log.warning(
                    "Cannot find repository for id %s. Error message: %s",
                    repo_id,
                    error_message,
                )
                continue
            if (
                repo["notes"]["include_in_download_service"]
                or include_unpublished_repos
            ):
                repos[repo_id] = self._make_repo_info(repo)
        return repos

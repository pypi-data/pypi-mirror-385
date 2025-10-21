===================
Pulp composes
===================

ODCS can generate a "compose" that contains packages from specified Pulp
content set. The result of this request will be a .repo file and a repository
with RPMs.

This document describes how to configure ODCS server to generate
``pulp`` composes.


High level overview
===================

When requesting a Pulp compose, ODCS client will submit a list of content sets
to the server.

Each content set in Pulp corresponds to at least one repository (identified by
a repo ID). The packages in these repositories are merged into a single repo.

If Pulp returns multiple repos for a given content set, and all of them have a
single product version each, and the product version follows the same schema
for all repos, the resulting compose will only contain the repository with the
highest version.

If the above optimization can not trigger, ODCS will run ``mergerepo_c`` and
produce a single repository metadata with all of the packages.


Using explicit repository IDs
=============================

Instead of content set names, the input can specify explicit repo IDs. In that
case the URLs of those repositories will be included in the resulting file.

If you combine content sets and repo IDs in the same request, the content sets
will still be processed as above. Then the explicitly provided repos will be
added to the final repo file.

The general advice is to not combine content sets and repository IDs in the
same request.


Flags
=====

Pulp composes accept a number of flags:

* ``include_unpublished_pulp_repos`` – Include also unpublished repositories
  included in the given content sets.
* ``ignore_absent_pulp_repos`` – The default behaviour when an argument can not
  be resolved as either a content set or a repo ID is to fail and return an
  error message. When this flag is specified, such error is ignored. As a user
  you can detect this by checking if the ``source`` attribute of your compose
  matches the request. Any non-existing sources will be removed.
* ``use_only_compatible_arch`` – When this flag is set, architecture hardcoded
  in URL returned from Pulp will be replaced with ``$basearch`` variable. The
  repository definition will also define ``skip_if_unavailable = 1``. This could
  be useful when multiple content sets are included in the repofile to
  completly ignore packages from repositories for incompatible architectures.

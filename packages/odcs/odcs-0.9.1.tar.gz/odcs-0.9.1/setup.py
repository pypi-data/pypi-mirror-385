from setuptools import setup
import os
import sys


def running_under_virtualenv():
    if hasattr(sys, "real_prefix"):
        return True
    elif sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        return True
    if os.getenv("VIRTUAL_ENV", False):
        return True
    if "--user" in sys.argv:
        return True
    return False


VIRTUAL_ENV = running_under_virtualenv()


def get_dir(system_path=None, virtual_path=None):
    """
    Retrieve VIRTUAL_ENV friendly path
    :param system_path: Relative system path
    :param virtual_path: Overrides system_path for virtual_env only
    :return: VIRTUAL_ENV friendly path
    """
    if virtual_path is None:
        virtual_path = system_path
    if VIRTUAL_ENV:
        if virtual_path is None:
            virtual_path = []
        return os.path.join(*virtual_path)
    else:
        if system_path is None:
            system_path = []
        return os.path.join(*(["/"] + system_path))


extras_require = {}
for package in ["client", "server"]:
    with open(os.path.join(package, "requirements.txt")) as f:
        extras_require[package] = f.readlines()

extras_require["all"] = list(
    set(
        requirement
        for requirements in extras_require.values()
        for requirement in requirements
    )
)

with open("test-requirements.txt") as f:
    test_requirements = f.readlines()

with open("README.md") as f:
    long_description = f.read()

setup(
    name="odcs",
    description="On Demand Compose Service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.9.1",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords="on demand compose service modularity fedora",
    author="The Compose Team",
    # TODO: Not sure which name would be used for mail alias,
    # but let's set this proactively to the new name.
    author_email="odcs-owner@fedoraproject.org",
    url="https://pagure.io/odcs/",
    license="MIT",
    packages=["odcs", "odcs.client", "odcs.server", "odcs.common"],
    package_dir={
        "odcs": "common/odcs",
        "odcs.client": "client/odcs/client",
        "odcs.server": "server/odcs/server",
        "odcs.common": "common/odcs/common",
    },
    extras_require=extras_require,
    include_package_data=True,
    zip_safe=False,
    tests_require=test_requirements,
    scripts=["server/contrib/odcs-promote-compose"],
    entry_points={
        "console_scripts": [
            "odcs = odcs.client.cli:main [client]",
            "odcs-frontend = odcs.server.manage:runssl [server]",
            "odcs-mock-runroot = odcs.server.mock_runroot:mock_runroot_main [server]",
            "odcs-manager = odcs.server.manage:cli [server]",
            "odcs-credential-helper = odcs.server.credential_helper:main [server]",
        ],
    },
    data_files=[
        (
            get_dir(["etc", "odcs"]),
            [
                "server/conf/config.py",
                "server/conf/pungi.conf",
                "server/conf/raw_config_urls.conf",
                "server/conf/raw_config_wrapper.conf",
            ],
        ),
    ],
)

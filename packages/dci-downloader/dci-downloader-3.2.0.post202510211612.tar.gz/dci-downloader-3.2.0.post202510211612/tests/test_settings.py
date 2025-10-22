import os
import mock
import pytest

from dci_downloader.settings import (
    _read_settings_files,
    _variants_are_invalid,
    exit_if_settings_invalid,
    exit_if_env_variables_invalid,
    get_settings,
)


def test_read_settings_file_v1a():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1a.yml")
    settings = _read_settings_files([settings_file_path])
    assert settings == {"topic": "RHEL-7"}


def test_override_settings_file_v1a():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_files_paths = [os.path.join(test_dir, "data", "settings_v1a.yml")]
    settings_files_paths.append(os.path.join(test_dir, "data", "override_v1a.yml"))
    settings = _read_settings_files(settings_files_paths)
    assert settings == {"topic": "RHEL-override"}


def test_read_settings_file_v1b():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1b.yml")
    settings = _read_settings_files([settings_file_path])
    assert settings == {
        "archs": ["x86_64", "ppc64le"],
        "dci_rhel_agent_cert": False,
        "local_repo_ip": "192.168.1.1",
        "systems": ["dci-client"],
        "topic": "RHEL-8.1",
        "variants": ["AppStream", "BaseOS"],
        "with_debug": False,
        "with_iso": False,
    }


def test_override_settings_file_v1b():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_files_paths = [os.path.join(test_dir, "data", "settings_v1b.yml")]
    settings_files_paths.append(os.path.join(test_dir, "data", "override_v1b.yml"))
    settings = _read_settings_files(settings_files_paths)
    assert settings == {
        "archs": ["x86_64", "ppc64le"],
        "dci_rhel_agent_cert": False,
        "local_repo_ip": "192.168.1.1",
        "systems": ["dci-client"],
        "topic": "RHEL-override",
        "variants": ["AppStream", "BaseOS"],
        "with_debug": False,
        "with_iso": True,
    }


def test_read_settings_file_v1c():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1c.yml")
    settings = _read_settings_files([settings_file_path])
    assert settings == {
        "download_folder": "/tmp/repo10",
        "jobs": [
            {
                "topic": "RHEL-7.6",
                "archs": ["x86_64", "ppc64le"],
                "variants": ["Server", "Server-SAP"],
                "filters": [
                    {"type": "component_type1", "tag": "tag1"},
                    {"type": "component_type2", "tag": "tag2"},
                ],
                "tests": ["rhcert", "hardware_cert"],
                "systems": ["SUT1", "SUT2", "SUT3"],
            },
            {
                "topic": "RHEL-8.1",
                "archs": ["x86_64"],
                "variants": [
                    "AppStream",
                    {
                        "name": "BaseOS",
                        "with_debug": True,
                        "with_source": True,
                        "with_iso": False,
                    },
                ],
                "systems": ["SUT4"],
            },
        ],
    }


def test_override_settings_file_v1c():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_files_paths = [os.path.join(test_dir, "data", "settings_v1c.yml")]
    settings_files_paths.append(os.path.join(test_dir, "data", "override_v1c.yml"))
    settings = _read_settings_files(settings_files_paths)
    assert settings == {
        "download_folder": "/tmp/override",
        "jobs": [
            {
                "topic": "RHEL-8.2",
                "archs": ["x86_64", "aarch64"],
                "variants": [
                    "AppStream",
                    {"name": "BaseOS", "with_debug": True, "with_iso": True},
                ],
                "systems": ["SUT4"],
            },
        ],
    }


def test_get_settings_read_arguments():
    settings = get_settings(
        sys_args=["RHEL-8", "/tmp/repo2", "--arch", "ppc64le", "--variant", "BaseOS"],
        env_variables={"DCI_CLIENT_ID": "", "DCI_API_SECRET": "", "DCI_CS_URL": ""},
    )
    assert settings[0] == {
        "variants": [
            {
                "name": "BaseOS",
                "with_debug": False,
                "with_source": False,
                "with_iso": False,
            }
        ],
        "download_everything": False,
        "download_folder": "/tmp/repo2",
        "repo_url": "https://repo.distributed-ci.io",
        "archs": ["ppc64le"],
        "component_id": None,
        "remoteci_id": None,
        "client_id": "",
        "api_secret": "",
        "cs_url": "",
        "components": [],
        "name": "RHEL-8",
        "with_debug": False,
        "with_source": False,
        "registry": None,
        "filters": [],
        "package_filters": [],
    }


def test_get_settings_read_arguments_with_component_id():
    settings = get_settings(
        sys_args=["RHEL-8", "/tmp/repo12", "--component-id", "c1"],
        env_variables={"DCI_CLIENT_ID": "", "DCI_API_SECRET": "", "DCI_CS_URL": ""},
    )
    assert settings[0]["component_id"] == "c1"


def test_get_settings_read_arguments_download_everything():
    settings = get_settings(
        sys_args=["RHEL-8", "/tmp/repo3", "--all"],
        env_variables={"DCI_CLIENT_ID": "", "DCI_API_SECRET": "", "DCI_CS_URL": ""},
    )
    assert settings[0] == {
        "variants": [],
        "download_everything": True,
        "download_folder": "/tmp/repo3",
        "repo_url": "https://repo.distributed-ci.io",
        "archs": ["x86_64"],
        "component_id": None,
        "remoteci_id": None,
        "client_id": "",
        "api_secret": "",
        "cs_url": "",
        "components": [],
        "name": "RHEL-8",
        "with_debug": False,
        "with_source": False,
        "registry": None,
        "filters": [],
        "package_filters": [],
    }


def test_get_settings_from_dci_rhel_agent_settings_file_with_only_topic_key():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1a.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path],
        env_variables={
            "DCI_CLIENT_ID": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
            "DCI_API_SECRET": "",
            "DCI_CS_URL": "",
            "DCI_LOCAL_REPO": "/tmp/repo4",
        },
    )
    assert settings == [
        {
            "variants": [],
            "download_everything": False,
            "download_folder": "/tmp/repo4",
            "repo_url": "https://repo.distributed-ci.io",
            "archs": ["x86_64"],
            "component_id": None,
            "remoteci_id": "9dd94b70-1707-46c5-a2bb-661e8d5d4212",
            "client_id": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
            "api_secret": "",
            "cs_url": "",
            "components": [],
            "name": "RHEL-7",
            "with_debug": False,
            "with_source": False,
            "registry": None,
            "filters": [],
            "package_filters": [],
        }
    ]


def test_get_settings_from_first_dci_rhel_agent_settings_file():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1b.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path],
        env_variables={
            "DCI_CLIENT_ID": "remoteci/66194b70-46c5-1707-a2bb-9dde8d5d4212",
            "DCI_API_SECRET": "",
            "DCI_CS_URL": "",
            "DCI_LOCAL_REPO": "/tmp/repo5",
        },
    )

    assert settings == [
        {
            "variants": [
                {
                    "name": "AppStream",
                    "with_debug": False,
                    "with_source": False,
                    "with_iso": False,
                },
                {
                    "name": "BaseOS",
                    "with_debug": False,
                    "with_source": False,
                    "with_iso": False,
                },
            ],
            "download_everything": False,
            "download_folder": "/tmp/repo5",
            "repo_url": "https://repo.distributed-ci.io",
            "archs": ["x86_64", "ppc64le"],
            "component_id": None,
            "remoteci_id": "66194b70-46c5-1707-a2bb-9dde8d5d4212",
            "client_id": "remoteci/66194b70-46c5-1707-a2bb-9dde8d5d4212",
            "api_secret": "",
            "cs_url": "",
            "components": [],
            "name": "RHEL-8.1",
            "with_debug": False,
            "with_source": False,
            "registry": None,
            "filters": [],
            "package_filters": [],
        }
    ]


def test_should_not_raise_an_exception_settings_are_valid():
    try:
        exit_if_settings_invalid(
            get_settings(
                sys_args=["RHEL-8", "/tmp/repo7", "--variant", "BaseOS"],
                env_variables={
                    "DCI_CLIENT_ID": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
                    "DCI_API_SECRET": "jSbJwfCdIfq12gwHAAtg5JXSBTO3wj0xkG7oW3DlqyM7bXahPRrfZlqmSv3BhmAy",
                    "DCI_CS_URL": "https://distributed-ci.io",
                },
            )
        )
    except SystemExit:
        pytest.fail("exit_if_settings_invalid raise SystemExit but should not")


def test_exit_if_env_variables_invalid_with_empty_env_variables():
    with pytest.raises(SystemExit):
        exit_if_env_variables_invalid(
            get_settings(sys_args=["RHEL-8", "/tmp/repo8"], env_variables={})
        )


def test_exit_if_settings_invalid_without_download_folder():
    with pytest.raises(SystemExit):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        settings_file_path = os.path.join(test_dir, "data", "settings_v1b.yml")
        exit_if_settings_invalid(
            get_settings(
                sys_args=["--settings", settings_file_path],
                env_variables={
                    "DCI_CLIENT_ID": "remoteci/66194b70-46c5-1707-a2bb-9dde8d5d4212",
                    "DCI_API_SECRET": "",
                    "DCI_CS_URL": "",
                },
            )
        )


def test_exit_if_settings_invalid_with_bad_variants():
    with pytest.raises(SystemExit):
        exit_if_settings_invalid(
            get_settings(
                sys_args=[
                    "RHEL-8",
                    "/tmp/repo9",
                    "--variant",
                    "AppStream",
                    "--variant",
                    "Server",
                ],
                env_variables={
                    "DCI_CLIENT_ID": "",
                    "DCI_API_SECRET": "",
                    "DCI_CS_URL": "",
                },
            )
        )


def test_get_settings_with_jobs_key():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1c.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path],
        env_variables={"DCI_CLIENT_ID": "", "DCI_API_SECRET": "", "DCI_CS_URL": ""},
    )
    assert settings == [
        {
            "name": "RHEL-7.6",
            "components": [],
            "archs": ["x86_64", "ppc64le"],
            "variants": [
                {
                    "name": "Server",
                    "with_debug": False,
                    "with_source": False,
                    "with_iso": False,
                },
                {
                    "name": "Server-SAP",
                    "with_debug": False,
                    "with_source": False,
                    "with_iso": False,
                },
            ],
            "download_everything": False,
            "download_folder": "/tmp/repo10",
            "repo_url": "https://repo.distributed-ci.io",
            "registry": None,
            "component_id": None,
            "remoteci_id": None,
            "client_id": "",
            "api_secret": "",
            "cs_url": "",
            "with_debug": False,
            "with_source": False,
            "filters": [
                {"type": "component_type1", "tag": "tag1"},
                {"type": "component_type2", "tag": "tag2"},
            ],
            "package_filters": [],
        },
        {
            "name": "RHEL-8.1",
            "components": [],
            "archs": ["x86_64"],
            "variants": [
                {
                    "name": "AppStream",
                    "with_debug": False,
                    "with_source": False,
                    "with_iso": False,
                },
                {
                    "name": "BaseOS",
                    "with_debug": True,
                    "with_source": True,
                    "with_iso": False,
                },
            ],
            "download_everything": False,
            "download_folder": "/tmp/repo10",
            "repo_url": "https://repo.distributed-ci.io",
            "registry": None,
            "component_id": None,
            "remoteci_id": None,
            "client_id": "",
            "api_secret": "",
            "cs_url": "",
            "with_debug": False,
            "with_source": False,
            "filters": [],
            "package_filters": [],
        },
    ]


def test_get_settings_local_repo_added_to_an_old_settings_file():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1d.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path],
        env_variables={
            "DCI_CLIENT_ID": "",
            "DCI_API_SECRET": "",
            "DCI_CS_URL": "",
            "DCI_LOCAL_REPO": "/tmp/repo4",
        },
    )
    assert settings[0] == {
        "variants": [
            {
                "name": "AppStream",
                "with_debug": False,
                "with_source": False,
                "with_iso": False,
            },
            {
                "name": "BaseOS",
                "with_debug": False,
                "with_source": False,
                "with_iso": False,
            },
        ],
        "download_everything": False,
        "download_folder": "/tmp/repo4",
        "repo_url": "https://repo.distributed-ci.io",
        "archs": ["x86_64", "ppc64le"],
        "component_id": None,
        "remoteci_id": None,
        "client_id": "",
        "api_secret": "",
        "cs_url": "",
        "components": [],
        "name": "RHEL-8.2",
        "with_debug": False,
        "with_source": False,
        "registry": None,
        "filters": [],
        "package_filters": [],
    }


def test_get_settings_local_repo_with_multiple_topics():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1e.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path],
        env_variables={"DCI_CLIENT_ID": "", "DCI_API_SECRET": "", "DCI_CS_URL": ""},
    )
    assert settings[0] == {
        "variants": [],
        "download_everything": False,
        "download_folder": "/tmp/repo6",
        "repo_url": "https://repo.distributed-ci.io",
        "archs": ["x86_64"],
        "component_id": None,
        "remoteci_id": None,
        "client_id": "",
        "api_secret": "",
        "cs_url": "",
        "components": [],
        "name": "RHEL-7.6",
        "with_debug": False,
        "with_source": False,
        "registry": None,
        "filters": [],
        "package_filters": [],
    }
    assert settings[1] == {
        "variants": [],
        "download_everything": False,
        "download_folder": "/tmp/repo6",
        "repo_url": "https://repo.distributed-ci.io",
        "archs": ["x86_64"],
        "component_id": None,
        "remoteci_id": None,
        "client_id": "",
        "api_secret": "",
        "cs_url": "",
        "components": [],
        "name": "RHEL-8.1",
        "with_debug": False,
        "with_source": False,
        "registry": None,
        "filters": [],
        "package_filters": [],
    }


def test_backward_compatibility_test_variants_are_invalid_with_metadata():
    assert (
        _variants_are_invalid({"name": "RHEL-7", "variants": [{"name": "metadata"}]})
        is False
    )
    assert (
        _variants_are_invalid({"name": "RHEL-8", "variants": [{"name": "metadata"}]})
        is False
    )


def test_get_settings_with_debug_without_a_variant():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1g.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path],
        env_variables={"DCI_CLIENT_ID": "", "DCI_API_SECRET": "", "DCI_CS_URL": ""},
    )
    assert settings[0] == {
        "variants": [],
        "download_everything": False,
        "download_folder": "/var/www/html",
        "repo_url": "https://repo.distributed-ci.io",
        "archs": ["ppc64le"],
        "component_id": None,
        "remoteci_id": None,
        "client_id": "",
        "api_secret": "",
        "cs_url": "",
        "components": [],
        "name": "RHEL-8.2-milestone",
        "with_debug": True,
        "with_source": False,
        "registry": None,
        "filters": [],
        "package_filters": [],
    }


def test_get_settings_with_debug_with_variants():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1h.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path],
        env_variables={"DCI_CLIENT_ID": "", "DCI_API_SECRET": "", "DCI_CS_URL": ""},
    )
    assert settings[0] == {
        "variants": [
            {
                "name": "AppStream",
                "with_debug": True,
                "with_source": True,
                "with_iso": False,
            },
            {
                "name": "BaseOS",
                "with_debug": True,
                "with_source": True,
                "with_iso": False,
            },
        ],
        "download_everything": False,
        "download_folder": "/var/www/html",
        "repo_url": "https://repo.distributed-ci.io",
        "archs": ["x86_64"],
        "component_id": None,
        "remoteci_id": None,
        "client_id": "",
        "api_secret": "",
        "cs_url": "",
        "components": [],
        "name": "RHEL-8.5",
        "with_debug": True,
        "with_source": True,
        "registry": None,
        "filters": [],
        "package_filters": [],
    }


def test_nrt_get_settings_with_debug_in_the_cli_overwriting_settings():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1l.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path, "--debug"],
        env_variables={"DCI_CLIENT_ID": "", "DCI_API_SECRET": "", "DCI_CS_URL": ""},
    )
    assert settings[0] == {
        "variants": [
            {
                "name": "AppStream",
                "with_debug": True,
                "with_source": False,
                "with_iso": False,
            },
            {
                "name": "BaseOS",
                "with_debug": True,
                "with_source": False,
                "with_iso": False,
            },
        ],
        "download_everything": False,
        "download_folder": "/var/www/html",
        "repo_url": "https://repo.distributed-ci.io",
        "archs": ["x86_64"],
        "component_id": None,
        "remoteci_id": None,
        "client_id": "",
        "api_secret": "",
        "cs_url": "",
        "components": [],
        "name": "RHEL-8.5",
        "with_debug": True,
        "with_source": False,
        "registry": None,
        "filters": [],
        "package_filters": [],
    }


def test_exit_if_architecture_in_settings_invalid():
    with pytest.raises(SystemExit):
        exit_if_settings_invalid(
            get_settings(
                sys_args=["RHEL-8", "/tmp/repo7", "--arch", "x86"],
                env_variables={
                    "DCI_CLIENT_ID": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
                    "DCI_API_SECRET": "jSbJwfCdIfq12gwHAAtg5JXSBTO3wj0xkG7oW3DlqyM7bXahPRrfZlqmSv3BhmAy",
                    "DCI_CS_URL": "https://distributed-ci.io",
                },
            )
        )


def test_exit_if_architecture_in_settings_invalid_for_rhel_7():
    with pytest.raises(SystemExit):
        exit_if_settings_invalid(
            get_settings(
                sys_args=["RHEL-7", "/tmp/repo7", "--arch", "aarch64"],
                env_variables={
                    "DCI_CLIENT_ID": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
                    "DCI_API_SECRET": "jSbJwfCdIfq12gwHAAtg5JXSBTO3wj0xkG7oW3DlqyM7bXahPRrfZlqmSv3BhmAy",
                    "DCI_CS_URL": "https://distributed-ci.io",
                },
            )
        )


@mock.patch("dci_downloader.settings.has_command")
def test_exit_if_registry_and_no_skopeo(has_command_mock):
    has_command_mock.return_value = False
    with pytest.raises(SystemExit):
        exit_if_settings_invalid(
            get_settings(
                sys_args=[
                    "OSP16.2",
                    "/tmp/repoOSP16.2",
                    "--registry",
                    "localhost:5000",
                ],
                env_variables={
                    "DCI_CLIENT_ID": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
                    "DCI_API_SECRET": "jSbJwfCdIfq12gwHAAtg5JXSBTO3wj0xkG7oW3DlqyM7bXahPRrfZlqmSv3BhmAy",
                    "DCI_CS_URL": "https://distributed-ci.io",
                },
            )
        )


@mock.patch("dci_downloader.settings.has_command")
def test_with_registry_and_skopeo(has_command_mock):
    has_command_mock.return_value = True
    exit_if_settings_invalid(
        get_settings(
            sys_args=["OSP16.2", "/tmp/repoOSP16.2", "--registry", "localhost:5000"],
            env_variables={
                "DCI_CLIENT_ID": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
                "DCI_API_SECRET": "jSbJwfCdIfq12gwHAAtg5JXSBTO3wj0xkG7oW3DlqyM7bXahPRrfZlqmSv3BhmAy",
                "DCI_CS_URL": "https://distributed-ci.io",
            },
        )
    )


def test_with_registry():
    settings = get_settings(
        sys_args=["RHEL-8", "/tmp/repo1", "--registry", "host:port"],
        env_variables={
            "DCI_CLIENT_ID": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
            "DCI_API_SECRET": "",
            "DCI_CS_URL": "",
            "XDG_DATA_HOME": "/home/dci/.local/share",
        },
    )
    topic = settings[0]
    assert topic["registry"] == "host:port"


def test_get_settings_v2():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v2.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path],
        env_variables={
            "DCI_CLIENT_ID": "",
            "DCI_API_SECRET": "",
            "DCI_CS_URL": "",
            "DCI_REPO_URL": "https://repo2.distributed-ci.io/",
        },
    )

    assert settings == [
        {
            "registry": None,
            "components": [],
            "variants": [],
            "name": "RHEL-8.2",
            "archs": ["x86_64"],
            "download_everything": False,
            "with_debug": False,
            "with_source": False,
            "download_folder": "/var/www/html",
            "repo_url": "https://repo2.distributed-ci.io",
            "component_id": None,
            "remoteci_id": None,
            "client_id": "",
            "api_secret": "",
            "cs_url": "",
            "filters": [],
            "package_filters": [],
        },
        {
            "registry": None,
            "components": [],
            "variants": [
                {
                    "name": "AppStream",
                    "with_iso": False,
                    "with_source": False,
                    "with_debug": False,
                },
                {"name": "BaseOS", "with_debug": True},
            ],
            "name": "RHEL-8.4",
            "archs": ["ppc64le"],
            "download_everything": False,
            "with_debug": False,
            "with_source": False,
            "download_folder": "/var/www/html",
            "repo_url": "https://repo2.distributed-ci.io",
            "component_id": None,
            "remoteci_id": None,
            "client_id": "",
            "api_secret": "",
            "cs_url": "",
            "filters": [
                {"type": "compose", "tag": "milestone"},
            ],
            "package_filters": [],
        },
        {
            "registry": None,
            "components": [],
            "variants": [],
            "name": "RHEL-9.0",
            "archs": ["x86_64"],
            "download_everything": False,
            "with_debug": False,
            "with_source": False,
            "download_folder": "/var/www/html",
            "repo_url": "https://repo2.distributed-ci.io",
            "component_id": None,
            "remoteci_id": None,
            "client_id": "",
            "api_secret": "",
            "cs_url": "",
            "filters": [
                {"type": "compose", "tag": "nightly"},
                {"type": "compose-noinstall"},
            ],
            "package_filters": [],
        },
    ]


def test_order_command_line_parameter_overwrite_env_variable():
    settings = get_settings(
        sys_args=["RHEL-9", "/var/www/html"],
        env_variables={
            "DCI_CLIENT_ID": "",
            "DCI_API_SECRET": "",
            "DCI_CS_URL": "",
            "DCI_LOCAL_REPO": "/tmp/repo",
        },
    )
    assert settings[0]["download_folder"] == "/var/www/html"


def test_env_variable_overwrite_settings_file():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v2.yml")
    settings = get_settings(
        sys_args=["--settings", settings_file_path],
        env_variables={
            "DCI_CLIENT_ID": "",
            "DCI_API_SECRET": "",
            "DCI_CS_URL": "",
            "DCI_LOCAL_REPO": "/tmp/repo",
        },
    )
    assert settings[0]["download_folder"] == "/tmp/repo"


def test_topic_in_cli_append_topics_array():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v2.yml")
    settings = get_settings(
        sys_args=["RHEL-8.5", "/var/www/html", "--settings", settings_file_path],
        env_variables={
            "DCI_CLIENT_ID": "",
            "DCI_API_SECRET": "",
            "DCI_CS_URL": "",
            "DCI_LOCAL_REPO": "/tmp/repo",
        },
    )
    assert len(settings) == 4


def test_local_repo_overwrite_local_repo_in_settings():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file_path = os.path.join(test_dir, "data", "settings_v1d.yml")
    settings = get_settings(
        sys_args=["--local-repo", "/tmp/notinv1d", "--settings", settings_file_path],
        env_variables={"DCI_CLIENT_ID": "", "DCI_API_SECRET": "", "DCI_CS_URL": ""},
    )
    assert settings[0]["download_folder"] == "/tmp/notinv1d"


def test_read_client_id_and_api_secret():
    settings = get_settings(
        sys_args=["RHEL-8.7", "/tmp/repo"],
        env_variables={
            "DCI_CLIENT_ID": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
            "DCI_API_SECRET": "jSbJwfCdIfq12gwHAAtg5JXSBTO3wj0xkG7oW3DlqyM7bXahPRrfZlqmSv3BhmAy",
            "DCI_CS_URL": "https://api.distributed-ci.io",
        },
    )
    assert settings[0]["client_id"] == "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212"
    assert (
        settings[0]["api_secret"]
        == "jSbJwfCdIfq12gwHAAtg5JXSBTO3wj0xkG7oW3DlqyM7bXahPRrfZlqmSv3BhmAy"
    )
    assert settings[0]["cs_url"] == "https://api.distributed-ci.io"

    settings = get_settings(
        sys_args=["RHEL-8.7", "/tmp/repo", "--dci-cs-url", "http://localhost:5000/"],
        env_variables={
            "DCI_CLIENT_ID": "remoteci/9dd94b70-1707-46c5-a2bb-661e8d5d4212",
            "DCI_API_SECRET": "jSbJwfCdIfq12gwHAAtg5JXSBTO3wj0xkG7oW3DlqyM7bXahPRrfZlqmSv3BhmAy",
            "DCI_CS_URL": "https://api.distributed-ci.io",
        },
    )
    assert settings[0]["cs_url"] == "http://localhost:5000"

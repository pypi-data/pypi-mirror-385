from dci_downloader.cli import parse_arguments


def test_parsing_no_options():
    args = parse_arguments(["RHEL-8", "/var/www/html"])
    assert args["name"] == "RHEL-8"
    assert args["archs"] == ["x86_64"]
    assert args["variants"] == []
    assert not args["with_debug"]
    assert not args["with_source"]
    assert not args["with_iso"]
    assert args["settings_files_paths"] == []
    assert args["download_folder"] == "/var/www/html"


def test_parsing_settings_file():
    args = parse_arguments(["--settings", "/etc/dci-downloader/settings.yml"])
    assert args["name"] is None
    assert args["archs"] == ["x86_64"]
    assert args["variants"] == []
    assert not args["with_debug"]
    assert not args["with_source"]
    assert not args["with_iso"]
    assert "/etc/dci-downloader/settings.yml" in args["settings_files_paths"]
    assert args["download_folder"] is None


def test_parsing_multiple_settings_file():
    args = parse_arguments(
        [
            "--settings",
            "/etc/dci-downloader/settings.yml",
            "--settings",
            "/etc/dci-downloader/extra.yml",
        ]
    )
    assert args["name"] is None
    assert args["archs"] == ["x86_64"]
    assert args["variants"] == []
    assert not args["with_debug"]
    assert not args["with_source"]
    assert not args["with_iso"]
    # ensure all settings files are present and in the right order
    assert args["settings_files_paths"] == [
        "/etc/dci-downloader/settings.yml",
        "/etc/dci-downloader/extra.yml",
    ]
    assert args["download_folder"] is None


def test_parsing_with_debug():
    args = parse_arguments(["RHEL-8", "/var/www/html", "--debug"])
    assert args["with_debug"]


def test_parsing_with_source():
    args = parse_arguments(["RHEL-8", "/var/www/html", "--src"])
    assert args["with_source"]


def test_parsing_with_iso():
    args = parse_arguments(["RHEL-8", "/var/www/html", "--iso"])
    assert args["with_iso"]


def test_parsing_name():
    args = parse_arguments(["RHEL-7.6", "/var/www/html"])
    assert args["name"] == "RHEL-7.6"


def test_parsing_no_components():
    args = parse_arguments(["RHEL-8", "/var/www/"])
    assert args["component_id"] is None


def test_parsing_component_id():
    args = parse_arguments(
        [
            "RHEL-8",
            "/var/www/html",
            "--component-id",
            "27bbcd7d-021b-4f0a-b04e-e64f1be386f7",
        ]
    )
    assert args["name"] == "RHEL-8"
    assert args["download_folder"] == "/var/www/html"
    assert args["component_id"] == "27bbcd7d-021b-4f0a-b04e-e64f1be386f7"


def test_parsing_1_variant():
    args = parse_arguments(["RHEL-8", "/var/www/html", "--variant", "BaseOS"])
    assert args["variants"] == [
        {
            "name": "BaseOS",
            "with_debug": False,
            "with_source": False,
            "with_iso": False,
        }
    ]


def test_parsing_2_variants():
    args = parse_arguments(
        ["RHEL-8", "/var/www/html", "--variant", "BaseOS", "--variant", "AppStream"]
    )
    assert sorted(args["variants"], key=lambda v: v["name"]) == [
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
    ]


def test_parsing_1_arch():
    args = parse_arguments(["RHEL-8", "/var/www/html", "--arch", "ppc64le"])
    assert args["archs"] == ["ppc64le"]


def test_parsing_2_archs():
    args = parse_arguments(
        ["RHEL-8", "/var/www/html", "--arch", "x86_64", "--arch", "ppc64le"]
    )
    assert sorted(args["archs"]) == ["ppc64le", "x86_64"]


def test_parsing_combined_arguments():
    args = parse_arguments(
        [
            "RHEL-8.1",
            "/var/www/html",
            "--variant",
            "BaseOS",
            "--variant",
            "AppStream",
            "--arch",
            "ppc64le",
        ]
    )
    assert args["name"] == "RHEL-8.1"
    assert args["download_folder"] == "/var/www/html"
    assert args["archs"] == ["ppc64le"]
    assert sorted(args["variants"], key=lambda v: v["name"]) == [
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
    ]
    assert not args["with_debug"]
    assert not args["with_source"]
    assert not args["with_iso"]


def test_parsing_combined_arguments_different_order():
    args = parse_arguments(
        [
            "--variant",
            "BaseOS",
            "--arch",
            "x86_64",
            "--variant",
            "AppStream",
            "RHEL-8.1",
            "/home/dci/repo",
        ]
    )
    assert args["name"] == "RHEL-8.1"
    assert args["download_folder"] == "/home/dci/repo"
    assert args["archs"] == ["x86_64"]
    assert sorted(args["variants"], key=lambda v: v["name"]) == [
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
    ]
    assert not args["with_debug"]
    assert not args["with_source"]
    assert not args["with_iso"]


def test_parsing_combined_arguments_with_equals_signs():
    args = parse_arguments(
        [
            "--variant=BaseOS",
            "--arch=x86_64",
            "--variant=AppStream",
            "RHEL-8",
            "/tmp/repo",
        ]
    )
    assert args["name"] == "RHEL-8"
    assert args["download_folder"] == "/tmp/repo"
    assert args["archs"] == ["x86_64"]
    assert sorted(args["variants"], key=lambda v: v["name"]) == [
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
    ]
    assert not args["with_debug"]
    assert not args["with_source"]
    assert not args["with_iso"]


def test_parsing_variants_with_debug():
    args = parse_arguments(
        [
            "--variant=BaseOS",
            "--arch=x86_64",
            "--variant=AppStream",
            "--debug",
            "RHEL-8",
            "/tmp/repo",
        ]
    )
    assert args["name"] == "RHEL-8"
    assert args["download_folder"] == "/tmp/repo"
    assert args["archs"] == ["x86_64"]
    assert sorted(args["variants"], key=lambda v: v["name"]) == [
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
    ]
    assert args["with_debug"]


def test_parsing_variants_with_iso():
    args = parse_arguments(
        [
            "--variant=BaseOS",
            "--arch=x86_64",
            "--variant=AppStream",
            "--iso",
            "RHEL-8",
            "/tmp/repo",
        ]
    )
    assert args["name"] == "RHEL-8"
    assert args["download_folder"] == "/tmp/repo"
    assert args["archs"] == ["x86_64"]
    assert sorted(args["variants"], key=lambda v: v["name"]) == [
        {
            "name": "AppStream",
            "with_debug": False,
            "with_source": False,
            "with_iso": True,
        },
        {"name": "BaseOS", "with_debug": False, "with_source": False, "with_iso": True},
    ]
    assert args["with_iso"]


def test_parsing_filters():
    args = parse_arguments(
        [
            "--filter=compose:nightly",
            "RHEL-8",
            "/tmp/repo",
        ]
    )
    assert args["name"] == "RHEL-8"
    assert args["download_folder"] == "/tmp/repo"
    assert args["archs"] == ["x86_64"]
    assert args["filters"] == [{"type": "compose", "tag": "nightly"}]


def test_parsing_filters_change_type_to_lower_case():
    args = parse_arguments(
        [
            "--filter=coMpose:Nightly",
            "RHEL-8",
            "/tmp/repo",
        ]
    )
    assert args["name"] == "RHEL-8"
    assert args["download_folder"] == "/tmp/repo"
    assert args["archs"] == ["x86_64"]
    assert args["filters"] == [{"type": "compose", "tag": "Nightly"}]


def test_parsing_filters_without_a_tag():
    args = parse_arguments(
        [
            "--filter=compose-noinstall",
            "RHEL-8",
            "/tmp/repo",
        ]
    )
    assert args["name"] == "RHEL-8"
    assert args["download_folder"] == "/tmp/repo"
    assert args["archs"] == ["x86_64"]
    assert args["filters"] == [{"type": "compose-noinstall", "tag": None}]


def test_parsing_registry():
    args = parse_arguments(
        [
            "OSP16.1",
            "/tmp/repo",
            "--registry",
            "localhost:5000",
        ]
    )
    assert args["registry"] == "localhost:5000"


def test_parsing_repo():
    args = parse_arguments(
        [
            "OSP16.1",
            "/tmp/repo",
            "--dci-repo-url",
            "https://repo2.distributed-ci.io/",
        ]
    )
    assert args["repo_url"] == "https://repo2.distributed-ci.io/"


def test_parsing_cs_url():
    args = parse_arguments(
        [
            "OSP16.1",
            "/tmp/repo",
            "--dci-cs-url",
            "https://example.org",
        ]
    )

    assert args["cs_url"] == "https://example.org"


def test_default_cs_url():
    args = parse_arguments(
        [
            "OSP16.1",
            "/tmp/repo",
        ]
    )
    assert args["cs_url"] is None


def test_parsing_local_repo():
    args = parse_arguments(
        ["--settings", "/etc/dci-downloader/settings.yml", "--local-repo", "/tmp/repo"]
    )
    assert args["settings_files_paths"] == ["/etc/dci-downloader/settings.yml"]
    assert args["download_folder"] == "/tmp/repo"


def test_parsing_local_repo_with_positional_arguments():
    args = parse_arguments(["RHEL-9.2", "/tmp/repo", "--local-repo", "/tmp/repo1"])
    assert args["download_folder"] == "/tmp/repo"


def test_package_filter_arg():
    args = parse_arguments(
        ["RHEL-9.2", "/tmp/repo", "--package-filter", "glibc"])
    assert args["package_filters"] == ["glibc"]


def test_multiple_package_filter_args():
    args = parse_arguments(
        ["RHEL-9.2", "/tmp/repo", "--package-filter", "glibc", "--package-filter", "kernel", "--package-filter", "grub"])
    assert args["package_filters"] == ["glibc", "kernel", "grub"]

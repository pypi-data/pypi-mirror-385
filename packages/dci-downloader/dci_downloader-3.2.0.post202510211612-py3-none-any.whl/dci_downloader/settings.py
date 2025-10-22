#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import yaml
import sys

from collections import defaultdict

from dci_downloader.cli import parse_arguments
from dci_downloader.containers import has_command


def _read_settings_files(settings_files_paths=[]):
    settings = {}
    for settings_file_path in settings_files_paths:
        with open(settings_file_path, "r") as stream:
            try:
                settings.update(yaml.safe_load(stream))
            except yaml.YAMLError:
                print("Can't read %s file" % settings_file_path)
                traceback.print_exc()
    return settings


def _clean_topic(topic_info):
    name = topic_info.get("topic", topic_info.get("name"))
    component_id = topic_info.get("component_id")
    components = topic_info.get("components", [])
    archs = topic_info.get("archs", ["x86_64"])
    variants = topic_info.get("variants", [])
    with_debug = topic_info.get("with_debug", False)
    with_source = topic_info.get("with_source", False)
    variants = [
        v
        if type(v) is dict
        else {
            "name": v,
            "with_debug": with_debug,
            "with_source": with_source,
            "with_iso": False,
        }
        for v in variants
    ]
    filters = topic_info.get("filters", [])
    package_filters = topic_info.get("package_filters", [])
    return {
        "name": name,
        "components": components,
        "archs": archs,
        "variants": variants,
        "download_everything": topic_info.get("download_everything", False),
        "download_folder": topic_info["download_folder"],
        "remoteci_id": topic_info["remoteci_id"],
        "repo_url": topic_info["repo_url"].rstrip("/"),
        "cs_url": topic_info["cs_url"].rstrip("/"),
        "client_id": topic_info["client_id"],
        "api_secret": topic_info["api_secret"],
        "registry": topic_info["registry"],
        "component_id": component_id,
        "with_debug": with_debug,
        "with_source": with_source,
        "filters": filters,
        "package_filters": package_filters,
    }


def _clean_settings(settings):
    new_settings = []
    for topic in settings["topics"]:
        topic["download_folder"] = settings["download_folder"]
        topic["remoteci_id"] = settings.get("remoteci_id")
        topic["repo_url"] = settings.get("repo_url", "https://repo.distributed-ci.io")
        topic["cs_url"] = settings.get("cs_url", "https://api.distributed-ci.io")
        topic["client_id"] = settings.get("client_id")
        topic["api_secret"] = settings.get("api_secret")
        topic["registry"] = settings["registry"]
        if settings["with_debug"]:
            topic["with_debug"] = settings["with_debug"]
        if settings["with_source"]:
            topic["with_source"] = settings["with_source"]
        new_settings.append(_clean_topic(topic))
    return sorted(new_settings, key=lambda k: k["name"])


def _keep_backward_compatibility(settings):
    if "local_repo" in settings:
        settings["download_folder"] = settings["local_repo"]
    if "topic" in settings:
        settings["topics"] = [settings.copy()]
    if "jobs" in settings:
        settings["topics"] = settings["jobs"]
    settings["download_folder"] = settings.get("download_folder")
    settings["registry"] = settings.get("registry")
    settings["topics"] = settings.get("topics", [])
    return settings


def _remove_none_values(d):
    return {k: v for k, v in d.items() if v is not None}


def _merge_settings(settings):
    topics_by_name = defaultdict(dict)
    s = {}
    for setting in settings:
        for topic in setting.get("topics", []):
            k = "name" if "name" in topic else "topic"
            topics_by_name[topic[k]].update(topic)
        s.update(setting)
    s["topics"] = list(topics_by_name.values())
    return s


def _get_remoteci_id(env_variables):
    remoteci_id = env_variables.get("DCI_CLIENT_ID")
    if remoteci_id:
        return remoteci_id.split("/")[1]
    return None


def get_settings(sys_args, env_variables={}):
    settings_from_env_variables = {
        "env_variables": env_variables,
        "download_folder": env_variables.get("DCI_LOCAL_REPO"),
        "registry": env_variables.get("DCI_REGISTRY"),
        "remoteci_id": _get_remoteci_id(env_variables),
        "repo_url": env_variables.get("DCI_REPO_URL"),
        "client_id": env_variables.get("DCI_CLIENT_ID"),
        "api_secret": env_variables.get("DCI_API_SECRET"),
        "cs_url": env_variables.get("DCI_CS_URL"),
    }

    cli_arguments = parse_arguments(sys_args)
    settings_from_cli = {
        "download_folder": cli_arguments["download_folder"],
        "registry": cli_arguments["registry"],
        "repo_url": cli_arguments["repo_url"],
        "cs_url": cli_arguments["cs_url"],
        "topics": [],
        "with_debug": cli_arguments["with_debug"],
        "with_source": cli_arguments["with_source"],
    }
    topic_name = cli_arguments["name"]
    if topic_name:
        settings_from_cli["topics"].append(
            {
                "download_everything": cli_arguments["download_everything"],
                "variants": cli_arguments["variants"],
                "with_debug": cli_arguments["with_debug"],
                "with_source": cli_arguments["with_source"],
                "name": topic_name,
                "with_iso": cli_arguments["with_iso"],
                "archs": cli_arguments["archs"],
                "filters": cli_arguments["filters"],
                "component_id": cli_arguments["component_id"],
                "package_filters": cli_arguments["package_filters"],
            }
        )

    settings_from_files = {"download_folder": None, "registry": None, "topics": []}
    settings_files_paths = cli_arguments["settings_files_paths"]
    if settings_files_paths:
        settings_from_files.update(
            _keep_backward_compatibility(_read_settings_files(settings_files_paths))
        )
    settings = _merge_settings(
        [
            settings_from_files,
            _remove_none_values(settings_from_env_variables),
            _remove_none_values(settings_from_cli),
        ]
    )
    return _clean_settings(settings)


def _variants_are_invalid(topic):
    topic_variants = {
        "RHEL-7": [
            "Client-optional",
            "Client",
            "ComputeNode-optional",
            "ComputeNode",
            "Server-NFV",
            "Server-RT",
            "Server-SAP",
            "Server-SAPHANA",
            "Server-optional",
            "Server",
            "Workstation-optional",
            "Workstation",
        ],
        "RHEL-8": [
            "AppStream",
            "BaseOS",
            "CRB",
            "HighAvailability",
            "NFV",
            "RT",
            "ResilientStorage",
            "SAP",
            "SAPHANA",
        ],
        "RHEL-9": [
            "AppStream",
            "BaseOS",
            "CRB",
            "HighAvailability",
            "NFV",
            "RT",
            "ResilientStorage",
            "SAP",
            "SAPHANA",
        ],
    }
    invalid = False
    for topic_name, variants in topic_variants.items():
        current_topic_name = topic["name"]
        current_variants = [v["name"] for v in topic["variants"]]
        variants_not_allowed = set(current_variants) - set(variants + ["metadata"])
        if current_topic_name.startswith(topic_name) and variants_not_allowed:
            invalid = True
            print(
                "Variants %s for the %s topic are not valid"
                % (", ".join(variants_not_allowed), current_topic_name)
            )
            print(
                "The authorized variants for %s are %s."
                % (current_topic_name, ", ".join(variants))
            )
            break
    return invalid


def _arches_are_invalid(topic):
    topic_archs = {
        "RHEL-7": ["ppc64", "ppc64le", "s390x", "x86_64"],
        "RHEL-8": ["aarch64", "ppc64le", "s390x", "x86_64"],
        "RHEL-9": ["aarch64", "ppc64le", "s390x", "x86_64"],
    }
    invalid = False
    current_topic_name = topic["name"]
    for topic_name, archs in topic_archs.items():
        archs_not_allowed = set(topic["archs"]) - set(archs)
        if current_topic_name.startswith(topic_name) and archs_not_allowed:
            invalid = True
            print(
                "Arches %s for the %s topic are not valid"
                % (", ".join(archs_not_allowed), current_topic_name)
            )
            print(
                "The authorized archs for %s are %s."
                % (current_topic_name, ", ".join(archs))
            )
            break
    return invalid


def exit_if_env_variables_invalid(env_variables):
    has_error = False
    for env_variable in ["DCI_CLIENT_ID", "DCI_API_SECRET", "DCI_CS_URL"]:
        if env_variable not in env_variables:
            has_error = True
            print("Environment variable %s not set" % env_variable)
    if has_error:
        sys.exit(1)


def exit_if_settings_invalid(settings):
    has_error = False

    if not settings:
        has_error = True
        print("You need to specify at least one topic")

    for topic in settings:
        if topic.get("download_folder") is None:
            has_error = True
            print("The destination folder for the download is not specified.")

        if topic.get("registry") and not has_command("skopeo sync --help"):
            has_error = True
            print(
                "You specified a registry to mirror container images "
                "but `skopeo sync [...]` is not available on your system. "
                "Please ensure that skopeo >= 0.1.41 is installed."
            )

        if _variants_are_invalid(topic):
            has_error = True

        if _arches_are_invalid(topic):
            has_error = True

    if has_error:
        sys.exit(1)

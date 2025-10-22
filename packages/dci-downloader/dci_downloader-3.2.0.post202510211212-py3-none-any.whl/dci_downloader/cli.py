#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys

from dci_downloader.version import __version__

EXAMPLES = """
examples:
  # download the latest RHEL-8-milestone compose in /tmp/repo
  dci-downloader RHEL-8-milestone /tmp/repo

  # download specific arch
  dci-downloader RHEL-8-milestone /tmp/repo --arch ppc64le

  # download explicit variants
  dci-downloader RHEL-8-milestone /tmp/repo --variant AppStream --variant BaseOS

  # load options from yaml settings file
  dci-downloader --settings settings.yml

  # load options from several yaml settings file (newer override older)
  dci-downloader --settings settings.yml --settings extra.yml

  # download the latest RHEL-9 development build
  dci-downloader --filter=compose:development RHEL-9.0 /tmp/repo

  # download the latest RHEL-8 kernel packages for x86 and ppc64le architectures
  dci-downloader dci-downloader RHEL-8.8 /tmp --variant BaseOS --arch x86_64 --arch ppc64le --package-filter=kernel
"""

COPYRIGHT = """
copyright:
  Copyright © 2019 Red Hat.
  Licensed under the Apache License, Version 2.0
"""


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(
        usage="dci-downloader TOPIC DEST [OPTIONS]",
        description="Download the latest DCI components easily:\n * source your credentials file\n * specify the topic name and the destination folder",
        epilog=EXAMPLES + COPYRIGHT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "name",
        metavar="TOPIC",
        nargs="?",
        help="topic name (i.e. RHEL-8-nightly, RHEL-8-milestone, RHEL-8.2-milestone, etc...)",
    )
    parser.add_argument(
        "download_folder", metavar="DEST", nargs="?", help="destination folder."
    )
    parser.add_argument(
        "--component-id",
        metavar="COMPONENT_ID",
        dest="component_id",
        help="download a specific component by id",
    )
    parser.add_argument(
        "--arch",
        action="append",
        metavar="ARCH",
        dest="archs",
        default=[],
        help="download a specific architecture (default: x86_64)",
    )
    parser.add_argument(
        "--iso",
        help="download ISO images (default: false)",
        dest="with_iso",
        action="store_true",
    )
    parser.add_argument(
        "--variant",
        action="append",
        metavar="VARIANT",
        dest="variants",
        default=[],
        help="download a specific variant (default: all variants)",
    )
    parser.add_argument(
        "--filter",
        action="append",
        metavar="FILTER",
        dest="filters",
        default=[],
        help="filter components by type and tag. Filter must be with the following format <component_type>:<tag>.",
    )
    parser.add_argument(
        "--debug", help="download debug RPMs", dest="with_debug", action="store_true"
    )
    parser.add_argument(
        "--src", help="download src RPMs", dest="with_source", action="store_true"
    )
    parser.add_argument(
        "--all",
        help="download all archs, all variants with sources and debugs rpms",
        dest="download_everything",
        action="store_true",
    )
    parser.add_argument(
        "--registry",
        help="local registry to mirror container images, this flag implicitly enables the container images mirrorring",
        dest="registry",
        default=None,
    )
    parser.add_argument(
        "--dci-repo-url",
        help="repo url used to download components",
        dest="repo_url",
        default=None,
    )
    parser.add_argument(
        "--dci-cs-url",
        help="control server url used to download components.",
        dest="cs_url",
        default=None,
    )
    parser.add_argument(
        "--local-repo",
        help="destination folder/",
        dest="local_repo",
        default=None,
    )
    parser.add_argument(
        "--settings",
        action="append",
        dest="settings_files_paths",
        metavar="FILE_PATH",
        help="settings file(s) to overwrite cli parameters",
        default=[],
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--package-filter",
        action="append",
        dest="package_filters",
        help="Download only the specified package(s) (e.g. kernel, glibc, etc)",
        default=[]
    )
    parsed_arguments = parser.parse_args(arguments)
    if not parsed_arguments.archs:
        parsed_arguments.archs = ["x86_64"]
    parsed_arguments.archs = list(set(parsed_arguments.archs))

    if parsed_arguments.settings_files_paths is None:
        download_folder = parsed_arguments.download_folder
        if download_folder is None:
            print("download folder is required")
            print("Try 'dci-downloader --help' for more information.")
            sys.exit(2)
        topic_name = parsed_arguments.name
        component_id = parsed_arguments.component_id
        if not topic_name and not component_id:
            print("TOPIC or --component-id is required")
            print("Try 'dci-downloader --help' for more information.")
            sys.exit(2)

    parsed_arguments.variants = [
        {
            "name": v,
            "with_debug": parsed_arguments.with_debug,
            "with_source": parsed_arguments.with_source,
            "with_iso": parsed_arguments.with_iso,
        }
        for v in parsed_arguments.variants
    ]
    filters = []
    for filter in parsed_arguments.filters:
        if ":" in filter:
            elements = filter.split(":", 1)
            filters.append({"type": elements[0].lower(), "tag": elements[1]})
        else:
            filters.append({"type": filter, "tag": None})

    parsed_arguments.filters = filters

    if parsed_arguments.local_repo and parsed_arguments.download_folder is None:
        parsed_arguments.download_folder = parsed_arguments.local_repo

    return vars(parsed_arguments)

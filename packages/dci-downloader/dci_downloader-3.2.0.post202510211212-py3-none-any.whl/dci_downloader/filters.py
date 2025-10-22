#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os


def _get_patterns(filters):
    variants = filters["variants"]
    archs = filters["archs"]
    with_debug = filters["with_debug"]
    with_source = filters["with_source"]
    patterns = []
    patterns.append(re.compile(r"^metadata"))
    if with_source:
        patterns.append(re.compile(r"^(.*)/source/tree"))
    archs = archs if archs else [".*"]
    variants = (
        variants
        if variants
        else [{"name": ".*", "with_iso": False, "with_debug": with_debug}]
    )
    package_filters = filters["package_filters"]
    package_filter_regex = (
        "|".join([".*%s.*" % p for p in package_filters]) if package_filters else ".*"
    )
    for variant in variants:
        variant_name = variant["name"]
        variant_with_debug = variant["with_debug"]
        with_iso = variant["with_iso"]
        iso_os_regex = "os"
        if variant_with_debug:
            iso_os_regex += "|debug"
        if with_iso:
            iso_os_regex += "|iso"
        arch_regex = "|".join(archs)
        regex = r"^(%s)/(%s)/(%s)/(%s)" % (
            variant_name,
            arch_regex,
            iso_os_regex,
            package_filter_regex,
        )
        patterns.append(re.compile(regex))
    return patterns


def _match_pattern(string, patterns):
    match = False
    for pattern in patterns:
        if pattern.match(string):
            match = True
            break
    return match


def filter_files_list(topic_info, files_list):
    if topic_info["download_everything"]:
        return files_list
    new_files_list = {"directories": [], "files": [], "symlinks": []}
    patterns = _get_patterns(topic_info)
    for file in files_list["files"]:
        file_path = file["path"]
        if not file["path"]:
            new_files_list["files"].append(file)
            continue
        if _match_pattern(os.path.join(file_path, file["name"]), patterns):
            new_files_list["files"].append(file)
    return new_files_list

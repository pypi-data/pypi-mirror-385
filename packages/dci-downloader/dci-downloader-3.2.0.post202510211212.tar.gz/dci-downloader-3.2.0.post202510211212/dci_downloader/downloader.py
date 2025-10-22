#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from dci_downloader.api import (
    get_files_list,
    get_and_save_image_list,
    download_files,
    build_s3_context,
)
from dci_downloader.containers import mirror_container_images
from dci_downloader.stats import check_download_folder_size
from dci_downloader.filters import filter_files_list
from dci_downloader.files_list import get_files_to_download, get_files_to_remove
from dci_downloader.fs import (
    mkdir_p,
    delete_all_symlink_in_path,
    recreate_symlinks,
    get_component_folder,
)


def clean_download_folder(files_list, download_folder):
    print("Verifying local mirror, this may take some time")
    if not os.path.isdir(download_folder):
        mkdir_p(download_folder)

    for file in get_files_to_remove(files_list, download_folder):
        print("Remove file %s" % file)
        os.remove(file)

    delete_all_symlink_in_path(download_folder)


def download_component(topic_info, topic, component):
    print("Download component %s" % component["name"])
    context = build_s3_context(
        component_id=component["id"],
        options={
            "cs_url": topic_info["cs_url"],
            "client_id": topic_info["client_id"],
            "api_secret": topic_info["api_secret"],
        },
    )
    files_list = get_files_list(context)
    if component["type"].lower() in ["compose", "compose-noinstall"]:
        files_list = filter_files_list(topic_info, files_list)
    download_folder = get_component_folder(topic_info, topic, component)
    clean_download_folder(files_list, download_folder)
    files_to_download = get_files_to_download(download_folder, files_list)
    check_download_folder_size(files_to_download, download_folder)
    download_files(context, files_to_download["files"])
    recreate_symlinks(files_list["symlinks"], download_folder)
    images_list = get_and_save_image_list(context, download_folder)
    if images_list and topic_info.get("registry", None):
        mirror_container_images(topic_info["registry"], topic, images_list)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import os
import sys
import time

from dci_downloader import api
from dci_downloader import downloader
from dci_downloader.lock import file_lock, LockError
from dci_downloader.fs import get_topic_folder, create_parent_dir
from dci_downloader.settings import (
    get_settings,
    exit_if_settings_invalid,
    exit_if_env_variables_invalid,
)


def download_components(topic_info, topic):
    if "component_id" in topic_info and topic_info["component_id"]:
        component_id = topic_info["component_id"]
        component = api.get_component_by_id(component_id)
        components = [component]
    else:
        filters = topic_info.get("filters", [])
        components = api.get_components(topic, filters)
    if not components:
        print("Nothing to download. Exiting...")
        sys.exit(0)
    for component in components:
        downloader.download_component(topic_info, topic, component)


def download_topic(topic_info):
    not_finished = True
    count = 0
    ten_hours = 10 * 60 * 60
    sleep = 30
    while not_finished and count < (ten_hours / sleep):
        try:
            api.check_api_is_accessible(topic_info)
            topic = api.get_topic(topic_info["name"])
            if topic is None:
                return
            lock_file = os.path.join(get_topic_folder(topic_info, topic), ".lock")
            create_parent_dir(lock_file)
            with file_lock(lock_file):
                download_components(topic_info, topic)
                not_finished = False
        except LockError:
            time.sleep(sleep)
            count += 1


def catch_all_and_print(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyboardInterrupt:
            print("Keyboard interrupt exiting...")
            sys.exit(130)
        except Exception as e:
            print(e)
            sys.exit(1)

    return inner


@catch_all_and_print
def main():
    env_variables = dict(os.environ)
    exit_if_env_variables_invalid(env_variables)
    settings = get_settings(sys_args=sys.argv[1:], env_variables=env_variables)
    exit_if_settings_invalid(settings)
    for topic_info in settings:
        download_topic(topic_info)


if __name__ == "__main__":
    main()

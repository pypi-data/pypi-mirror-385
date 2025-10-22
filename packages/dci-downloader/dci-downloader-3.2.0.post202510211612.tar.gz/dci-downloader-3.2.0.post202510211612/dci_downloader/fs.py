import errno
import os


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        elif exc.errno in [errno.EPERM, errno.EACCES]:
            print("Permission error on %s" % path)
        else:
            raise


def create_parent_dir(path):
    mkdir_p(os.path.dirname(path))


def delete_all_symlink_in_path(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.islink(file_path):
                os.unlink(file_path)
        for dir in dirs:
            folder_path = os.path.join(root, dir)
            if os.path.islink(folder_path):
                os.unlink(folder_path)


def recreate_symlinks(symlinks, destination_path):
    for symlink in symlinks:
        link_path = os.path.join(destination_path, symlink["path"], symlink["name"])
        os.symlink(symlink["destination"], link_path)


def get_topic_folder(settings, topic):
    topic_name = topic["name"].strip().replace(" ", "_")
    download_folder = settings["download_folder"]
    return os.path.join(download_folder, topic_name)


def get_component_folder(topic_info, topic, component):
    topic_folder = get_topic_folder(topic_info, topic)
    component_type = component["type"].strip().replace(" ", "_").lower()
    return os.path.join(topic_folder, component_type)

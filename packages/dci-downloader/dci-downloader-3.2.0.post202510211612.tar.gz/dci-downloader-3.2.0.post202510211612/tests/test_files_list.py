import os

from dci_downloader.files_list import get_files_to_download, get_files_to_remove


def test_get_files_to_download_remove_existing_files():
    dci_files_list = {
        "directories": [],
        "files": [
            {
                "name": "a",
                "path": "",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "size": 0,
            },
            {
                "name": "b",
                "path": "",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "size": 0,
            },
            {
                "name": "c",
                "path": "",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "size": 0,
            },
        ],
        "symlinks": [],
    }
    test_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(test_dir, "data", "repo")
    expected_files_to_download = {
        "directories": [],
        "files": [
            {
                "name": "c",
                "path": "",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "size": 0,
                "source": "c",
                "destination": os.path.join(path, "c"),
            },
        ],
        "symlinks": [],
    }
    files_to_download = get_files_to_download(path, dci_files_list)
    assert files_to_download == expected_files_to_download


def test_get_files_to_remove():
    dci_files_list = {
        "directories": [],
        "files": [
            {
                "name": "b",
                "path": "",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "size": 0,
            },
            {
                "name": "c",
                "path": "subfolder",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "size": 0,
            },
        ],
        "symlinks": [],
    }
    test_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(test_dir, "data", "repo")
    files_to_remove = [os.path.join(path, "a")]
    assert get_files_to_remove(dci_files_list, path) == files_to_remove


def test_get_files_to_remove_add_files_with_different_sha():
    dci_files_list = {
        "directories": [],
        "files": [
            {
                "name": "a",
                "path": "",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "size": 0,
            },
            {
                "name": "b",
                "path": "",
                "sha256": "7848a92f625831b29caa0c74770603b78f8f6877541f803c33aa3741f946712d",
                "size": 7123,
            },
            {
                "name": "c",
                "path": "subfolder",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "size": 0,
            },
        ],
        "symlinks": [],
    }
    test_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(test_dir, "data", "repo")
    files_to_remove = [os.path.join(path, "b")]
    assert get_files_to_remove(dci_files_list, path) == files_to_remove

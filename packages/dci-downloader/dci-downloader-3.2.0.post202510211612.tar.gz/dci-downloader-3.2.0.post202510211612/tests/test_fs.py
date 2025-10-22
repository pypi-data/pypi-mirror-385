from dci_downloader.fs import get_component_folder, get_topic_folder


def test_get_component_folder():
    settings = {"name": "RHEL-9.*", "download_folder": "/var/www/html"}
    topic = {"id": "t1", "name": "RHEL-9.0"}
    component = {"id": "c1", "type": "Compose"}
    download_folder = get_component_folder(settings, topic, component)
    assert download_folder == "/var/www/html/RHEL-9.0/compose"


def test_get_topic_folder():
    settings = {"name": "RHEL-9.*", "download_folder": "/var/www/html"}
    topic = {"id": "t1", "name": "RHEL-9.0"}
    assert get_topic_folder(settings, topic) == "/var/www/html/RHEL-9.0"

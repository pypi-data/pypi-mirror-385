from dci_downloader.containers import (
    dci_images_list_yaml_to_skopeo_format,
    dci_image_info,
    has_command,
)


def test_dci_image_info():
    dci_image = "registry.distributed-ci.io/rhosp16/openstack-base:16.2_20210215.1"
    image_info = dci_image_info(dci_image)
    assert image_info == {
        "registry": "registry.distributed-ci.io",
        "image": "rhosp16/openstack-base",
        "tag": "16.2_20210215.1",
    }


def test_images_list_yaml_to_skopeo_yaml():
    images_list_yaml = """---
- registry.distributed-ci.io/rhosp16/openstack-base:16.2_20210215.1
- registry.distributed-ci.io/rhosp16/openstack-barbican-base:16.2_20210215.1
- registry.distributed-ci.io/rhosp16/openstack-barbican-api:16.2_20210215.1
- registry.distributed-ci.io/rhosp16/openstack-barbican-keystone-listener:16.2_20210215.1
- registry.distributed-ci.io/rhosp16/openstack-barbican-worker:16.2_20210215.1
"""
    skopeo_format = dci_images_list_yaml_to_skopeo_format(
        images_list_yaml, "toto", "superhardtoguess"
    )
    assert "registry.distributed-ci.io" in skopeo_format.keys()
    reg = skopeo_format["registry.distributed-ci.io"]
    assert "credentials" in reg
    assert "username" in reg["credentials"]
    assert reg["credentials"]["username"] == "toto"
    assert "password" in reg["credentials"]
    assert reg["credentials"]["password"] == "superhardtoguess"
    assert "images" in reg
    assert len(reg["images"]) == 5


def test_has_command():
    assert has_command("meh") is False
    assert has_command("/bin/ls") is True

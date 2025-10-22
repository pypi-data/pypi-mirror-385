import re
import tempfile
import yaml

from subprocess import check_output, CalledProcessError, Popen

DCI_CONTAINER_RE = re.compile(r"^(?P<registry>.+?)/(?P<image>.+):(?P<tag>.+)$")


def dci_image_info(dci_container):
    m = DCI_CONTAINER_RE.match(dci_container)
    return m.groupdict()


def dci_images_list_yaml_to_skopeo_format(
    images_list_yaml, registry_user, registry_password
):
    images_list = yaml.safe_load(images_list_yaml)
    skopeo_dict = {}
    for dci_container in images_list:
        image_info = dci_image_info(dci_container)
        if image_info["registry"] not in skopeo_dict:
            skopeo_dict[image_info["registry"]] = {
                "credentials": {
                    "username": registry_user,
                    "password": registry_password,
                },
                "images": {},
            }
        skopeo_dict[image_info["registry"]]["images"][image_info["image"]] = [
            image_info["tag"],
        ]

    return skopeo_dict


def has_command(command):
    try:
        check_output(command.split(" "))
    except (OSError, CalledProcessError):
        return False
    return True


def skopeo_sync(skopeo_yaml_source, destination_registry, skopeo_bin="skopeo"):
    with tempfile.NamedTemporaryFile(mode="w+t") as tmpf:
        yaml.dump(skopeo_yaml_source, tmpf)
        tmpf.flush()
        skopeo_sync_command = [
            skopeo_bin,
            "sync",
            "--src",
            "yaml",
            "--dest",
            "docker",
            "--dest-tls-verify=false",
            "--dest-no-creds",
            tmpf.name,
            destination_registry,
        ]
        print("Running skopeo sync as: `%s`" % " ".join(skopeo_sync_command))
        skopeo = Popen(skopeo_sync_command, bufsize=1)
        retcode = skopeo.wait()
        if retcode != 0:
            print(
                "Skopeo sync failed with exit code %d.\n"
                "Please check the skopeo logs above to determine the problem." % retcode
            )
            exit(retcode)
        print("Skopeo sync succeeeded.")


def mirror_container_images(registry, topic, images_list):
    if "registry" in topic["data"]:
        skopeo_yaml = dci_images_list_yaml_to_skopeo_format(
            images_list,
            topic["data"]["registry"]["login"],
            topic["data"]["registry"]["password"],
        )
        skopeo_sync(skopeo_yaml, registry)

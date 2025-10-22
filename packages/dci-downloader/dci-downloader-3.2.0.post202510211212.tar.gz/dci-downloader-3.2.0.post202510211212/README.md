# DCI Downloader

`dci-downloader` is a useful tool for downloading the latest versions of Red Hat products.

## TLDR

```console
$ sudo dnf -y install https://packages.distributed-ci.io/dci-release.el8.noarch.rpm
$ sudo dnf -y install dci-downloader
$ source ~/dcirc.sh
$ dci-downloader RHEL-9.2 /tmp/repo
```

## Requirements

### Red Hat SSO

DCI is connected to the Red Hat SSO. You will need a [Red Hat account](https://access.redhat.com/).

### Remoteci

A remoteci is a Virtual Machine or a baremetal server running RHEL.
You should check that your remoteci:

- Is running the latest RHEL 8 release.
- Has enough free space in the destination folder.
- Should be able to reach:
  - `https://api.distributed-ci.io` (443).
  - `https://repo.distributed-ci.io` (443).
  - `https://registry.distributed-ci.io` (443).

## Installation

The `dci-downloader` is packaged and available as a RPM files.

```console
$ sudo dnf -y install https://packages.distributed-ci.io/dci-release.el8.noarch.rpm
$ sudo dnf -y install dci-downloader
```

## Configuration

### Remoteci creation

DCI is connected to the Red Hat SSO. You need to log in `https://www.distributed-ci.io` with your redhat.com SSO account. Your user account will be created in our database the first time you connect.

After the first connection you can create a remoteci. Go to [https://www.distributed-ci.io/remotecis](https://www.distributed-ci.io/remotecis) and click `Create a new remoteci` button. Once your `remoteci` is created, you can retrieve the connection information in the `Authentication` column. Save those information in `~/dcirc.sh` file.

At this point, you can validate your credentials with the following commands:

```console
$ source ~/dcirc.sh
$ dcictl remoteci-list
```

If you see your remoteci in the list, everything is working great so far.

### Topic access

Before using dci-downloader, we need to check the list of topic (version of the product) you have access to:

```console
$ source ~/dcirc.sh
$ dcictl topic-list
```

If you don't see any topic then **you should contact your EPM at Red Hat** which will give you access to the topic you need.

## Usage

You can now download the latest version of a product using dci-downloader.

### RHEL examples

Example command to download the latest RHEL-9.2 components into /tmp/repo folder.

```console
$ dci-downloader RHEL-9.2 /tmp/repo
```

### RHOSP examples

```console
$ dci-downloader OSP16.1 /tmp/repo
```

dci-downloader also allows to mirror the container images associated with the component to a [local anonymous registry](#local-anonymous-registry).

```
$ dci-downloader OSP16.1 /tmp/repo --registry local_registry_host:5000
```

<a name="local-anonymous-registry">ℹ NOTE:</a> except when using dci-openstack-agent, it's the user's responsibility to provide a working anonymous registry.
If needed a simple way to setup one is by using Docker Distribution registry in a container

```console
$ podman run --rm -p 5000:5000 registry:2
```

ℹ NOTE: dci-downloader does not currently clean/purge/untag any image on the registry, leaving this responsibility to the the user until a suitable solution is provided.

## Options

By default dci-downloader will download all variants for x86_64 architecture without debug RPMs.

### Download other architectures

To download other architectures you can specify those using `--arch` option

Download x86_64 and ppc64le architectures for RHEL-9.2 topic:

```console
$ dci-downloader RHEL-9.2 /tmp/repo --arch x86_64 --arch ppc64le
```

### Specific variants

To download only specific variants you can specify those using `--variant`

Download only AppStream and BaseOS variants:

```console
$ dci-downloader RHEL-9.2 /tmp/repo --variant AppStream --variant BaseOS
```

### Filters

By default dci-downloader download the latest components attached to a topic.
But if you want to filter those component, you can use the `--filter <type>` or `--filter <type>:<tag>` option.

Download only the latest RHEL-9.2 `compose`

```console
$ dci-downloader RHEL-9.2 /tmp/repo --filter=compose
```

Download only the latest RHEL-9.2 `compose` with tag `nightly`

```console
$ dci-downloader RHEL-9.2 /tmp/repo --filter=compose:nightly
```

### Download the whole compose

To download everything you can add the `--all` flag

```console
$ dci-downloader RHEL-9.2 /tmp/repo --all
```

### Debug RPMs

To download debug RPMs you can add the `--debug` flag

Download RHEL-9.2 compose with debug rpms

```console
$ dci-downloader RHEL-9.2 /tmp/repo --debug
```

### Download only specified packages

To download packages specified on the command line, use the `--package-filter` flag

Download all kernel and glibc packages for RHEL-8.8 for the ppc64le architecture

```console
$ dci-downloader RHEL-8.8 /tmp --variant BaseOS --arch ppc64le --package-filter=kernel --package-filter=glibc
```
### Settings file

You can use a settings file to send parameters to parameterize dci-downloader.

Use `--settings` parameter:

```console
$ dci-downloader --settings "/etc/dci-rhel-agent/settings.yml"
```

All settings from settings.yml file will overwrite cli parameters.

Examples of a settings file:

```yaml
download_folder: /tmp/repo
topics:
  - name: RHEL-9.2
    filters:
      - type: compose
        tag: nightly
  - name: RHEL-8.6
    filters:
      - type: compose
        tag: milestone
    archs:
      - ppc64le
    variants:
      - AppStream
      - name: BaseOS
        with_debug: true
```

## Proxy

If you are using a proxy, just add `HTTP_PROXY` or `HTTPS_PROXY` env variable pointing to your proxy.

## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Help

If something is not working correctly, ensure you have the latest version installed

```console
$ dci-downloader --version
$ dci-downloader --help
```

To contact DCI see [Questions and help](https://docs.distributed-ci.io/question_and_help.html)

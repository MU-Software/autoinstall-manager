# syntax=docker/dockerfile:1
FROM ubuntu:24.04

SHELL [ "/bin/bash", "-euxvc"]

ENV TZ=Asia/Seoul \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=UTF-8

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        7zip build-essential ca-certificates cloud-image-utils cloud-init curl \
        git grub-pc grub-pc-bin isolinux rsync sudo tree \
    && git clone https://github.com/canonical/subiquity.git

WORKDIR /subiquity
RUN make install_deps

COPY <<EOF /ubuntu_iso_builder.sh
#!/bin/bash
set -euxo pipefail

NOCLOUD_URL="\${NOCLOUD_URL:-http://autoinstall-manager.local/nocloud/}"
UBUNTU_ISO_PATH="\${UBUNTU_ISO_PATH:-/input/ubuntu-input.iso}"
OUTPUT_ISO_PATH="\${OUTPUT_ISO_PATH:-/output/ubuntu-output.iso}"

mkdir -p /tmp/iso \
7z x -o/tmp/iso "\${UBUNTU_ISO_PATH}" boot/grub/grub.cfg md5sum.txt

sed -E -i "s@^( *linux[[:space:]]+/casper/vmlinuz)[[:space:]]+---@\\1 autoinstall ds=nocloud-net\\;s=\${NOCLOUD_URL}__dmi.system-serial-number__/ ip=dhcp cloud-config-url=/dev/null ---@" /tmp/iso/boot/grub/grub.cfg

hash=\$(md5sum /tmp/iso/boot/grub/grub.cfg | awk '{print \$1}')
sed -i -E "/^[0-9a-f]{32}[[:space:]]+\\.\\/boot\\/grub\\/grub\\.cfg\$/c\\\${hash} ./boot/grub/grub.cfg" /tmp/iso/md5sum.txt

xorriso\\
    -indev "\${UBUNTU_ISO_PATH}"\\
    -outdev "\${OUTPUT_ISO_PATH}"\\
    -boot_image any replay\\
    -volid 'UBUNTU_AUTOINSTALL'\\
    -map /tmp/iso/boot/grub/grub.cfg /boot/grub/grub.cfg\\
    -map /tmp/iso/md5sum.txt /md5sum.txt\\
    -compliance joliet_long_names -joliet on -rockridge on\\
    -end
EOF

RUN chmod +x /ubuntu_iso_builder.sh

#!/usr/bin/env bash

set -euo pipefail

usage() {
  echo "Usage: $0 BOOTX64.EFI SREP_CONFIG OUTPUT_DIR [VERSION]" >&2
  exit 2
}

[[ $# -ge 3 && $# -le 4 ]] || usage

efi_path=$1
config_path=$2
output_dir=$3
version=${4:-dev}

[[ -s "$efi_path" ]] || { echo "Missing or empty EFI executable: $efi_path" >&2; exit 1; }
[[ -s "$config_path" ]] || { echo "Missing or empty SREP configuration: $config_path" >&2; exit 1; }

for command_name in cmp mcopy mdir mformat mmd sgdisk sha256sum truncate xz zip; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "Required command not found: $command_name" >&2
    exit 1
  }
done

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd -- "$script_dir/.." && pwd)
usb_readme="$repo_root/configs/srep/USB-README.txt"

[[ -s "$usb_readme" ]] || { echo "Missing USB readme: $usb_readme" >&2; exit 1; }

safe_version=${version//[^A-Za-z0-9._-]/-}
artifact_name="lenovo-15arh05-srep-usb-$safe_version"

mkdir -p "$output_dir"
output_dir=$(cd -- "$output_dir" && pwd)

work_dir=$(mktemp -d)
trap 'rm -rf -- "$work_dir"' EXIT

usb_root="$work_dir/usb-root"
image_path="$work_dir/$artifact_name.img"
zip_path="$output_dir/$artifact_name-files.zip"
xz_path="$output_dir/$artifact_name.img.xz"

mkdir -p "$usb_root/EFI/BOOT"
cp -- "$efi_path" "$usb_root/EFI/BOOT/BOOTX64.EFI"
cp -- "$config_path" "$usb_root/SREP_Config.cfg"
cp -- "$usb_readme" "$usb_root/README.txt"

# A fixed-size image makes the GPT layout deterministic. The single FAT32 EFI
# System Partition starts at sector 2048 and ends at the last GPT-usable sector.
sector_size=512
disk_sectors=262144
first_sector=2048
# Leave the final MiB free for the backup GPT and keep both partition edges on
# 1 MiB boundaries for broad USB-writer and firmware compatibility.
last_sector=260095
partition_sectors=$((last_sector - first_sector + 1))
partition_offset=$((first_sector * sector_size))

truncate -s $((disk_sectors * sector_size)) "$image_path"
sgdisk --clear \
  --new="1:${first_sector}:${last_sector}" \
  --typecode=1:ef00 \
  --change-name=1:SREP \
  "$image_path" >/dev/null

mformat -i "$image_path@@$partition_offset" \
  -F -h 255 -s 63 -H "$first_sector" -T "$partition_sectors" -v SREP ::
mmd -i "$image_path@@$partition_offset" ::/EFI ::/EFI/BOOT
mcopy -i "$image_path@@$partition_offset" \
  "$usb_root/EFI/BOOT/BOOTX64.EFI" ::/EFI/BOOT/BOOTX64.EFI
mcopy -i "$image_path@@$partition_offset" \
  "$usb_root/SREP_Config.cfg" ::/SREP_Config.cfg
mcopy -i "$image_path@@$partition_offset" \
  "$usb_root/README.txt" ::/README.txt

# Read the files back from the completed image. This catches offset, FAT, and
# copy errors before an artifact can be published.
mdir -i "$image_path@@$partition_offset" ::/EFI/BOOT/BOOTX64.EFI >/dev/null
mdir -i "$image_path@@$partition_offset" ::/SREP_Config.cfg >/dev/null
mcopy -i "$image_path@@$partition_offset" ::/SREP_Config.cfg "$work_dir/config-check.cfg"
cmp -- "$config_path" "$work_dir/config-check.cfg"

(
  cd -- "$usb_root"
  zip -9 -q -r "$zip_path" EFI SREP_Config.cfg README.txt
)

xz -T0 -9e -c -- "$image_path" > "$xz_path"

(
  cd -- "$output_dir"
  sha256sum "$(basename -- "$xz_path")" "$(basename -- "$zip_path")" > SHA256SUMS
)

echo "Created:"
echo "  $xz_path"
echo "  $zip_path"
echo "  $output_dir/SHA256SUMS"

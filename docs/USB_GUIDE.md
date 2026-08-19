# SREP USB Creation and Boot Guide

This guide reproduces the **temporary runtime reveal** of the hidden InsydeH2O
menus documented by this repository. It covers the complete path from obtaining
SREP to opening `Advanced`, `AMD PBS`, and `AMD CBS` on the physical laptop.

> [!WARNING]
> This procedure exposes firmware controls that Lenovo normally hides. Opening
> the menus is non-persistent; saving a changed setting may not be. A wrong
> display, storage, security, voltage, memory, or SoC setting can cause a no-boot
> or no-display condition. Follow the guide in observation-only mode and do not
> press `F10` or save changes.

## Confirmed test target

| Item | Confirmed value |
|---|---|
| Laptop | Lenovo IdeaPad Gaming 3 15ARH05 |
| Machine type | `82EY` |
| Product string | `IP3GAMING-15ARH` |
| Installed BIOS used for the physical test | `FCCN19WW` |
| Firmware used for IFR research | `FCCN21WW` |
| SREP version | `0.1.4c` |
| Boot mode | UEFI |
| Secure Boot during the test | Disabled |
| Result | `Advanced`, `AMD PBS`, and `AMD CBS` visible |

Do not assume compatibility with another Lenovo model or firmware family. If a
pattern is not found, stop and preserve `SREP.log`; do not invent replacement
patterns or write setup variables by trial and error.

## What you need

- A USB drive whose contents may be erased.
- AC power connected and a charged laptop battery.
- The ready-to-write release image, or a copy of this repository when building
  it locally.
- A trusted x86-64 SREP EFI executable only when following the manual path.
- Access to the Windows device-encryption or BitLocker recovery key, if enabled.
- A second device from which to read this guide is strongly recommended.

GitHub Actions builds the third-party SREP application from the pinned source
revision and publishes it inside the ready-to-write image. The repository does
not track the binary itself and no Lenovo firmware is included.

## Process overview

```text
Build or obtain SREP
        ↓
Create a GPT/FAT32 USB
        ↓
Copy BOOTX64.EFI and SREP_Config.cfg
        ↓
Disable Secure Boot and boot the USB in UEFI mode
        ↓
SREP patches H2OFormBrowserDxe in memory
        ↓
SetupUtilityApp opens with the hidden menus visible
```

## Fast path — use the ready-to-write image

Open the [latest GitHub Release](https://github.com/root-hunter/lenovo_bios/releases/latest)
and download:

- `lenovo-15arh05-srep-usb-*.img.xz`, the compressed GPT/FAT32 disk image;
- `SHA256SUMS`, used to verify the download.

The release also provides `*-files.zip` for users who already have a correctly
formatted GPT/FAT32 USB and prefer to copy the files manually.

> [!CAUTION]
> Writing the `.img` replaces the partition table and all data on the selected
> USB drive. Confirm its manufacturer and capacity. Never select the system
> disk.

On Windows, verify the SHA-256 value, decompress the image with 7-Zip, and write
the resulting `.img` with Rufus or balenaEtcher. Select the image and the USB by
model and capacity; do not use ISO extraction mode.

On Linux, download both files into one directory and run:

```bash
grep '\.img\.xz$' SHA256SUMS | sha256sum --check -
xz --decompress --keep lenovo-15arh05-srep-usb-*.img.xz
lsblk --output NAME,SIZE,MODEL,TRAN,MOUNTPOINTS
```

After identifying the whole USB device—not one of its partitions—write it with
the explicit device path. The following is only a template; replace `/dev/sdX`
after checking `lsblk`:

```bash
sudo dd if=lenovo-15arh05-srep-usb-*.img \
  of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

Remove and reconnect the drive. It should expose a FAT32 partition labelled
`SREP` containing `EFI/BOOT/BOOTX64.EFI`, `SREP_Config.cfg`, and `README.txt`.
Continue at [Step 6 — Prepare the laptop](#step-6--prepare-the-laptop).

### How the published image is produced

The workflow in
[`build-usb-image.yml`](../.github/workflows/build-usb-image.yml) performs the
complete pinned-source build:

1. checks out EDK II and SREP at the commits pinned in the workflow;
2. builds the x86-64 release EFI application;
3. validates its PE/COFF architecture;
4. creates a 128 MiB GPT image with one FAT32 EFI System Partition;
5. copies and reads back the bootloader and tracked configuration;
6. publishes the compressed image, manual-copy ZIP, build information, and
   SHA-256 checksums as a workflow artifact;
7. publishes the same files to GitHub Releases when a `v*` tag is pushed or a
   manual run supplies a `release_tag`.

Pushes to `main`, pull requests, and manual runs without a release tag remain
downloadable as workflow artifacts for 30 days. Only `v*` tags or a manual
`release_tag` publish files to GitHub Releases. The packaging logic is kept in
[`package_srep_usb.sh`](../scripts/package_srep_usb.sh) so the disk layout can be
tested independently of GitHub Actions.

### Local build with the latest stable EDK II

To reproduce the current EDK II stable release locally, install the build and
image tools on Ubuntu or Debian:

```bash
sudo apt update
sudo apt install build-essential file gdisk git mtools nasm \
  python3 python3-setuptools uuid-dev xz-utils zip
```

Then run from the repository root:

```bash
scripts/build_srep_latest.sh
```

By default this checks out `edk2-stable202605`, keeps the temporary source tree
under `/tmp/lenovo-srep-latest-build`, and writes the resulting image and build
metadata to `artifacts/releases/latest-edk2/`. Both locations can be overridden:

```bash
scripts/build_srep_latest.sh /path/to/build-workspace /path/to/output
```

The script fetches only the five EDK II submodules needed by this build and
automatically applies
[`srep-edk2-stable202605.patch`](../patches/srep-edk2-stable202605.patch). It
uses the current `GCC` toolchain profile because modern EDK II no longer defines
the historical `GCC5` profile name.

Verify the generated files before writing them:

```bash
cd artifacts/releases/latest-edk2
sha256sum --check SHA256SUMS
xz --decompress --keep lenovo-15arh05-srep-usb-*.img.xz
lsblk --output NAME,SIZE,MODEL,TRAN,MOUNTPOINTS
```

After identifying a stable USB device by model and capacity, follow the Linux
`dd` command in the [fast path](#fast-path--use-the-ready-to-write-image). Never
reuse an old `/dev/sdX` name after reconnecting a drive; run `lsblk` again.

The `edk2-stable202605` and pinned SREP source combination has successfully
booted on the documented physical test machine. The EDK II commit, compiler,
Python version, EFI hash, disk-image hash, and ZIP hash are recorded for every
rebuild. Since toolchain changes can alter the binary, first boot each new
artifact in observation-only mode and exit without saving.

## Step 1 — Get this repository

Clone the repository or download it as a ZIP from GitHub:

```bash
git clone https://github.com/root-hunter/lenovo_bios.git
```

The remaining path examples assume that the current directory contains the
new `lenovo_bios/` directory.

The file used on the USB is:

```text
configs/srep/15ARH05-FCCN21WW.cfg
```

Do not copy and retype its hexadecimal patterns manually. Copy the tracked file
so that a transcription error cannot alter the patch.

## Step 2 — Obtain `BOOTX64.EFI`

### Option A: verify an existing trusted build

If you already have the exact SREP executable used in this research, it has the
following properties:

| Property | Tested value |
|---|---|
| Original build filename | `SmokelessRuntimeEFIPatcher.efi` |
| USB filename | `BOOTX64.EFI` |
| Size | 16,640 bytes |
| SHA-256 | `79c46eb5fdb37ceb0aff7dcafa385c3f2cf018538f6e82704081242a714529da` |

Linux:

```bash
sha256sum SmokelessRuntimeEFIPatcher.efi
```

PowerShell:

```powershell
Get-FileHash .\SmokelessRuntimeEFIPatcher.efi -Algorithm SHA256
```

The hash identifies the tested artifact. A locally compiled binary may differ
because of the build environment; in that case verify the source revisions and
build output rather than treating a hash mismatch alone as proof of a problem.

### Option B: build the tested source revisions on Linux or WSL

The following reproduces the upstream Ubuntu build workflow with the revisions
used for the successful test.

Install the required tools on Ubuntu or Debian:

```bash
sudo apt update
sudo apt install build-essential git nasm uuid-dev iasl python3 python3-setuptools
```

Create a separate build workspace and fetch EDK II:

```bash
mkdir srep-build
cd srep-build
git clone --branch edk2-stable202205 https://github.com/tianocore/edk2.git
cd edk2
git checkout 16779ede2d366bfc6b702e817356ccf43425bcc8
git submodule update --init --recursive
```

Place SREP inside the EDK II workspace and select the tested commit:

```bash
git clone https://github.com/barlowhaydnb/SmokelessRuntimeEFIPatcher.git
git -C SmokelessRuntimeEFIPatcher checkout 83d0ae47c9a48b3a2227aef06fb98a372c5ba354
```

Build EDK II BaseTools and the x86-64 release application:

```bash
make -C BaseTools
. ./edksetup.sh
build -b RELEASE -t GCC5 \
  -p SmokelessRuntimeEFIPatcher/SmokelessRuntimeEFIPatcher.dsc \
  -a X64 -s
```

The resulting executable is:

```text
Build/SmokelessRuntimeEFIPatcher/RELEASE_GCC5/X64/SmokelessRuntimeEFIPatcher.efi
```

If the build fails, do not substitute an unrelated EFI menu tool. Resolve the
build error or use a trusted SREP build from the same source revision.

## Step 3 — Erase and format the USB drive

The USB must contain a GPT partition table and a FAT32 filesystem. This step
erases the selected drive.

> [!CAUTION]
> Confirm the USB by manufacturer, capacity, and current contents before erasing
> it. Selecting the system disk will destroy data.

### Windows

Open Terminal or Command Prompt **as Administrator**, then start DiskPart:

```text
diskpart
list disk
select disk N
detail disk
```

Replace `N` with the USB disk number. Read the `detail disk` output and stop if
the model or capacity is not the USB drive. Only after confirming the target:

```text
clean
convert gpt
create partition primary
format fs=fat32 quick label=SREP
assign
exit
```

Record the drive letter assigned to `SREP`.

### Linux with GNOME Disks

1. Open **Disks**.
2. Select the USB drive by model and capacity in the left column.
3. Open the drive menu and choose **Format Disk**.
4. Select **GPT** as the partitioning scheme.
5. Create one partition using the full available space.
6. Format that partition as **FAT** and label it `SREP`.
7. Mount the new partition.

The graphical method is recommended because it keeps the selected physical drive
visible throughout the destructive step.

## Step 4 — Copy the two required files

Create this exact layout on the FAT32 partition:

```text
SREP USB root
├── EFI/
│   └── BOOT/
│       └── BOOTX64.EFI
└── SREP_Config.cfg
```

The names and locations matter:

- Rename `SmokelessRuntimeEFIPatcher.efi` to `BOOTX64.EFI`.
- Put it in `EFI/BOOT/`.
- Copy `configs/srep/15ARH05-FCCN21WW.cfg` to the USB root.
- Rename that copied configuration to `SREP_Config.cfg`.
- Make sure Windows has not silently created `SREP_Config.cfg.txt`.

Example on Linux, after replacing `/media/USER/SREP` with the actual mount path:

```bash
# If you have just completed Option B, return to the directory that contains
# both lenovo_bios/ and srep-build/.
cd ../..

mkdir -p /media/USER/SREP/EFI/BOOT
cp srep-build/edk2/Build/SmokelessRuntimeEFIPatcher/RELEASE_GCC5/X64/SmokelessRuntimeEFIPatcher.efi \
  /media/USER/SREP/EFI/BOOT/BOOTX64.EFI
cp lenovo_bios/configs/srep/15ARH05-FCCN21WW.cfg \
  /media/USER/SREP/SREP_Config.cfg
sync
```

If the repository and build workspace are elsewhere, adjust only the source
paths. If you used Option A, replace the first source path with the location of
your verified SREP executable. Do not change the destination names.

## Step 5 — Verify the finished USB

Before ejecting it, confirm all of the following:

- [ ] The partition table is GPT.
- [ ] The filesystem is FAT32.
- [ ] `EFI/BOOT/BOOTX64.EFI` exists.
- [ ] `SREP_Config.cfg` exists in the root, not inside `EFI`.
- [ ] The configuration is the tracked file from this repository.
- [ ] There is no hidden `.txt` extension.
- [ ] `BOOTX64.EFI` is the x86-64 SREP application.

On Linux, from the USB root:

```bash
find . -maxdepth 3 -type f -print
sha256sum EFI/BOOT/BOOTX64.EFI
```

Expected file listing:

```text
./EFI/BOOT/BOOTX64.EFI
./SREP_Config.cfg
```

Safely eject the drive after all writes have completed.

## Step 6 — Prepare the laptop

1. Save your work and shut down Windows cleanly.
2. Connect the AC adapter.
3. Make sure the BitLocker or device-encryption recovery key is available.
4. Enter Lenovo Setup with `F2`, `Fn+F2`, or the Novo button.
5. Disable **Secure Boot**.
6. Keep the machine in **UEFI** boot mode; do not enable Legacy/CSM mode.
7. Save this Secure Boot change and shut down.

Disabling Secure Boot is a prerequisite for the unsigned SREP application. It
may cause Windows to request its recovery key on a later boot.

## Step 7 — Boot SREP

1. Insert the prepared USB drive.
2. Power on and open the boot menu with `F12`, `Fn+F12`, or the Novo button.
3. Select the USB entry marked as UEFI.
4. Wait for SREP `0.1.4c` to open and parse `SREP_Config.cfg`.
5. Let the configuration launch `SetupUtilityApp` automatically.

Do **not** exit SREP and then enter the ordinary F2 setup. The patch exists only
in the current boot session, so the Setup Utility must be launched by the final
`Op LoadFromFV` / `Op Exec` commands in the configuration.

## Step 8 — Confirm the result without saving

A successful run opens Lenovo Setup Utility with these additional entries in the
left navigation:

- `Advanced`
- `AMD PBS`
- `AMD CBS`

Compare the result with the
[physical-test gallery](SCREENSHOTS.md), especially the
[Advanced overview](../screenshots/advanced-01-menu-overview.jpg).

Browse only. Do not change values, load defaults, or press `F10`. To finish, use
the Setup Utility option that exits while discarding changes, shut the laptop
down, and remove the USB drive.

The menus disappear after a normal reboot because the SPI firmware was not
modified.

## Step 9 — Preserve `SREP.log`

SREP creates `SREP.log` in the USB root. After returning to the operating system:

1. Copy the log to a safe location.
2. Record the laptop model and installed BIOS version with it.
3. Check for successful module loading, pattern matches, patch operations, and
   execution of `SetupUtilityApp`.
4. Remove serial numbers, UUIDs, or other machine identifiers before publishing
   the log.

## Troubleshooting

| Symptom | Check or action |
|---|---|
| USB does not appear in the boot menu | Confirm GPT, FAT32, UEFI mode, Secure Boot disabled, and `EFI/BOOT/BOOTX64.EFI`. |
| `Failed on Opening SREP_Config` | Confirm the root-level name `SREP_Config.cfg`; check for a hidden `.txt` extension. |
| `No Patter Found` in the log | The message contains SREP's original typo. Stop: the firmware/module does not match that pattern. Do not continue with guessed bytes. |
| Setup Utility does not open | Confirm the final `LoadFromFV SetupUtilityApp` and `Exec` operations are present in the copied configuration. |
| Setup opens without hidden entries | Confirm it was launched directly by SREP in the same boot session; then inspect `SREP.log` for missing matches. |
| Windows requests a recovery key | Use the recovery key saved before changing Secure Boot state. Do not reset the TPM. |
| Black screen before any setting was saved | Power off, remove the USB, and boot normally. The runtime patch itself should not persist across power-off. |

## What this procedure does not do

- It does not flash or permanently modify the BIOS image.
- It does not back up the physical SPI flash.
- It does not validate exposed settings as safe.
- It does not make `FCCN21WW` IFR offsets authoritative for `FCCN19WW`.
- It does not provide a recovery path after saving a dangerous firmware value.

Before any experiment that writes settings, obtain and verify a machine-specific
SPI backup and prepare a physical recovery method. The current project result is
the safe observation and documentation of the runtime-visible forms.

## Related documentation

- [Project overview and research notes](../README.md)
- [Tracked SREP configuration](../configs/srep/15ARH05-FCCN21WW.cfg)
- [Advanced option inventory](ADVANCED_OPTIONS.md)
- [Physical-test gallery](SCREENSHOTS.md)
- [Upstream SREP documentation](https://github.com/barlowhaydnb/SmokelessRuntimeEFIPatcher)

LENOVO IDEAPAD GAMING 3 15ARH05 - FCCN FAMILY - SREP USB
========================================================

PROFILE
  Machine: Lenovo IdeaPad Gaming 3 15ARH05 / type 82EY
  Product: IP3GAMING-15ARH
  BIOS family: FCCN
  Firmware analyzed: FCCN21WW
  Installed BIOS tested on hardware: FCCN19WW
  Boot mode: UEFI with Secure Boot disabled

WARNING
  This profile exposes firmware settings that Lenovo normally hides. Opening
  the menus is temporary, but saving a changed setting may not be. An unsafe
  value can cause a no-boot or no-display condition. Browse in
  observation-only mode, exit without saving, and do not load setup defaults.

  A matching FCCN prefix alone does not prove compatibility. On an unlisted
  version, stop if every expected pattern is not found exactly as documented
  and preserve SREP.log. Do not invent replacement patterns on the machine.

CONTENTS
  EFI/BOOT/BOOTX64.EFI  SREP EFI application built from the pinned source
  SREP_Config.cfg       Runtime visibility configuration for this profile

SREP source and attribution:
  https://github.com/barlowhaydnb/SmokelessRuntimeEFIPatcher

BOOT
  1. Make sure the BitLocker/device-encryption recovery key is available.
  2. Disable Secure Boot while keeping the machine in UEFI mode.
  3. Open Lenovo's boot menu and select the UEFI entry for this USB drive.
  4. Let SREP launch SetupUtilityApp in the same session.
  5. Browse only, then exit without saving.

Full guide and checks:
  https://github.com/root-hunter/lenovo_bios/blob/main/docs/USB_GUIDE.md

This package contains no Lenovo firmware image.

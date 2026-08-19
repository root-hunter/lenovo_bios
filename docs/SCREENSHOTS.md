# Physical Test Gallery

These photographs document the successful runtime exposure of Lenovo's hidden
InsydeH2O setup pages on the IdeaPad Gaming 3 15ARH05 test laptop. The machine is
running `FCCN19WW`; SREP applies the combined form-set patch in memory and starts
`SetupUtilityApp` in the same boot session.

The result was also shared in this
[Reddit community discussion](https://www.reddit.com/r/LenovoLegion/comments/1vsqzod/comment/p4o1d51/).
To reproduce the same runtime result, start with the
[SREP USB creation and boot guide](USB_GUIDE.md).

> [!IMPORTANT]
> The gallery proves that the menus can be rendered. It does **not** prove that
> every control works, that the displayed defaults are safe, or that the
> `FCCN21WW` IFR offsets are identical on `FCCN19WW`. No photographed value
> should be copied as a recommendation.

## At a glance

| Advanced | AMD PBS | AMD CBS |
|---|---|---|
| [![Advanced menu](../screenshots/advanced-01-menu-overview.jpg)](../screenshots/advanced-01-menu-overview.jpg) | [![AMD PBS menu](../screenshots/pbs-01-main-platform-controls.jpg)](../screenshots/pbs-01-main-platform-controls.jpg) | [![AMD CBS menu](../screenshots/cbs-02-cpu-prefetch-controls.jpg)](../screenshots/cbs-02-cpu-prefetch-controls.jpg) |
| Hidden platform configuration forms | Board- and platform-specific controls | Processor, fabric, memory, and I/O controls |

## Test context and evidence

| Capture | What it documents |
|---|---|
| [![System information](../screenshots/00-test-system-information-fccn19ww.jpg)](../screenshots/00-test-system-information-fccn19ww.jpg) | Physical machine context: IdeaPad Gaming 3 15ARH, BIOS `FCCN19WW`, Secure Boot disabled, and the newly visible `Advanced`, `AMD PBS`, and `AMD CBS` navigation entries. Machine-specific identifiers were obscured before publication. |
| [![AMD PBS controls](../screenshots/01-test-amd-pbs-storage-gpp-controls.jpg)](../screenshots/01-test-amd-pbs-storage-gpp-controls.jpg) | A rendered AMD PBS page with storage-power and GPP routing controls, confirming that the entry opens a functional form rather than an empty label. |

## Hidden Advanced menu

The `Advanced` photographs closely match the categories reconstructed from the
`FCCN21WW` IFR. This is useful cross-version evidence, but not proof that the
variable layout is unchanged on the installed `FCCN19WW` firmware.

| Capture | Page or subject |
|---|---|
| [![Advanced index](../screenshots/advanced-01-menu-overview.jpg)](../screenshots/advanced-01-menu-overview.jpg) | Advanced index: Video, USB, Chipset, ACPI, CPU, DASH, and Above 4GB MMIO controls. |
| [![PCI Express](../screenshots/advanced-02-pcie-pspp-gpp-controls.jpg)](../screenshots/advanced-02-pcie-pspp-gpp-controls.jpg) | PCI Express configuration and PSPP/GPP policy choices. |
| [![GPP control](../screenshots/advanced-03-pcie-gpp-enable.jpg)](../screenshots/advanced-03-pcie-gpp-enable.jpg) | Continuation of PCI Express configuration, showing an individual GPP enable control. |
| [![Boot configuration](../screenshots/advanced-04-boot-configuration.jpg)](../screenshots/advanced-04-boot-configuration.jpg) | Boot Configuration, including NumLock and Fast Recovery. |
| [![Firmware TPM](../screenshots/advanced-05-firmware-tpm-option.jpg)](../screenshots/advanced-05-firmware-tpm-option.jpg) | Peripheral Configuration with the firmware TPM selection expanded. |
| [![Discrete TPM](../screenshots/advanced-06-discrete-tpm-option.jpg)](../screenshots/advanced-06-discrete-tpm-option.jpg) | Peripheral Configuration with the discrete TPM choice visible. |
| [![SATA configuration](../screenshots/advanced-07-sata-ahci-raid-controls.jpg)](../screenshots/advanced-07-sata-ahci-raid-controls.jpg) | IDE/SATA controller, AHCI, RAID, and port controls. |
| [![NVMe configuration](../screenshots/advanced-08-nvme-devices.jpg)](../screenshots/advanced-08-nvme-devices.jpg) | NVMe page and the storage devices detected by Setup Utility. |
| [![Video configuration](../screenshots/advanced-09-video-configuration.jpg)](../screenshots/advanced-09-video-configuration.jpg) | Video Configuration, including HDMI audio and brightness-control method. |
| [![USB configuration](../screenshots/advanced-10-usb-support.jpg)](../screenshots/advanced-10-usb-support.jpg) | USB BIOS and USB 2.0 support controls. |
| [![USB ports](../screenshots/advanced-11-usb-port-controls.jpg)](../screenshots/advanced-11-usb-port-controls.jpg) | Per-controller USB port controls. |
| [![ACPI configuration](../screenshots/advanced-12-acpi-controls.jpg)](../screenshots/advanced-12-acpi-controls.jpg) | ACPI table/features and latency-related controls. |
| [![CPU configuration](../screenshots/advanced-13-cpu-svm-locks.jpg)](../screenshots/advanced-13-cpu-svm-locks.jpg) | CPU Configuration with SVM and lock-related controls. |
| [![DASH configuration](../screenshots/advanced-14-dash-amd-kvm.jpg)](../screenshots/advanced-14-dash-amd-kvm.jpg) | DASH and AMD remote-KVM management controls. |

## Standard pages observed in the patched session

These pages are not the hidden-menu discovery itself, but they complete the
record of the Setup Utility session and show that ordinary setup forms remained
accessible.

| Power | Boot |
|---|---|
| [![Power page](../screenshots/standard-01-power-settings.jpg)](../screenshots/standard-01-power-settings.jpg) | [![Boot page](../screenshots/standard-02-boot-settings.jpg)](../screenshots/standard-02-boot-settings.jpg) |

## AMD PBS

AMD PBS is a platform-specific form set. The captures cover firmware versions,
storage and PCIe routing, USB Type-C behavior, recovery support, audio, and
board-level options. Labels are recorded for identification only.

| Capture | Page or subject |
|---|---|
| [![PBS main controls](../screenshots/pbs-01-main-platform-controls.jpg)](../screenshots/pbs-01-main-platform-controls.jpg) | Main PBS platform and storage-power controls. |
| [![PBS firmware versions](../screenshots/pbs-02-firmware-versions.jpg)](../screenshots/pbs-02-firmware-versions.jpg) | AGESA, PSP, ABL, APCB, SMU, DXIO, MP2, VBIOS, GOP, EC, and USB-PD version inventory. |
| [![PBS platform settings](../screenshots/pbs-03-platform-policy-controls.jpg)](../screenshots/pbs-03-platform-policy-controls.jpg) | Additional platform, recovery, and device policy settings. |
| [![PBS USB-C settings](../screenshots/pbs-04-recovery-usb-c-controls.jpg)](../screenshots/pbs-04-recovery-usb-c-controls.jpg) | OS recovery, PLDR, USB Type-C connector, and related behavior. |
| [![PBS board settings](../screenshots/pbs-05-board-power-audio-controls.jpg)](../screenshots/pbs-05-board-power-audio-controls.jpg) | Board-level power, audio, LED, and miscellaneous policy controls. |

## AMD CBS

AMD CBS exposes low-level processor and SoC configuration. These are the most
dangerous pages in the gallery: incorrect CPU, fabric, memory, graphics, or I/O
settings can cause instability, data loss, loss of display output, or a no-boot
condition.

| Capture | Page or subject |
|---|---|
| [![CBS warning](../screenshots/cbs-01-legal-warning.jpg)](../screenshots/cbs-01-legal-warning.jpg) | AMD's warranty and out-of-specification operation warning. |
| [![CBS CPU prefetch](../screenshots/cbs-02-cpu-prefetch-controls.jpg)](../screenshots/cbs-02-cpu-prefetch-controls.jpg) | CPU Common Options and L1/L2 stream hardware prefetch controls. |
| [![CBS CPU options](../screenshots/cbs-03-cpu-cstates-sev-controls.jpg)](../screenshots/cbs-03-cpu-cstates-sev-controls.jpg) | Additional CPU performance, power, and virtualization-related controls. |
| [![CBS fabric options](../screenshots/cbs-04-data-fabric-controls.jpg)](../screenshots/cbs-04-data-fabric-controls.jpg) | Data Fabric failure handling and downstream-device behavior. |
| [![CBS scrub options](../screenshots/cbs-05-memory-scrub-controls.jpg)](../screenshots/cbs-05-memory-scrub-controls.jpg) | UMC memory scrub mode, interval, and request-limit controls. |
| [![CBS memory mapping](../screenshots/cbs-06-memory-mapping-controls.jpg)](../screenshots/cbs-06-memory-mapping-controls.jpg) | UMC memory mapping options. |
| [![CBS memory errors](../screenshots/cbs-07-memory-error-bank-controls.jpg)](../screenshots/cbs-07-memory-error-bank-controls.jpg) | Per-bank memory error and reporting controls. |
| [![CBS ABL debug options](../screenshots/cbs-08-abl-debug-controls.jpg)](../screenshots/cbs-08-abl-debug-controls.jpg) | ABL console-output and PMU debug-message controls. |
| [![CBS FCH I/O index](../screenshots/cbs-09-fch-io-menu.jpg)](../screenshots/cbs-09-fch-io-menu.jpg) | FCH I/O index with SATA, USB, AC power-loss, I2C, UART, eSPI, and XGBE submenus. |
| [![CBS SATA options](../screenshots/cbs-10-sata-controls.jpg)](../screenshots/cbs-10-sata-controls.jpg) | SATA controller and port configuration under AMD CBS. |
| [![CBS SoC clock and voltage options](../screenshots/cbs-11-soc-fclk-vid-uclk-controls.jpg)](../screenshots/cbs-11-soc-fclk-vid-uclk-controls.jpg) | FCLK frequency, VDDR_SOC overclock VID, and UCLK divider controls. The displayed VID formula is firmware help text, not a tuning recommendation. |
| [![CBS fan control](../screenshots/cbs-12-fan-control.jpg)](../screenshots/cbs-12-fan-control.jpg) | Fan-control mode, forced PWM control, and fan-table policy. |
| [![CBS SmartShift limits](../screenshots/cbs-13-smartshift-power-limits.jpg)](../screenshots/cbs-13-smartshift-power-limits.jpg) | SmartShift/A+A support and APU-only, sustained, fast, and slow power-limit fields. |
| [![CBS system power profiles](../screenshots/cbs-14-system-configuration-por-profiles.jpg)](../screenshots/cbs-14-system-configuration-por-profiles.jpg) | System Configuration menu with 10 W through 54 W consumer/embedded POR profiles, plus Fan, temperature, STAPM, SmartShift, and CPPC submenus. The firmware itself warns that an unsupported profile may hang the system. |
| [![CBS CAD bus timing](../screenshots/cbs-15-cad-bus-timing-controls.jpg)](../screenshots/cbs-15-cad-bus-timing-controls.jpg) | CAD bus timing controls for `AddrCmdSetup`, `CsOdtSetup`, and `CkeSetup`. |
| [![CBS CAD bus drive strength](../screenshots/cbs-16-cad-bus-drive-strength.jpg)](../screenshots/cbs-16-cad-bus-drive-strength.jpg) | CAD bus drive-strength controls and visible impedance choices from 120.0 to 20.0 ohms. |
| [![CBS data bus termination](../screenshots/cbs-17-data-bus-termination-controls.jpg)](../screenshots/cbs-17-data-bus-termination-controls.jpg) | DRAM data-bus configuration with `RttNom`, `RttWr`, and `RttPark`; the open list shows the available `RZQ` termination ratios. |
| [![CBS DRAM repair and CRC](../screenshots/cbs-18-dram-repair-parity-crc-controls.jpg)](../screenshots/cbs-18-dram-repair-parity-crc-controls.jpg) | Data poisoning, post-package repair, RCD/command parity, replay limits, and write-CRC controls. |
| [![CBS DRAM ECC](../screenshots/cbs-19-dram-ecc-controls.jpg)](../screenshots/cbs-19-dram-ecc-controls.jpg) | DRAM ECC symbol size, ECC enable, and uncorrectable-error retry controls. |
| [![CBS TSME and scrambling](../screenshots/cbs-20-tsme-data-scrambling.jpg)](../screenshots/cbs-20-tsme-data-scrambling.jpg) | TSME and DRAM data-scrambling controls. |
| [![CBS memory timings](../screenshots/cbs-21-memory-overclock-timings.jpg)](../screenshots/cbs-21-memory-overclock-timings.jpg) | Memory overclock page with clock selection and primary timings including `Tcl`, `Trcdrd`, `Trcdwr`, `Trp`, and `Tras`. |
| [![CBS memory clock choices](../screenshots/cbs-22-memory-clock-options.jpg)](../screenshots/cbs-22-memory-clock-options.jpg) | Memory Clock Speed list, visibly ranging from 667 MHz to 1800 MHz. Availability does not establish hardware support. |
| [![CBS memory MBIST](../screenshots/cbs-23-memory-mbist-controls.jpg)](../screenshots/cbs-23-memory-mbist-controls.jpg) | Memory MBIST mode, aggressor test, per-bit slave-die reporting, and Data Eye controls. |
| [![CBS memory interleaving](../screenshots/cbs-24-memory-interleaving-map.jpg)](../screenshots/cbs-24-memory-interleaving-map.jpg) | Memory-channel interleaving, interleave size, and DRAM map inversion. |

## Interpretation rules

- A visible control proves only that its HII form rendered in this session.
- A displayed value is a snapshot, not a tested or recommended setting.
- The authoritative static inventory currently comes from `FCCN21WW`; consult
  [ADVANCED_OPTIONS.md](ADVANCED_OPTIONS.md) for offsets and caveats.
- The menu reveal is volatile. It does not demonstrate a modified or flashed
  firmware image.
- Further testing should remain observation-only until a verified SPI backup and
  hardware recovery path exist.

# Hidden Advanced and Runtime Option Inventory

This inventory was reconstructed from
`SetupUtility.3.0.Advanced.en-US.uefi.ifr.txt`, extracted from Lenovo's
`FCCN21WW` update for the IdeaPad Gaming 3 15ARH05. The raw IFR and firmware are
not distributed by this repository because they are vendor-derived artifacts.

> [!CAUTION]
> An IFR listing proves that a control exists in a firmware package; it does not
> prove that the installed hardware supports it or that changing it is safe.
> The test laptop currently runs `FCCN19WW`, while this inventory describes
> `FCCN21WW`. Offsets must not be written directly across BIOS versions.

## Form-set structure

| Property | Value |
|---|---|
| Advanced form-set GUID | `C6D4769E-7F48-4D2A-98E9-87ADCCF35CCC` |
| Form ID | `0x0001` |
| Primary VarStore | `SystemConfig`, ID `0x1234`, size `0x2BC` |
| Variable GUID | `A04A27F4-DF00-4D42-B552-39511302113D` |
| Secondary VarStore | `AdvanceConfig`, ID `0x1233`, size 8 |

The top page links to PCI Express, Boot Configuration, Peripheral
Configuration, IDE/SATA, NVMe, Video, USB, Chipset, ACPI, CPU, and DASH forms.
It also exposes `Above 4GB MMIO` at `SystemConfig+0x1FE`: Disabled (`0`) or
Enabled (`1`, default).

The menu has since been rendered successfully on the physical `FCCN19WW` test
machine through a runtime SREP patch. The [photo gallery](SCREENSHOTS.md) provides
visual cross-checks for these categories. This does not promote the offsets
below to `FCCN19WW` offsets; they remain an inventory extracted from `FCCN21WW`.

## Controls physically observed on FCCN19WW

The runtime session provides direct evidence that the following controls render
on the test laptop. These entries come from photographs of the running setup
utility, not from the `FCCN21WW` Advanced IFR inventory below. Consequently,
their VarStore IDs, offsets, encoded values, dependencies, and defaults remain
**unknown**.

> [!IMPORTANT]
> `Auto`, `Manual`, `Enabled`, and other values shown in a photograph describe
> that captured UI state only. Some lists were opened solely to record their
> choices. None of these states is presented as the factory default or as a safe
> configuration.

### Clocks, thermals, and platform power

| Area | Controls or choices visibly observed | Evidence |
|---|---|---|
| SoC clocks and voltage | FCLK Frequency, VDDR_SOC overclock VID, UCLK DIV1 MODE; help text states `UCLK=MEMCLK` or `MEMCLK/2` according to divider mode | [`cbs-11`](../screenshots/cbs-11-soc-fclk-vid-uclk-controls.jpg) |
| Fan policy | Fan Control, Force PWM Control, Fan Table Control | [`cbs-12`](../screenshots/cbs-12-fan-control.jpg) |
| SmartShift and limits | SmartShift Control, SmartShift/A+A enable, APU-only sPPT, sustained, fast, and slow PPT limits | [`cbs-13`](../screenshots/cbs-13-smartshift-power-limits.jpg) |
| System profiles | Fan Control, System Temperature Tracking, STAPM Control, SmartShift Control, CPPC, and selectable 10 W–54 W consumer/embedded POR profiles | [`cbs-14`](../screenshots/cbs-14-system-configuration-por-profiles.jpg) |

The System Configuration help text explicitly warns that selecting a profile
unsupported by the processor OPN can hang the system.

### DRAM electrical and reliability controls

| Area | Controls or choices visibly observed | Evidence |
|---|---|---|
| CAD timing | `AddrCmdSetup`, `CsOdtSetup`, `CkeSetup`, and manual/automatic timing policy | [`cbs-15`](../screenshots/cbs-15-cad-bus-timing-controls.jpg) |
| CAD drive strength | Clock, address/command, chip-select/ODT, and CKE drive strength; the open list visibly includes 120.0, 60.0, 40.0, 30.0, 24.0, and 20.0 ohms | [`cbs-16`](../screenshots/cbs-16-cad-bus-drive-strength.jpg) |
| Data-bus termination | `RttNom`, `RttWr`, and `RttPark`; visible `RZQ/1` through `RZQ/7` choices and disable/auto states | [`cbs-17`](../screenshots/cbs-17-data-bus-termination-controls.jpg) |
| Repair, parity, and CRC | Data Poisoning, DRAM Post Package Repair, RCD Parity, DRAM Address Command Parity Retry, parity replay limit, Write CRC, DRAM Write CRC retry, and CRC replay limit | [`cbs-18`](../screenshots/cbs-18-dram-repair-parity-crc-controls.jpg) |
| ECC | DRAM ECC Symbol Size (`x4`/`x8` per help text), DRAM ECC Enable, and DRAM UECC Retry | [`cbs-19`](../screenshots/cbs-19-dram-ecc-controls.jpg) |
| Memory protection | TSME and Data Scramble | [`cbs-20`](../screenshots/cbs-20-tsme-data-scrambling.jpg) |

### Memory tuning, testing, and topology

| Area | Controls or choices visibly observed | Evidence |
|---|---|---|
| Memory overclock | Overclock gate, Memory Clock Speed, `Tcl`, `Trcdrd`, `Trcdwr`, `Trp`, `Tras`, and additional timing fields below the photographed viewport | [`cbs-21`](../screenshots/cbs-21-memory-overclock-timings.jpg) |
| Memory clock list | `Auto` and 667–1800 MHz choices visible in the expanded selector | [`cbs-22`](../screenshots/cbs-22-memory-clock-options.jpg) |
| Memory diagnostics | MBIST Enable, Test Mode, Aggressors, Per Bit Slave Die Reporting, and Data Eye | [`cbs-23`](../screenshots/cbs-23-memory-mbist-controls.jpg) |
| Memory mapping | Memory interleaving, 256-byte through 2-Kbyte interleave sizes, and DRAM map inversion | [`cbs-24`](../screenshots/cbs-24-memory-interleaving-map.jpg) |

This physical inventory confirms the presence of extensive AMD CBS pages that
were not represented in the static `Advanced` form-set tables. It still does not
resolve the `Hybrid Graphics` control: that label was not observed in these new
captures and no offset is assigned to it.

## PCI Express

| Setting | Offset | Values; default |
|---|---:|---|
| PSPP Policy | `0x15A` | Disabled `0`, Performance `1`, Balanced High `2`, Balanced Low `3` (default), Power Saving `4`, Auto `5` |
| GPP0 | `0x15B` | Disabled `0`, Enabled `1` (default) |
| GPP1 | `0x15F` | Disabled `0`, Enabled `1` (default) |
| GPP2 | `0x163` | Disabled `0`, Enabled `1` (default) |
| GPP3 | `0x167` | Disabled `0`, Enabled `1` (default) |
| GPP4 | `0x16B` | Disabled `0`, Enabled `1` (default) |
| GPP5 | `0x16F` | Disabled `0`, Enabled `1` (default) |
| GPP6 | `0x170` | Disabled `0`, Enabled `1` (default) |

## Boot Configuration

| Setting | Offset | Values; default |
|---|---:|---|
| NumLock | `0x08` | Off `0` (default), On `1` |
| Fast Recovery | `0x17B` | Disabled `0` (default), Enabled `1` |

## Peripheral Configuration

| Setting | Offset | Values; default |
|---|---:|---|
| TPM Device | `0x100` | Disabled `0` (default), Discrete TPM `1`, Firmware TPM `2` |
| LPC/SPI TPM | `0x102` | LPC `0`, SPI `1` (default) |
| Erase fTPM NV | `0x107` | Disabled `0`, Enabled `1` (default in IFR) |
| Azalia | `0x33` | Disabled `0`, Auto `1` (default) |
| Secure biometrics camera | `0x1FF` | Disabled `0` (default), Enabled `1` |

The apparent default for `Erase fTPM NV` is especially dangerous and may be
conditional or reset-oriented. Do not interpret the table as a recommendation.

## IDE/SATA and NVMe

| Setting | Offset | Values; default |
|---|---:|---|
| SATA controller | `0x145` | Disabled `0`, Auto `1` (default) |
| Configure SATA as | `0x39` | IDE `0`, AHCI `2` (default) |
| AHCI supporting type | `0xFA` | Legacy `0` (default), UEFI `1` |
| Force RAID | `0x147` | Disabled `0` (default), Enabled `1` |
| SATA port 0 | `0x148` | Enabled `0` (default), Disabled `1` |
| SATA port 1 | `0x149` | Enabled `0` (default), Disabled `1` |

The reversed port values are exactly what the IFR reports. Additional dynamic
references exist for ports 0 through 5. An NVMe form exists, but it contains no
static controls in this IFR package.

## Video Configuration

| Setting | Offset | Values; default |
|---|---:|---|
| HDMI audio | `0x101` | Disabled `0`, Enabled `1` (default) |
| Brightness control method | `0x17E` | Video BIOS `0`, VGA driver `1` (default) |

`Hybrid Graphics` is not present in this particular Advanced IFR. It may be
provided dynamically or by a separate AMD PBS/CBS package. Its absence here is
important: a label found in another string package must not be assigned an
offset from guesswork.

## USB Configuration

| Setting | Offset | Values; default |
|---|---:|---|
| XHCI0 controller | `0x119` | Disabled `0` (default), Enabled `1` |
| USB BIOS support | `0x48` | Disabled `0`, Enabled `1` (default), UEFI-only `2` |
| USB 2.0 support | `0x47` | Disabled `0`, Enabled `1` (default) |
| Controller 0 ports 0-3 | `0x13C`-`0x13F` | Disabled `0`, Enabled `1` (default) |
| Controller 1 ports 0-3 | `0x140`-`0x143` | Disabled `0`, Enabled `1` (default) |

## Chipset and ACPI

| Setting | Offset | Values; default |
|---|---:|---|
| PCI latency timer | `0x49` | 32 through 248 PCI clocks; 64 default |
| STIBP | `0xED` | Checkbox, disabled by default |
| ACPI C2 | `0x51` | Disabled `0`, Enabled `1` (default) |
| ACPI C3 | `0x52` | Disabled `0`, Enabled `1` (default) |
| RTC wake from S4 | `0x53` | Disabled `0`, Enabled `1` (default) |
| I/O APIC | `0x54` | Disabled `0`, Enabled `1` (default) |
| HPET | `0x55` | Disabled `0`, Enabled `1` (default) |
| ACPI `_OSC` | `0x13A` | Disabled `0`, Enabled `1` (default) |

## CPU Configuration

| Setting | Offset | Values; default |
|---|---:|---|
| P-state policy | `0xF3` | Auto `0` (default), Lowest `1` |
| SVM | `0xEE` | Disabled `0` (default), Enabled `1` |
| SVM Lock | `0xEF` | Disabled `0`, Enabled `1` (default) |
| SMM Code Lock | `0x14D` | Disabled `0`, Enabled `1` (default) |

## DASH

| Setting | Offset | Values; default |
|---|---:|---|
| DASH | `0x1A9` | Disabled `0` (default), Enabled `1` |
| AMD KVM | `0x1A7` | Disabled `0` (default), Enabled `1` |

Here, `AMD KVM` refers to AMD's DASH remote keyboard/video/mouse management
feature, not the Linux Kernel-based Virtual Machine hypervisor.

## Unidentified disabled fields

The IFR contains unnamed numeric questions at `SystemConfig` offsets `0x79`,
`0x80`, and `0x81`, plus all eight bytes of `AdvanceConfig` (`0x00`-`0x07`).
They are wrapped in an always-true `DisableIf` expression. Their names and
semantics are unknown, so they must not be treated as menu-unlock variables.

## Safety classification

The highest-risk areas are display routing, SATA/RAID mode, PCIe GPP state,
PSP/fTPM and Secure Boot, SVM/SMM locks, and any unidentified field. The runtime
captures add equally sensitive fan/PWM tables, SmartShift/STAPM/PPT limits,
system POR profiles, SoC VID, FCLK/UCLK, DRAM impedance and termination, ECC/CRC,
memory timings, MBIST, and interleaving controls. Changing one of these can
prevent storage discovery, video or memory initialization, setup access, or
boot, and unsafe thermal or voltage settings may damage hardware. Testing should
remain observation-only until a verified physical SPI recovery path exists.

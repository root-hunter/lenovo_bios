# BIOS profile system

This repository packages one SREP artifact per BIOS profile. A profile may
cover several firmware versions when they use the same verified runtime
visibility patterns. It is not tied to the SHA-256 hash of one complete ROM.

## Compatibility and evidence are different

Compatibility is based on the platform, loaded module, setup application, and
the exact search/replacement patterns in `SREP_Config.cfg`. Hashes in
`profile.json` identify files used during research so that the analysis can be
reproduced. They are evidence, not runtime allow-list entries.

Useful evidence types include:

| Type | File identified | Purpose |
|---|---|---|
| `vendor-updater` | Original vendor download | Source provenance |
| `firmware-container` | `BIOS.fd` or equivalent | Reproduce unpacking |
| `extracted-update-rom` | Normalized ROM image | Identify static analysis input |
| `uefi-module` | Extracted `H2OFormBrowserDxe` | Identify the exact patch target studied |

Do not commit vendor firmware or extracted modules. Record only metadata and
hashes for legitimately obtained local files.

## Profile layout

Each directory directly under `profiles/` contains:

```text
profiles/<profile-id>/
├── profile.json
├── SREP_Config.cfg
└── README.txt
```

The directory name and manifest `id` must match. IDs contain lowercase letters,
digits, and hyphens so they are safe to use in release filenames.

The current manifest schema is:

```json
{
  "schema_version": 1,
  "id": "vendor-model-bios-family",
  "display_name": "Human-readable platform and BIOS family",
  "platform": {
    "manufacturer": "Vendor",
    "machine_types": ["machine-type"],
    "product_names": ["firmware-product-string"]
  },
  "compatibility": {
    "bios_family": "FAMILY",
    "analyzed_versions": ["VERSION1"],
    "hardware_tested_versions": []
  },
  "patch": {
    "module": "H2OFormBrowserDxe",
    "launcher": "SetupUtilityApp"
  },
  "status": "firmware-verified",
  "config": "SREP_Config.cfg",
  "readme": "README.txt",
  "evidence": [
    {
      "bios_version": "VERSION1",
      "file": "descriptive-local-filename.rom",
      "type": "extracted-update-rom",
      "sha256": "64-lowercase-hexadecimal-digits"
    }
  ]
}
```

Profile status has a precise meaning:

| Status | Meaning |
|---|---|
| `generated` | Candidate patterns exist but have not been confirmed in extracted firmware |
| `firmware-verified` | Patterns and targets were verified in the listed firmware artifacts |
| `hardware-tested` | At least one listed BIOS version was successfully tested on physical hardware |
| `deprecated` | The profile is retained for history and should not be used for new tests |

## Adding another BIOS

1. Create a new profile directory; do not modify a working profile to include
   an unrelated platform or firmware family.
2. Extract the new firmware and locate its own `H2OFormBrowserDxe`, setup
   application, HII packages, and form-set GUIDs.
3. Confirm every original pattern in the extracted target module and establish
   that the match is unique. Do not infer patterns from a BIOS family prefix.
4. Add analyzed versions and hashes as evidence. A hash identifies the exact
   file analyzed but does not limit the profile to that file.
5. Start at `firmware-verified` only after static verification. Add a version to
   `hardware_tested_versions` and promote the status only after a successful,
   observation-only physical test.
6. Preserve the resulting `SREP.log`. Do not commit firmware, machine-specific
   dumps, or logs containing identifiers.

The validator checks manifest structure and the safety shape of the current
visibility patches: every pair must preserve the 16-byte GUID and change only
the following 32-bit value from zero to one. Run it with:

```bash
python3 scripts/profile_tool.py validate profiles/*
```

This is a structural repository check. It cannot prove that a byte pattern is
unique in a firmware module that is not included in the repository. That check
must be performed during analysis and recorded as evidence.

## Building profiles

Build the default, physically tested profile:

```bash
scripts/build_srep_latest.sh
```

Build one named profile:

```bash
scripts/build_srep_latest.sh /tmp/srep-build dist vendor-model-bios-family
```

Build every valid profile while compiling SREP only once:

```bash
scripts/build_srep_latest.sh /tmp/srep-build dist all
```

Each output filename includes its profile ID. `SHA256SUMS` covers every image
and ZIP in the output directory; `BUILD-INFO.txt` records the packaged profile
IDs and build revisions.

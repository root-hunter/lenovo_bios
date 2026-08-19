# BIOS strategies and profiles

The project separates a reusable firmware mechanism from compatibility claims
about individual machines:

```text
Strategy: how a firmware family can be patched
    └── Profile: where that strategy was analyzed or physically tested
            └── Evidence: exact local files used during the research
```

The first implemented strategy targets the InsydeH2O form-set visibility table.
It describes records made from a UEFI GUID followed by a little-endian 32-bit
visibility value. Changing that value from zero to one can reveal a form set in
the tested environment.

This does not claim that every Lenovo or every InsydeH2O release has the same
module, record layout, GUIDs, launcher, or runtime behavior. A profile makes
those narrower claims and records their verification level.

## Strategy definitions

Reusable mechanisms live under `strategies/`. The current definition is:

```text
strategies/insyde-h2o-formset-visibility.json
```

It records:

- the firmware vendor and family;
- the GUID and visibility-field encoding;
- hidden and shown values;
- known module and Setup launcher candidates;
- the upstream SREP revision documenting the mechanism.

The form-list structure, GUID byte encoding, and mappings for AMD PBS, AMD CBS,
Power, and Advanced are also documented in the
[SmokeyCPU reverse-engineering notes](https://www.stanto.com/files/SmokeyCPU-DecExt.pdf).

A strategy definition is not a list of compatible computers. Adding a module
or launcher candidate means only that the renderer understands that target; it
does not validate a particular BIOS.

## Profile layout

Each directory directly under `profiles/` contains:

```text
profiles/<profile-id>/
├── profile.json       Semantic source of truth
├── SREP_Config.cfg    Deterministically generated output
└── README.txt         Safety and machine-specific instructions
```

The directory name and manifest `id` must match. IDs contain lowercase letters,
digits, and hyphens so they can safely form part of release filenames.

The schema version 2 structure is:

```json
{
  "schema_version": 2,
  "id": "vendor-model-bios-family",
  "display_name": "Human-readable platform and BIOS family",
  "platform": {
    "manufacturer": "Computer vendor",
    "machine_types": ["machine-type"],
    "product_names": ["SMBIOS-product-string"]
  },
  "firmware": {
    "vendor": "Insyde",
    "family": "InsydeH2O",
    "architecture": "x86_64"
  },
  "compatibility": {
    "bios_family": "FAMILY",
    "analyzed_versions": ["VERSION1"],
    "hardware_tested_versions": []
  },
  "strategy": "insyde-h2o-formset-visibility",
  "targets": {
    "module": "H2OFormBrowserDxe",
    "launcher": "SetupUtilityApp"
  },
  "form_sets": [
    {
      "guid": "00000000-0000-0000-0000-000000000000",
      "name": "Name recovered from IFR or other evidence",
      "required": true,
      "provenance": "where-this-mapping-was-established"
    }
  ],
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

GUIDs are written in canonical uppercase form. The generator converts their
UEFI fields to the correct byte order and appends the visibility value. Raw hex
patterns are therefore generated output rather than manually maintained input.

All form sets are currently required. Optional patch behavior must not be
declared until its failure semantics have been verified in the pinned SREP
implementation.

## Compatibility and evidence

Compatibility is based on the platform, selected strategy and targets, verified
form-set GUIDs, and test results. A BIOS family prefix by itself is insufficient.

Hashes identify the exact files used during research:

| Evidence type | File identified | Purpose |
|---|---|---|
| `vendor-updater` | Original vendor download | Source provenance |
| `firmware-container` | `BIOS.fd` or equivalent | Reproduce unpacking |
| `extracted-update-rom` | Normalized ROM image | Identify static analysis input |
| `uefi-module` | Extracted form-browser module | Identify the exact patch target studied |

They are not runtime allow-list entries. A different ROM or module hash may
remain compatible if the relevant structure and patterns are independently
verified. Do not commit vendor firmware, extracted modules, or machine-specific
dumps; retain only their metadata and hashes.

Profile status has a precise meaning:

| Status | Meaning |
|---|---|
| `generated` | Candidate metadata exists but has not been confirmed in extracted firmware |
| `firmware-verified` | Targets, structure, and form-set patterns were verified statically |
| `hardware-tested` | At least one listed BIOS version was successfully tested on physical hardware |
| `deprecated` | The profile is retained for history and should not be used for new tests |

## Adding another InsydeH2O BIOS

1. Create a new profile instead of widening an unrelated platform profile.
2. Extract the firmware and identify its form-browser module, Setup launcher,
   HII packages, and form-set GUIDs.
3. Confirm that the strategy's `GUID + uint32 visibility` record really exists
   in that module. Do not infer this only from the InsydeH2O branding.
4. Confirm every hidden pattern and establish its number of occurrences in the
   extracted target. Record names only when IFR or another stated source proves
   the GUID-to-name mapping.
5. Add hashes as research evidence, generate the configuration, and validate the
   complete profile.
6. Start at `firmware-verified` only after static verification. Promote it to
   `hardware-tested` only after a successful observation-only physical test.
7. Preserve `SREP.log`, removing machine identifiers before publishing it.

If the module name, launcher, or record layout differs, first determine whether
this is a new candidate for the existing strategy or a genuinely different
strategy. Do not force an incompatible firmware into the current renderer.

## Generation and validation

Regenerate the tracked SREP configuration after editing semantic fields:

```bash
python3 scripts/profile_tool.py sync profiles/vendor-model-bios-family
```

Inspect the generated configuration without writing it:

```bash
python3 scripts/profile_tool.py render profiles/vendor-model-bios-family
```

Validate all profiles:

```bash
python3 scripts/profile_tool.py validate profiles/*
```

Validation checks schema versions, strategy/firmware agreement, allowed target
names, canonical and unique GUIDs, evidence hashes, status consistency, safe
profile filenames, and exact byte-for-byte correspondence between the semantic
manifest and `SREP_Config.cfg`.

It cannot prove uniqueness inside a proprietary module that is not present in
the repository. That remains an analysis step whose result must be recorded as
profile evidence.

## Building profiles

Build the default physically tested profile:

```bash
scripts/build_srep_latest.sh
```

Build one named profile:

```bash
scripts/build_srep_latest.sh /tmp/srep-build dist vendor-model-bios-family
```

Build every validated profile while compiling SREP only once:

```bash
scripts/build_srep_latest.sh /tmp/srep-build dist all
```

Each output filename contains its profile ID. `SHA256SUMS` covers every image
and ZIP in the output directory, while `BUILD-INFO.txt` records the selected
profiles and source revisions.

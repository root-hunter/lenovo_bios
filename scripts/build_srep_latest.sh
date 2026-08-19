#!/usr/bin/env bash

set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd -- "$script_dir/.." && pwd)

edk2_ref=${EDK2_REF:-edk2-stable202605}
srep_ref=${SREP_REF:-83d0ae47c9a48b3a2227aef06fb98a372c5ba354}
expected_edk2_commit=${EDK2_COMMIT:-}
build_root=${1:-/tmp/lenovo-srep-latest-build}
output_dir=${2:-$repo_root/artifacts/releases/latest-edk2}

for command_name in file git make nasm python3; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "Required command not found: $command_name" >&2
    exit 1
  }
done

mkdir -p "$build_root" "$output_dir"
build_root=$(cd -- "$build_root" && pwd)
output_dir=$(cd -- "$output_dir" && pwd)
edk2_dir="$build_root/edk2"
srep_dir="$edk2_dir/SmokelessRuntimeEFIPatcher"

if [[ ! -d "$edk2_dir/.git" ]]; then
  git clone --branch "$edk2_ref" --depth 1 \
    https://github.com/tianocore/edk2.git "$edk2_dir"
else
  git -C "$edk2_dir" fetch --depth 1 origin "$edk2_ref"
  git -C "$edk2_dir" checkout --detach FETCH_HEAD
fi

edk2_commit=$(git -C "$edk2_dir" rev-parse HEAD)
if [[ -n "$expected_edk2_commit" && "$edk2_commit" != "$expected_edk2_commit" ]]; then
  echo "Unexpected EDK II commit: $edk2_commit" >&2
  echo "Expected EDK II commit:   $expected_edk2_commit" >&2
  exit 1
fi

# BaseTools and MdeModulePkg reference Brotli; CryptoPkg declares OpenSSL and
# MbedTLS include paths; MdePkg references MipiSysT headers. Fetch only these
# dependencies instead of every EDK II test/tool submodule.
git -C "$edk2_dir" submodule update --init --depth 1 \
  BaseTools/Source/C/BrotliCompress/brotli \
  CryptoPkg/Library/OpensslLib/openssl \
  CryptoPkg/Library/MbedTlsLib/mbedtls \
  MdePkg/Library/MipiSysTLib/mipisyst \
  MdeModulePkg/Library/BrotliCustomDecompressLib/brotli

if [[ ! -d "$srep_dir/.git" ]]; then
  git clone https://github.com/barlowhaydnb/SmokelessRuntimeEFIPatcher.git \
    "$srep_dir"
fi

git -C "$srep_dir" fetch --depth 1 origin "$srep_ref"
git -C "$srep_dir" checkout --detach FETCH_HEAD
git -C "$srep_dir" restore --source=HEAD --staged --worktree .
git -C "$srep_dir" apply "$repo_root/patches/srep-edk2-stable202605.patch"

make -C "$edk2_dir/BaseTools" -j"$(nproc)"

(
  cd -- "$edk2_dir"
  # Pass an explicit, supported argument: sourced scripts otherwise inherit
  # this wrapper's positional parameters and edksetup.sh rejects them. EDK II's
  # setup also probes variables before defining them, so nounset must be paused.
  set +u
  . ./edksetup.sh BaseTools
  set -u
  build -b RELEASE -t GCC \
    -p SmokelessRuntimeEFIPatcher/SmokelessRuntimeEFIPatcher.dsc \
    -a X64 -s
)

efi_path="$edk2_dir/Build/SmokelessRuntimeEFIPatcher/RELEASE_GCC/X64/SmokelessRuntimeEFIPatcher.efi"
[[ -s "$efi_path" ]] || { echo "EFI build output not found: $efi_path" >&2; exit 1; }

file "$efi_path"
file "$efi_path" | grep -E 'PE32\+.*EFI.*application.*x86-64'

srep_commit=$(git -C "$srep_dir" rev-parse HEAD)
version=${ARTIFACT_VERSION:-"${edk2_ref}-${edk2_commit:0:12}"}

"$repo_root/scripts/package_srep_usb.sh" \
  "$efi_path" \
  "$repo_root/configs/srep/15ARH05-FCCN21WW.cfg" \
  "$output_dir" \
  "$version"

{
  echo "Status: source revisions boot-tested on Lenovo 15ARH05; this artifact requires observation-only verification"
  echo "EDK II ref: $edk2_ref"
  echo "EDK II commit: $edk2_commit"
  echo "SREP commit: $srep_commit"
  echo "Compiler: $(gcc --version | head -n 1)"
  echo "Python: $(python3 --version)"
  echo "EFI SHA-256: $(sha256sum "$efi_path" | awk '{print $1}')"
  echo "Repository commit: ${GITHUB_SHA:-local working tree}"
  echo "Runner: ${RUNNER_OS:-local} ${RUNNER_ARCH:-$(uname -m)}"
} > "$output_dir/BUILD-INFO.txt"

(
  cd -- "$output_dir"
  sha256sum BUILD-INFO.txt >> SHA256SUMS
  sha256sum --check SHA256SUMS
)

echo "Latest EDK II image is ready in: $output_dir"

#!/usr/bin/env python3
"""Apply the minimal, reproducible Dimm identity overlay to the pinned Skyline source."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_exact(path: Path, old: str, new: str) -> None:
    if not path.is_file():
        raise SystemExit(f"Required upstream file is missing: {path}")
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Expected exactly one occurrence in {path}: {old!r}; found {count}. "
            "The pinned upstream source changed; review the overlay before continuing."
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("vendor/skyline-upstream"),
        help="Path to the pinned Skyline Git submodule",
    )
    args = parser.parse_args()
    root = args.source.resolve()

    gradle = root / "app/build.gradle"
    strings = root / "app/src/main/res/values/strings.xml"
    emulation = root / "app/src/main/java/emu/skyline/EmulationActivity.kt"

    # Keep namespace emu.skyline unchanged: the native library exports JNI symbols
    # using these exact package/class names. Only the Android application ID changes.
    replace_exact(gradle, 'applicationId "skyline.emu"', 'applicationId "com.dimm.skyline"')
    replace_exact(gradle, "versionCode 3", "versionCode 4")
    replace_exact(gradle, 'versionName "0.0.3"', 'versionName "0.2.0-dimm"')
    # The upstream project intentionally ships a debuggable release. Disable this
    # for the Dimm candidate so the release APK is not debuggable.
    replace_exact(gradle, 'release {\n            debuggable true', 'release {\n            debuggable false')
    replace_exact(
        gradle,
        'manifestPlaceholders += [appLabel: "Skyline"]',
        'manifestPlaceholders += [appLabel: "Skyline Dimm"]',
    )
    replace_exact(
        strings,
        '<string name="app_name" translatable="false">Skyline</string>',
        '<string name="app_name" translatable="false">Skyline Dimm</string>',
    )
    replace_exact(
        emulation,
        'putExtra("package_name", "skyline.emu")',
        'putExtra("package_name", "com.dimm.skyline")',
    )

    # Guard the JNI and device ABI contract against accidental overlay changes.
    gradle_text = gradle.read_text(encoding="utf-8")
    if "namespace 'emu.skyline'" not in gradle_text:
        raise SystemExit("JNI namespace emu.skyline was unexpectedly changed.")
    if 'abiFilters "arm64-v8a"' not in gradle_text:
        raise SystemExit("Expected ARM64-only native ABI configuration was changed.")
    if 'release {\n            debuggable false' not in gradle_text:
        raise SystemExit("Release build must have debuggable=false.")

    print("Dimm identity overlay applied successfully.")
    print("Changed: app/build.gradle")
    print("Changed: app/src/main/res/values/strings.xml")
    print("Changed: app/src/main/java/emu/skyline/EmulationActivity.kt")
    print("Preserved JNI namespace: emu.skyline")
    print("Application ID: com.dimm.skyline")
    print("Release debuggable: false")


if __name__ == "__main__":
    main()

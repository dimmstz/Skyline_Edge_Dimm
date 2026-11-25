# Changelog

All notable project changes are documented here.

## [0.1.0-reconstruction] - 2026-11-25

### Added
- Initial Android reconstruction scaffold for Skyline Dimm.
- APK extraction and reverse-engineering inventory documentation.
- Android CI workflow for debug APK, release APK and AAB builds.
- APK/AAB validation, SHA-256 checksums and downloadable Actions artifacts.
- Optional release signing through GitHub Actions Secrets.
- Manual and tag-triggered GitHub Release publishing.

### Fixed
- Android SDK setup no longer attempts to install the obsolete `tools` package.
- CI installs or locates Android command-line tools explicitly and verifies SDK API 35 / Build Tools 35.0.0.

### Known limitations
- This version is a minimal Android shell, not a working Skyline emulator reconstruction.
- Original DEX and native library behavior have not yet been fully recovered.
- Release outputs remain unsigned until stable signing secrets are configured.

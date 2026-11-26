# Third-party video decoder notices

The Host1x NVDEC/VIC implementation in `third_party/strato-video/` is vendored from:

- Repository: https://github.com/LukeValen/Strato-Mali-Public-Build
- Pinned source commit: `9249ea351ad7bd7b0e7d4a319e1ad1c56dae865c`\n- Skyline base used by CI: https://github.com/im030/skyline-emu at `35fb874a42cb548cbd3d66a00d65e4b2a4c1516b`
- Original upstream ancestry: Strato / Skyline, with decoder and VIC implementation derived from Eden and yuzu.
- License for the decoder/runtime implementation: GPL-3.0-or-later.
- FFmpeg: version 6.1.2, built as a static Android arm64 library with H.264, VP8 and VP9 decoders/parsers enabled.

The integration keeps the original Skyline Host1x command FIFO and adds a small adapter that routes NVDEC/VIC register writes to the decoder runtime and guest SMMU memory.

Original Skyline files retain their original SPDX copyright and MPL-2.0 notices. The GPL-3.0-or-later portions retain their own SPDX notices. See `LICENSE-GPL-3.0.txt` and `LICENSE-MPL-2.0.txt`.

## Functional scope and limitations

- Implemented decode paths: H.264, VP8 and VP9 through FFmpeg.
- Implemented VIC output paths include progressive single-slot composition to RGBA/BGRA/XRGB and NV12, with pitch-linear and supported block-linear surfaces.
- The current imported VIC implementation does not implement multiple-slot alpha composition, interlaced output, transpose, or every VIC pixel/layout mode.
- AV1 is not enabled in this Android build.
- A successful native build is not proof that Resident Evil 4's prerecorded campaign movies render correctly. Device validation must confirm the actual game's codec, register sequence, surface layout, and presentation path.

The integration is pinned and applied only to the temporary upstream Skyline checkout used by CI; it does not rewrite or replace the protected backup branch.

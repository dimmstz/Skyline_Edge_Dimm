#!/usr/bin/env python3
"""Apply the pinned Skyline-compatible Host1x NVDEC/VIC implementation."""
from pathlib import Path
import shutil
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_video_decoder.py <skyline-source-root>")

project = Path(__file__).resolve().parents[1]
root = Path(sys.argv[1]).resolve()
cpp = root / "app/src/main/cpp"
vendor = project / "third_party/strato-video"
integration = project / "third_party/strato-video-integration"
soc = cpp / "skyline/soc"
host = soc / "host1x"

required = [
    root / "app/CMakeLists.txt",
    soc / "host1x.h",
    host / "command_fifo.h",
    host / "command_fifo.cpp",
    host / "classes/nvdec.cpp",
    host / "classes/nvdec.h",
    host / "classes/vic.cpp",
    host / "classes/vic.h",
]
for path in required:
    if not path.is_file():
        raise SystemExit(f"Expected Skyline source file is missing: {path}")

video_files = list(vendor.rglob("*"))
if not any(p.is_file() for p in video_files):
    raise SystemExit("Vendored video decoder source is missing")
target_video = host / "video"
shutil.copytree(vendor, target_video, dirs_exist_ok=True)

test_vendor = project / "third_party/strato-video-tests"
test_target = root / "tests"
test_target.mkdir(parents=True, exist_ok=True)
for name in ["test_video_pipeline.py", "test_video_completion.py", "video_pipeline_test.cpp"]:
    source = test_vendor / name
    if not source.is_file():
        raise SystemExit(f"Vendored video regression test is missing: {source}")
    shutil.copy2(source, test_target / name)

for name, destination in [
    ("nvdec.cpp", host / "classes/nvdec.cpp"),
    ("nvdec.h", host / "classes/nvdec.h"),
    ("vic.cpp", host / "classes/vic.cpp"),
    ("vic.h", host / "classes/vic.h"),
    ("tegra_host_interface.h", host / "tegra_host_interface.h"),
    ("host1x.cpp", cpp / "skyline/soc/host1x.cpp"),
]:
    source = integration / name
    if not source.is_file():
        raise SystemExit(f"Vendored integration file is missing: {source}")
    shutil.copy2(source, destination)

def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Refusing ambiguous patch in {path}: expected one match, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

host_header = soc / "host1x.h"
replace_once(host_header,
    '#include "host1x/command_fifo.h"',
    '#include "host1x/command_fifo.h"\n#include "host1x/video/runtime.h"')
replace_once(host_header,
    '        SyncpointSet syncpoints;\n        std::array<ChannelCommandFifo, ChannelCount> channels;\n\n        Host1x(const DeviceState &state) : channels{util::MakeFilledArray<ChannelCommandFifo, ChannelCount>(state, syncpoints)} {}',
    '        strato::video::Runtime video;\n        SyncpointSet syncpoints;\n        std::array<ChannelCommandFifo, ChannelCount> channels;\n\n        Host1x(const DeviceState &state);')

fifo_header = host / "command_fifo.h"
replace_once(fifo_header,
    '        CircularQueue<span<u32>> gatherQueue;',
    '        CircularQueue<span<u32>> gatherQueue;\n        unsigned videoChannel;')
replace_once(fifo_header,
    '        ChannelCommandFifo(const DeviceState &state, SyncpointSet &syncpoints);',
    '        ChannelCommandFifo(const DeviceState &state, SyncpointSet &syncpoints, strato::video::Runtime &video);')

fifo_source = host / "command_fifo.cpp"
replace_once(fifo_source,
    '    ChannelCommandFifo::ChannelCommandFifo(const DeviceState &state, SyncpointSet &syncpoints) : state(state), gatherQueue(GatherQueueSize), host1XClass(syncpoints), nvDecClass(syncpoints), vicClass(syncpoints) {}',
    '    ChannelCommandFifo::ChannelCommandFifo(const DeviceState &state, SyncpointSet &syncpoints, strato::video::Runtime &video) : state(state), gatherQueue(GatherQueueSize), videoChannel(video.ReserveChannel()), host1XClass(syncpoints), nvDecClass(syncpoints, video, videoChannel), vicClass(syncpoints, video, videoChannel) {}')

cmake = root / "app/CMakeLists.txt"
replace_once(cmake,
    '# Skyline\nadd_library(skyline SHARED',
    '# Skyline Host1x video decode (NVDEC + VIC, FFmpeg H.264/VP8/VP9)\nadd_subdirectory(${source_DIR}/skyline/soc/host1x/video)\n\n# Skyline\nadd_library(skyline SHARED')
replace_once(cmake,
    '        ${source_DIR}/skyline/soc/smmu.cpp\n',
    '        ${source_DIR}/skyline/soc/smmu.cpp\n        ${source_DIR}/skyline/soc/host1x.cpp\n')
needle = 'target_link_libraries_system(skyline '
text = cmake.read_text(encoding="utf-8")
line = next((line for line in text.splitlines() if line.startswith(needle)), None)
if line is None or "strato_video" in line:
    raise SystemExit("Could not safely locate Skyline target link line")
cmake.write_text(text.replace(line, line + " strato_video", 1), encoding="utf-8")

print("Applied Host1x NVDEC/VIC video decoder integration.")
print("Enabled FFmpeg H.264, VP8 and VP9 decode plus VIC surface composition.")

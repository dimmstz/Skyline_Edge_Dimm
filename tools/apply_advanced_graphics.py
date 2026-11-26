#!/usr/bin/env python3
"""Patch the pinned Strato/Skyline source with Dimm graphics controls and VIC fixes."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_advanced_graphics.py <strato-source-root>")

root = Path(sys.argv[1]).resolve()

def edit(relative: str, replacements: list[tuple[str, str]]) -> None:
    path = root / relative
    if not path.is_file():
        raise SystemExit(f"Required source file missing: {relative}")
    data = path.read_text(encoding="utf-8")
    for old, new in replacements:
        count = data.count(old)
        if count != 1:
            raise SystemExit(f"{relative}: expected one exact patch anchor, found {count}: {old[:100]!r}")
        data = data.replace(old, new, 1)
    path.write_text(data, encoding="utf-8")

# Keep Strato's native Kotlin/JNI namespace intact; only change install identity.
edit("app/build.gradle", [
    ('applicationId "com.lukevalen.stratomali"', 'applicationId "com.dimm.skyline"'),
    ("buildConfigField 'String', 'RELEASE_VERSION', '\"0.0.4-1\"'",
     "buildConfigField 'String', 'RELEASE_VERSION', '\"0.1.59-advanced\"'"),
    ("versionCode getGitVersionCode()", "versionCode 73"),
    ('versionName "0.0.4-1"', 'versionName "0.1.59-advanced"'),
])

edit("app/src/main/res/values/strings.xml", [
    ('<string name="app_name" translatable="false">Strato Mali</string>',
     '<string name="app_name" translatable="false">Skyline Dimm</string>')
])

# Existing real Vulkan internal-resolution scaling is already implemented by this pinned source.
# Add per-game/global sampler controls, passed all the way from Android preferences to Vulkan.
edit("app/src/main/java/org/stratoemu/strato/settings/EmulationSettings.kt", [
    ("    var resolutionScale by sharedPreferences(context, 2, prefName = prefName)\n",
     "    var resolutionScale by sharedPreferences(context, 2, prefName = prefName)\n"
     "    var mipmapLodBias by sharedPreferences(context, 0, prefName = prefName) // quarter mip levels\n"
     "    var maxAnisotropy by sharedPreferences(context, 0, prefName = prefName) // 0 = game default\n")
])

edit("app/src/main/java/org/stratoemu/strato/settings/NativeSettings.kt", [
    ("    var resolutionScale : Int = 2\n",
     "    var resolutionScale : Int = 2,\n"
     "    var mipmapLodBias : Int = 0,\n"
     "    var maxAnisotropy : Int = 0\n"),
    ("        pref.resolutionScale\n",
     "        pref.resolutionScale,\n"
     "        pref.mipmapLodBias,\n"
     "        pref.maxAnisotropy\n")
])

edit("app/src/main/cpp/skyline/common/settings.h", [
    ("        Setting<int> resolutionScale; //!< Internal render scale index; 2 is native\n",
     "        Setting<int> resolutionScale; //!< Internal render scale index; 2 is native\n"
     "        Setting<int> mipmapLodBias; //!< Additional sampler LOD bias in quarter-mip units\n"
     "        Setting<int> maxAnisotropy; //!< 0 keeps the game's sampler anisotropy\n")
])

edit("app/src/main/cpp/skyline/common/android_settings.h", [
    ('            resolutionScale = ktSettings.GetInt<int>("resolutionScale");\n',
     '            resolutionScale = ktSettings.GetInt<int>("resolutionScale");\n'
     '            mipmapLodBias = ktSettings.GetInt<int>("mipmapLodBias");\n'
     '            maxAnisotropy = ktSettings.GetInt<int>("maxAnisotropy");\n')
])

edit("app/src/main/cpp/skyline/gpu.h", [
    ("        const resolution::Scale resolutionScale; //!< Fixed for this emulation session\n",
     "        const resolution::Scale resolutionScale; //!< Fixed for this emulation session\n"
     "        int MipmapLodBias() const;\n"
     "        int MaxAnisotropy() const;\n")
])

edit("app/src/main/cpp/skyline/gpu.cpp", [
    ("namespace skyline::gpu {\n",
     "namespace skyline::gpu {\n"
     "    int GPU::MipmapLodBias() const { return *state.settings->mipmapLodBias; }\n"
     "    int GPU::MaxAnisotropy() const { return *state.settings->maxAnisotropy; }\n")
])

edit("app/src/main/cpp/skyline/gpu/interconnect/common/samplers.cpp", [
    ('#include <soc/gm20b/channel.h>\n', '#include <algorithm>\n#include <soc/gm20b/channel.h>\n'),
    ('            auto maxAnisotropy{texSampler.MaxAnisotropy()};\n',
     '            auto maxAnisotropy{texSampler.MaxAnisotropy()};\n'
     '            const auto requestedAnisotropy{ctx.gpu.MaxAnisotropy()};\n'
     '            const auto deviceLimits{ctx.gpu.vkPhysicalDevice.getProperties().limits};\n'
     '            if (requestedAnisotropy > 0)\n'
     '                maxAnisotropy = std::min(static_cast<float>(requestedAnisotropy), deviceLimits.maxSamplerAnisotropy);\n'
     '            const auto mipLodBias{std::clamp(texSampler.MipLodBias() +\n'
     '                static_cast<float>(ctx.gpu.MipmapLodBias()) * 0.25f,\n'
     '                -deviceLimits.maxSamplerLodBias, deviceLimits.maxSamplerLodBias)};\n'),
    ('                    .mipLodBias = texSampler.MipLodBias(),\n',
     '                    .mipLodBias = mipLodBias,\n')
])

edit("app/src/main/java/org/stratoemu/strato/settings/GlobalSettingsFragment.kt", [
    ('        "executor_flush_threshold", "use_direct_memory_import", "force_max_gpu_clocks", "free_guest_texture_memory",\n',
     '        "executor_flush_threshold", "use_direct_memory_import", "force_max_gpu_clocks", "free_guest_texture_memory",\n'
     '        "mipmap_lod_bias", "max_anisotropy",\n')
])

edit("app/src/main/res/xml/emulation_preferences.xml", [
    ('        <SwitchPreferenceCompat\n            android:defaultValue="true"\n            android:summaryOff="@string/triple_buffering_disabled"',
     '        <org.stratoemu.strato.preference.IntegerListPreference\n'
     '            android:defaultValue="0"\n'
     '            android:entries="@array/mipmap_lod_bias_entries"\n'
     '            android:entryValues="@array/mipmap_lod_bias_values"\n'
     '            android:summary="@string/mipmap_lod_bias_desc"\n'
     '            app:key="mipmap_lod_bias"\n'
     '            app:refreshRequired="true"\n'
     '            app:title="@string/mipmap_lod_bias"\n'
     '            app:useSimpleSummaryProvider="true" />\n'
     '        <org.stratoemu.strato.preference.IntegerListPreference\n'
     '            android:defaultValue="0"\n'
     '            android:entries="@array/max_anisotropy_entries"\n'
     '            android:entryValues="@array/max_anisotropy_values"\n'
     '            android:summary="@string/max_anisotropy_desc"\n'
     '            app:key="max_anisotropy"\n'
     '            app:refreshRequired="true"\n'
     '            app:title="@string/max_anisotropy"\n'
     '            app:useSimpleSummaryProvider="true" />\n'
     '        <SwitchPreferenceCompat\n            android:defaultValue="true"\n            android:summaryOff="@string/triple_buffering_disabled"')
])

resources = root / "app/src/main/res/values/dimm_advanced_graphics.xml"
if resources.exists():
    raise SystemExit("Refusing to overwrite app/src/main/res/values/dimm_advanced_graphics.xml")
resources.write_text("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="mipmap_lod_bias">Mipmap LOD bias</string>
    <string name="mipmap_lod_bias_desc">Positive values select lower-resolution mip levels at distance and can reduce texture bandwidth. Negative values sharpen distant textures but may cause shimmering. Restart the game after changing.</string>
    <string-array name="mipmap_lod_bias_entries" translatable="false">
        <item>-1.00 (sharper)</item>
        <item>-0.75</item>
        <item>-0.50</item>
        <item>-0.25</item>
        <item>0 (game default)</item>
        <item>+0.25</item>
        <item>+0.50</item>
        <item>+0.75</item>
        <item>+1.00</item>
        <item>+1.25</item>
        <item>+1.50</item>
        <item>+1.75</item>
        <item>+2.00 (more blur)</item>
    </string-array>
    <integer-array name="mipmap_lod_bias_values">
        <item>-4</item><item>-3</item><item>-2</item><item>-1</item><item>0</item>
        <item>1</item><item>2</item><item>3</item><item>4</item><item>5</item>
        <item>6</item><item>7</item><item>8</item>
    </integer-array>
    <string name="max_anisotropy">Anisotropic filtering override</string>
    <string name="max_anisotropy_desc">Overrides game-provided texture anisotropy when supported by the GPU. Higher values can improve angled surfaces but may cost performance. Restart the game after changing.</string>
    <string-array name="max_anisotropy_entries" translatable="false">
        <item>Game default</item><item>1x</item><item>2x</item><item>4x</item><item>8x</item><item>16x (device-limited)</item>
    </string-array>
    <integer-array name="max_anisotropy_values">
        <item>0</item><item>1</item><item>2</item><item>4</item><item>8</item><item>16</item>
    </integer-array>
</resources>
""", encoding="utf-8")

# Resolve the decoded frame by its exact guest surface address. The previous FIFO-only
# lookup could present a different frame when decode and VIC presentation got out of step.
edit("app/src/main/cpp/skyline/soc/host1x/video/video_core/host1x/host1x.h", [
    ("#include <deque>\n", "#include <deque>\n"),
    ("""    std::shared_ptr<FFmpeg::Frame> GetFrame(s32 fd, u64 offset) {
        if (fd != -1) {
            std::scoped_lock l{m_mutex};
            if (auto const it = m_frame_devices.find(fd); it != m_frame_devices.end()) {
                if (it->second.m_presentation_order.size() > 0)
                    return GetPresentOrderLocked(fd);
                if (it->second.m_decode_order.size() > 0)
                    return GetDecodeOrderLocked(fd, offset);
            }
        }
        return {};
    }

private:
    std::shared_ptr<FFmpeg::Frame> GetPresentOrderLocked(s32 fd) {
        if (auto const it = m_frame_devices.find(fd); it != m_frame_devices.end()) {
            auto frame = std::move(it->second.m_presentation_order.front().second);
            it->second.m_presentation_order.pop_front();
            return frame;
        }
        return {};
    }

    std::shared_ptr<FFmpeg::Frame> GetDecodeOrderLocked(s32 fd, u64 offset) {
        if (auto const it = m_frame_devices.find(fd); it != m_frame_devices.end()) {
            if (auto const it2 = it->second.m_decode_order.find(offset); it2 != it->second.m_decode_order.end()) {
                // TODO: this "mapped" prevents us from fully embracing ankerl
                return std::move(it->second.m_decode_order.extract(it2).mapped());
            }
        }
        return {};
    }
""",
"""    std::shared_ptr<FFmpeg::Frame> GetFrame(s32 fd, u64 offset) {
        if (fd == -1)
            return {};
        std::scoped_lock l{m_mutex};
        const auto device = m_frame_devices.find(fd);
        if (device == m_frame_devices.end())
            return {};
        auto& frames = device->second.m_presentation_order;
        for (auto it = frames.begin(); it != frames.end(); ++it) {
            if (it->first == offset) {
                auto frame = std::move(it->second);
                frames.erase(it);
                return frame;
            }
        }
        auto decoded = device->second.m_decode_order.find(offset);
        if (decoded != device->second.m_decode_order.end())
            return std::move(device->second.m_decode_order.extract(decoded).mapped());
        return {};
    }
""")
])

# VIC now accepts multiple enabled surfaces and non-opaque planes. Composite source-over
# in 10-bit channel space instead of aborting the entire movie on those common registers.
edit("app/src/main/cpp/skyline/soc/host1x/video/video_core/host1x/vic_processor.cpp", [
    ("""Pixel Sample(const FFmpeg::Frame& f, u32 x, u32 y, u16 alpha) {
    const auto format = f.GetPixelFormat();
    const u8* luma = f.GetPlane(0) + y * f.GetStride(0);
    const u8* u = f.GetPlane(1) + (y / 2) * f.GetStride(1);
    if (format == AV_PIX_FMT_YUV420P || format == AV_PIX_FMT_YUVJ420P) {
        const u8* v = f.GetPlane(2) + (y / 2) * f.GetStride(2);
        return {u16(luma[x] << 2), u16(u[x/2] << 2), u16(v[x/2] << 2), alpha};
    }
    if (format == AV_PIX_FMT_NV12)
        return {u16(luma[x] << 2), u16(u[x & ~1u] << 2), u16(u[(x & ~1u)+1] << 2), alpha};
    throw std::runtime_error("Unsupported NVDEC output pixel format");
}
""",
"""Pixel Sample(const FFmpeg::Frame& f, u32 x, u32 y, u16 alpha) {
    const auto format = f.GetPixelFormat();
    const u8* luma = f.GetPlane(0) + y * f.GetStride(0);
    const u8* u = f.GetPlane(1) + (y / 2) * f.GetStride(1);
    if (format == AV_PIX_FMT_YUV420P || format == AV_PIX_FMT_YUVJ420P) {
        const u8* v = f.GetPlane(2) + (y / 2) * f.GetStride(2);
        return {u16(luma[x] << 2), u16(u[x/2] << 2), u16(v[x/2] << 2), alpha};
    }
    if (format == AV_PIX_FMT_NV12)
        return {u16(luma[x] << 2), u16(u[x & ~1u] << 2), u16(u[(x & ~1u)+1] << 2), alpha};
    throw std::runtime_error("Unsupported NVDEC output pixel format");
}
Pixel Composite(Pixel source, Pixel destination) {
    const u32 alpha = std::min<u32>(source.a, 1023);
    const u32 inverse = 1023 - alpha;
    const auto channel = [alpha, inverse](u16 src, u16 dst) {
        return static_cast<u16>((u32(src) * alpha + u32(dst) * inverse + 511) / 1023);
    };
    const u32 outAlpha = alpha + (u32(destination.a) * inverse + 511) / 1023;
    return {channel(source.r, destination.r), channel(source.g, destination.g),
            channel(source.b, destination.b), static_cast<u16>(std::min<u32>(outAlpha, 1023))};
}
"""),
    ("""        if (enabled || slot.config.planar_alpha.Value() != 1023)
            throw std::runtime_error("VIC alpha/multiple-slot composition is not implemented");
        if (slot.config.frame_format.Value() != DxvhadFrameFormat::Progressive)
            throw std::runtime_error("VIC interlaced output is not implemented");
""",
"""        const auto frameFormat = slot.config.frame_format.Value();
        if (frameFormat != DxvhadFrameFormat::Progressive &&
            frameFormat != DxvhadFrameFormat::TopField &&
            frameFormat != DxvhadFrameFormat::BottomField &&
            frameFormat != DxvhadFrameFormat::InterlacedTopFieldFirst &&
            frameFormat != DxvhadFrameFormat::InterlacedBottomFieldFirst)
            throw std::runtime_error("Unsupported VIC field format");
"""),
    ("""            const u32 sy = sy0 + u64(y - top) * (sy1 - sy0) / (bottom - top);
            if (sy >= u32(frame->GetHeight())) continue;
            for (u32 x = clipLeft; x < clipRight; ++x) {
""",
"""            u64 sourceY;
            if (frameFormat == DxvhadFrameFormat::Progressive) {
                sourceY = sy0 + u64(y - top) * (sy1 - sy0) / (bottom - top);
            } else {
                // Bob the selected field: sample alternating source lines and duplicate each
                // into the two destination scanlines.
                const u64 destinationFieldHeight = std::max<u64>(1, (bottom - top + 1) / 2);
                const u64 fieldLine = (y - top) / 2;
                sourceY = sy0 + fieldLine * (sy1 - sy0) / destinationFieldHeight;
                const bool bottomField = frameFormat == DxvhadFrameFormat::BottomField ||
                                         frameFormat == DxvhadFrameFormat::InterlacedBottomFieldFirst;
                sourceY = sourceY * 2 + (bottomField ? 1 : 0);
            }
            if (sourceY >= u32(frame->GetHeight())) continue;
            const u32 sy = static_cast<u32>(sourceY);
            for (u32 x = clipLeft; x < clipRight; ++x) {
"""),
    ("""                auto p = Convert(Sample(*frame, sx, sy, slot.config.planar_alpha), slot);
                pixels[size_t(y)*width+x] = p;
""",
"""                auto p = Convert(Sample(*frame, sx, sy, slot.config.planar_alpha), slot);
                auto& destination = pixels[size_t(y)*width+x];
                destination = p.a >= 1023 ? p : Composite(p, destination);
"""),
    ("""        if (config.output_config.output_flip_x || config.output_config.output_flip_y)
            throw std::runtime_error("VIC flipped NV12 output is not implemented");
""", "")
])

# Flipped NV12 surfaces are valid VIC output modes; flip both luma and chroma planes.
edit("app/src/main/cpp/skyline/soc/host1x/video/video_core/host1x/vic_processor.cpp", [
    ("""        for (u32 y=0; y<std::min(height,lh); ++y) for (u32 x=0; x<std::min(width,lw); ++x) {
            const auto& p=pixels[size_t(y)*width+x];
            luma[size_t(y)*yp+x]=p.r>>2;
            if (!(x&1) && !(y&1) && x/2<cw && y/2<ch) {
                chroma[size_t(y/2)*cp+x]=p.g>>2;
                chroma[size_t(y/2)*cp+x+1]=p.b>>2;
            }
        }
""",
"""        for (u32 y=0; y<std::min(height,lh); ++y) for (u32 x=0; x<std::min(width,lw); ++x) {
            const auto& p=pixels[size_t(y)*width+x];
            const u32 dx=config.output_config.output_flip_x ? lw-1-x : x;
            const u32 dy=config.output_config.output_flip_y ? lh-1-y : y;
            if (dx>=lw || dy>=lh) continue;
            luma[size_t(dy)*yp+dx]=p.r>>2;
            if (!(x&1) && !(y&1)) {
                const u32 cx=config.output_config.output_flip_x ? cw-1-x/2 : x/2;
                const u32 cy=config.output_config.output_flip_y ? ch-1-y/2 : y/2;
                if (cx<cw && cy<ch) {
                    chroma[size_t(cy)*cp+cx*2]=p.g>>2;
                    chroma[size_t(cy)*cp+cx*2+1]=p.b>>2;
                }
            }
        }
""")
])

print("Applied Dimm advanced graphics settings: Vulkan resolution scale, mipmap LOD bias and anisotropy.")
print("Applied exact-offset NVDEC frame retrieval and expanded VIC multi-slot/alpha/field/flip handling.")

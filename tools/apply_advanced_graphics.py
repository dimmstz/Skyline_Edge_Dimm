#!/usr/bin/env python3
"""Patch the pinned Strato/Skyline source with Dimm graphics controls and VIC fixes."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_advanced_graphics.py <strato-source-root>")

root = Path(sys.argv[1]).resolve()
project_root = Path(__file__).resolve().parents[1]
version_file = project_root / "version.properties"
version_values = {}
for line in version_file.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        version_values[key.strip()] = value.strip()
VERSION_NAME = version_values["VERSION_NAME"]
VERSION_CODE = int(version_values["VERSION_CODE"])
RELEASE_TAG = version_values["RELEASE_TAG"]
if not VERSION_NAME or VERSION_CODE < 1 or not RELEASE_TAG.startswith("v"):
    raise SystemExit("Invalid version.properties: set VERSION_NAME, positive VERSION_CODE and RELEASE_TAG")

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
    ("compileSdk 34", "compileSdk 35"),
    ("targetSdk 33", "targetSdk 35"),
    ("buildConfigField 'String', 'RELEASE_VERSION', '\"0.0.4-1\"'",
     f"""buildConfigField 'String', 'RELEASE_VERSION', '"{VERSION_NAME}"'"""),
    ("versionCode getGitVersionCode()", f"versionCode {VERSION_CODE}"),
    ('versionName "0.0.4-1"', f'versionName "{VERSION_NAME}"'),
    ("""android {
""", """def releaseStorePath = System.getenv("ANDROID_KEYSTORE_PATH")
def releaseStorePassword = System.getenv("ANDROID_STORE_PASSWORD")
def releaseKeyAlias = System.getenv("ANDROID_KEY_ALIAS")
def releaseKeyPassword = System.getenv("ANDROID_KEY_PASSWORD")

android {
    signingConfigs {
        release {
            storeFile file(releaseStorePath ?: "${rootDir}/missing-release-key.jks")
            storePassword releaseStorePassword ?: ""
            keyAlias releaseKeyAlias ?: ""
            keyPassword releaseKeyPassword ?: ""
        }
    }
"""),
    ("""signingConfig signingConfigs.debug
            manifestPlaceholders""", """signingConfig signingConfigs.release
            manifestPlaceholders""")

])

# Android 15 requires a toolchain that understands API 35.
edit("build.gradle", [
    ("com.android.tools.build:gradle:8.2.1", "com.android.tools.build:gradle:8.6.1")
])

edit("gradle/wrapper/gradle-wrapper.properties", [
    ("gradle-8.2-bin.zip", "gradle-8.7-bin.zip")
])

edit("app/src/main/res/values/strings.xml", [
    ('<string name="app_name" translatable="false">Strato Mali</string>',
     '<string name="app_name" translatable="false">Skyline Dimm</string>')
])

# Use a three-column library on phones, with compact fixed-height cover art.
# Tablets keep an adaptive grid with at least three columns.
edit("app/src/main/java/org/stratoemu/strato/MainActivity.kt", [
    ("""        val itemWidth = 225
        val metrics = resources.displayMetrics
        val gridSpan = ceil((metrics.widthPixels / metrics.density) / itemWidth).toInt()
""",
     """        val metrics = resources.displayMetrics
        val widthDp = metrics.widthPixels / metrics.density
        val gridSpan = if (widthDp < 600f) 3 else ceil(widthDp / 220f).toInt().coerceAtLeast(3)
""")
])

edit("app/src/main/res/layout/app_item_grid.xml", [
    ('android:layout_height="wrap_content"\n        android:layout_margin="5dp"\n        app:cardBackgroundColor="@color/mali_card"\n        app:cardCornerRadius="20dp"',
     'android:layout_height="112dp"\n        android:layout_margin="3dp"\n        app:cardBackgroundColor="@color/mali_card"\n        app:cardCornerRadius="14dp"'),
    ('android:layout_height="wrap_content"\n            android:adjustViewBounds="true"',
     'android:layout_height="112dp"\n            android:adjustViewBounds="false"'),
    ('android:layout_marginStart="10dp"\n        android:layout_marginEnd="10dp"\n        android:ellipsize="end"',
     'android:layout_marginStart="6dp"\n        android:layout_marginEnd="6dp"\n        android:ellipsize="end"'),
    ('android:singleLine="true"\n        android:textColor="@color/mali_text"',
     'android:singleLine="true"\n        android:textSize="11sp"\n        android:textColor="@color/mali_text"')
])

edit("app/src/main/res/layout/app_item_grid_compact.xml", [
    ('android:layout_height="wrap_content"\n    android:layout_margin="5dp"\n    app:cardBackgroundColor="@color/mali_card"\n    app:cardCornerRadius="20dp"',
     'android:layout_height="112dp"\n    android:layout_margin="3dp"\n    app:cardBackgroundColor="@color/mali_card"\n    app:cardCornerRadius="14dp"'),
    ('android:layout_height="wrap_content">\n\n        <ImageView',
     'android:layout_height="match_parent">\n\n        <ImageView'),
    ('android:layout_height="wrap_content"\n            android:adjustViewBounds="true"',
     'android:layout_height="match_parent"\n            android:adjustViewBounds="false"')
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
    ('        "respect_display_cutout", "enable_foldable_layout", "show_pause_button", "disable_shader_cache")\n',
     '        "respect_display_cutout", "enable_foldable_layout", "show_pause_button", "disable_shader_cache",\n'
     '        "force_triple_buffering", "disable_frame_throttling", "executor_slot_count_scale",\n'
     '        "executor_flush_threshold", "use_direct_memory_import", "force_max_gpu_clocks", "free_guest_texture_memory", "performance_profile")\n')
])

edit("app/src/main/java/org/stratoemu/strato/settings/GlobalSettingsFragment.kt", [
    ('        "executor_flush_threshold", "use_direct_memory_import", "force_max_gpu_clocks", "free_guest_texture_memory",\n',
     '        "executor_flush_threshold", "use_direct_memory_import", "force_max_gpu_clocks", "free_guest_texture_memory",\n'
     '        "mipmap_lod_bias", "max_anisotropy",\n')
])

edit("app/src/main/res/xml/emulation_preferences.xml", [
    ('        android:key="category_gpu"\n        android:title="@string/gpu">',
     '        android:key="category_gpu"\n        android:title="@string/advanced_graphics_controls">'),
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
     '        <SwitchPreferenceCompat\n            android:defaultValue="true"\n            android:summaryOff="@string/triple_buffering_disabled"'),
    ('''            app:key="resolution_scale"
            app:refreshRequired="true"
            app:title="@string/resolution_scale"
            app:useSimpleSummaryProvider="true" />''',
     '''            app:key="resolution_scale"
            app:refreshRequired="true"
            app:title="@string/resolution_scale"
            app:useSimpleSummaryProvider="true" />
        <org.stratoemu.strato.preference.IntegerListPreference
            android:defaultValue="0"
            android:entries="@array/performance_profile_entries"
            android:entryValues="@array/performance_profile_values"
            android:summary="@string/performance_profile_desc"
            app:key="performance_profile"
            app:refreshRequired="true"
            app:title="@string/performance_profile"
            app:useSimpleSummaryProvider="true" />''')
])

# Reorganize the emulation settings into focused, top-level sections.
# Keep the existing preference objects and keys intact so stored values and listeners survive.
import xml.etree.ElementTree as ET

ET.register_namespace("android", "http://schemas.android.com/apk/res/android")
ET.register_namespace("app", "http://schemas.android.com/apk/res-auto")
preferences_path = root / "app/src/main/res/xml/emulation_preferences.xml"
tree = ET.parse(preferences_path)
preference_root = tree.getroot()
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"
APP_NS = "{http://schemas.android.com/apk/res-auto}"

def pref_key(element):
    return element.get(APP_NS + "key") or element.get(ANDROID_NS + "key")

def make_category(key, title):
    return ET.Element("PreferenceCategory", {
        ANDROID_NS + "key": key,
        ANDROID_NS + "title": title,
    })

presentation = next((e for e in preference_root if e.tag == "PreferenceCategory" and e.get(ANDROID_NS + "key") == "category_presentation"), None)
gpu = next((e for e in preference_root if e.tag == "PreferenceCategory" and e.get(ANDROID_NS + "key") == "category_gpu"), None)
if presentation is None or gpu is None:
    raise SystemExit("Cannot organize settings: presentation/GPU categories are missing")

graphics = make_category("category_graphics_quality", "@string/graphics_quality")
driver = make_category("category_gpu_driver", "@string/graphics_drivers")
performance = make_category("category_performance", "@string/performance_stability")

# Resolution scaling currently lives in Display; move it with texture quality controls.
for element in list(presentation):
    if pref_key(element) == "resolution_scale":
        presentation.remove(element)
        graphics.append(element)

for element in list(gpu):
    key = pref_key(element)
    if key == "gpu_driver":
        gpu.remove(element)
        driver.append(element)
    elif key in {"mipmap_lod_bias", "max_anisotropy", "performance_profile"}:
        gpu.remove(element)
        graphics.append(element)
    else:
        gpu.remove(element)
        performance.append(element)

# Keep the settings screen ordered by user task: display, visual quality, drivers,
# performance/latency, then audio and compatibility/debug sections.
children = list(preference_root)
insert_at = children.index(presentation) + 1
for category in (graphics, driver, performance):
    preference_root.insert(insert_at, category)
    insert_at += 1
preference_root.remove(gpu)
ET.indent(tree, space="    ")
tree.write(preferences_path, encoding="utf-8", xml_declaration=True)

resources = root / "app/src/main/res/values/dimm_advanced_graphics.xml"
if resources.exists():
    raise SystemExit("Refusing to overwrite app/src/main/res/values/dimm_advanced_graphics.xml")
resources.write_text("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="graphics_quality">Qualidade gráfica</string>
    <string name="graphics_drivers">Drivers gráficos</string>
    <string name="performance_stability">Desempenho, CPU e memória</string>
    <string name="advanced_graphics_controls">GPU e desempenho avançado</string>
    <string name="mipmap_lod_bias">Mipmap LOD bias</string>
    <string name="mipmap_lod_bias_desc">Positive values select lower-resolution mip levels at distance and can reduce texture bandwidth. Negative values sharpen distant textures but may cause shimmering. Restart the game after changing.</string>
    <string-array name="mipmap_lod_bias_entries" translatable="false">
        <item>Padrão (0.0)</item>
        <item>Leve (+1.0)</item>
        <item>Agressivo (+2.0)</item>
    </string-array>
    <integer-array name="mipmap_lod_bias_values">
        <item>0</item><item>4</item><item>8</item>
    </integer-array>
    <string name="max_anisotropy">Anisotropic filtering override</string>
    <string name="max_anisotropy_desc">Overrides game-provided texture anisotropy when supported by the GPU. Higher values can improve angled surfaces but may cost performance. Restart the game after changing.</string>
    <string name="performance_profile">Performance profile</string>
    <string name="performance_profile_desc">Applies conservative presets to render resolution, texture filtering and GPU queue/memory usage. The low-memory profile may reload textures more often. Frame pacing, shader cache and game compatibility paths remain enabled.</string>
    <string-array name="performance_profile_entries">
        <item>Custom</item><item>Balanced FPS (0.75x)</item><item>Performance (0.50x)</item><item>Low memory (may reload textures)</item>
    </string-array>
    <integer-array name="performance_profile_values">
        <item>0</item><item>1</item><item>2</item><item>4</item>
    </integer-array>
    <string-array name="max_anisotropy_entries" translatable="false">
        <item>Game default</item><item>1x</item><item>2x</item><item>4x</item><item>8x</item><item>16x (device-limited)</item>
    </string-array>
    <integer-array name="max_anisotropy_values">
        <item>0</item><item>1</item><item>2</item><item>4</item><item>8</item><item>16</item>
    </integer-array>
</resources>
""", encoding="utf-8")

# A measured, conservative performance profile maps only to existing real renderer
# controls. It never disables frame pacing, shader/pipeline caches or video paths.
edit("app/src/main/java/org/stratoemu/strato/settings/EmulationSettings.kt", [
    ("    var resolutionScale by sharedPreferences(context, 2, prefName = prefName)\n",
     "    var resolutionScale by sharedPreferences(context, 2, prefName = prefName)\n"
     "    var performanceProfile by sharedPreferences(context, 0, prefName = prefName)\n"
     "    val effectiveResolutionScale: Int get() = when (performanceProfile) { 1 -> 1; 2, 4 -> 0; else -> resolutionScale }\n"
     "    val effectiveMipmapLodBias: Int get() = when (performanceProfile) { 1 -> 1; 2 -> 3; 4 -> 8; else -> mipmapLodBias }\n"
     "    val effectiveMaxAnisotropy: Int get() = when (performanceProfile) { 1 -> 2; 2, 4 -> 1; else -> maxAnisotropy }\n"
     "    val effectiveExecutorSlotCountScale: Int get() = if (performanceProfile == 4) 2 else executorSlotCountScale\n"
     "    val effectiveExecutorFlushThreshold: Int get() = if (performanceProfile == 4) 128 else executorFlushThreshold\n"
     "    val effectiveFreeGuestTextureMemory: Boolean get() = performanceProfile == 4 || freeGuestTextureMemory\n")
])

edit("app/src/main/java/org/stratoemu/strato/settings/NativeSettings.kt", [
    ("        pref.resolutionScale,\n"
     "        pref.mipmapLodBias,\n"
     "        pref.maxAnisotropy\n",
     "        pref.effectiveResolutionScale,\n"
     "        pref.effectiveMipmapLodBias,\n"
     "        pref.effectiveMaxAnisotropy\n")
])

edit("app/src/main/java/org/stratoemu/strato/settings/EmulationSettings.kt", [
    ("    var executorSlotCountScale by sharedPreferences(context, 6, prefName = prefName)\n",
     "    var executorSlotCountScale by sharedPreferences(context, 4, prefName = prefName)\n")
])

edit("app/src/main/java/org/stratoemu/strato/settings/NativeSettings.kt", [
    ("        pref.executorSlotCountScale,\n", "        pref.effectiveExecutorSlotCountScale,\n"),
    ("        pref.executorFlushThreshold,\n", "        pref.effectiveExecutorFlushThreshold,\n"),
    ("        pref.freeGuestTextureMemory,\n", "        pref.effectiveFreeGuestTextureMemory,\n")
])

# Keep the per-frame overlay lightweight on Adreno 619: do not format locale-aware
# floating-point strings on every Compose update. FPS/RAM remain available; detailed
# frametime/jitter stay in diagnostics/logging rather than the hot UI path.
edit("app/src/main/java/org/stratoemu/strato/EmulationActivity.kt", [
    ('                        text = "$fps FPS • $ramUsage MB"\n',
     '                        text = "$fps FPS • $ramUsage MB"\n')
])

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


# Accessibility and contrast audit: keep all settings surfaces readable in dark mode.
edit("app/src/main/res/values/settings_design.xml", [
    ("""        <item name="colorOnSurface">@color/settings_on_container</item>
""", """        <item name="colorOnSurface">@color/settings_on_container</item>
        <item name="android:textColorPrimary">@color/settings_on_container</item>
        <item name="android:textColorSecondary">@color/settings_secondary_text</item>
        <item name="android:textColorHint">@color/settings_secondary_text</item>
        <item name="colorOnSurfaceVariant">@color/settings_secondary_text</item>
        <item name="colorControlNormal">@color/settings_secondary_text</item>
        <item name="colorControlActivated">@color/settings_blue</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:windowLightNavigationBar">false</item>
""")
])

# Preference rows previously painted with fixed RGB values; resolve colors from the active theme.
edit("app/src/main/java/org/stratoemu/strato/settings/MaliPreferenceCards.kt", [
    ("import androidx.recyclerview.widget.RecyclerView\n",
     "import androidx.recyclerview.widget.RecyclerView\n"
     "import com.google.android.material.color.MaterialColors\n"),
    ("    private val fill = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = android.graphics.Color.rgb(15, 38, 77) }\n"
     "    private val stroke = Paint(Paint.ANTI_ALIAS_FLAG).apply {\n"
     "        color = android.graphics.Color.rgb(39, 101, 170)\n",
     "    private val fill = Paint(Paint.ANTI_ALIAS_FLAG).apply {\n"
     "        color = MaterialColors.getColor(context, com.google.android.material.R.attr.colorSurfaceVariant, android.graphics.Color.rgb(15, 38, 77))\n"
     "    }\n"
     "    private val stroke = Paint(Paint.ANTI_ALIAS_FLAG).apply {\n"
     "        color = MaterialColors.getColor(context, com.google.android.material.R.attr.colorOutline, android.graphics.Color.rgb(39, 101, 170))\n")
])


# Global on-screen controller opacity. This is a view-level alpha multiplier:
# touch hit-testing and per-button opacity/scale customization remain unchanged.
edit("app/src/main/java/org/stratoemu/strato/settings/AppSettings.kt", [
    ("    var onScreenControl by sharedPreferences(context, true)\n",
     "    var onScreenControl by sharedPreferences(context, true)\n"
     "    var onScreenControlOpacity by sharedPreferences(context, 100)\n")
])

edit("app/src/main/java/org/stratoemu/strato/input/onscreen/OnScreenControllerView.kt", [
    ("    var controllerType : ControllerType? = null\n",
     "    var globalOpacityPercent : Int = 100\n"
     "        set(value) { field = value.coerceIn(0, 100); invalidate() }\n"
     "    var controllerType : ControllerType? = null\n"),
    ("""        val allowedIds = controllerTypeMappings[controllerType]
        controls.allButtons.forEach { button ->
""",
     """        val layer = canvas.saveLayerAlpha(0f, 0f, width.toFloat(), height.toFloat(),
            (globalOpacityPercent * 255 / 100).coerceIn(0, 255))
        val allowedIds = controllerTypeMappings[controllerType]
        controls.allButtons.forEach { button ->
"""),
    ("""        // Draw the selection box around the edit button
        if (editInfo.isEditing && editInfo.editButton is OnScreenButton)
            canvas.drawRect((editInfo.editButton as OnScreenButton).currentBounds, selectionPaint)
""",
     """        // Draw the selection box around the edit button
        if (editInfo.isEditing && editInfo.editButton is OnScreenButton)
            canvas.drawRect((editInfo.editButton as OnScreenButton).currentBounds, selectionPaint)
        canvas.restoreToCount(layer)
""")
])

edit("app/src/main/java/org/stratoemu/strato/EmulationActivity.kt", [
    ("""        binding.onScreenControllerView.apply {
            vibrator = builtinVibrator
""",
     """        binding.onScreenControllerView.apply {
            globalOpacityPercent = appSettings.onScreenControlOpacity
            vibrator = builtinVibrator
""")
])

edit("app/src/main/res/xml/input_preferences.xml", [
    ("</androidx.preference.PreferenceScreen>",
     """    <PreferenceCategory
        android:key="category_onscreen_controls"
        android:title="@string/onscreen_controls">
        <SeekBarPreference
            android:defaultValue="100"
            android:max="100"
            android:min="0"
            android:summary="@string/onscreen_control_opacity_desc"
            app:key="on_screen_control_opacity"
            app:showSeekBarValue="true"
            app:title="@string/onscreen_control_opacity" />
    </PreferenceCategory>
</androidx.preference.PreferenceScreen>""")
])

edit("app/src/main/res/values/dimm_advanced_graphics.xml", [
    ("</resources>",
     """    <string name="onscreen_controls">Controles na tela</string>
    <string name="onscreen_control_opacity">Opacidade dos controles</string>
    <string name="onscreen_control_opacity_desc">Ajusta a transparência global dos botões e analógicos na tela durante o jogo. Não altera a área de toque nem a opacidade individual configurada no editor.</string>
</resources>""")
])

print("Applied Dimm advanced graphics settings: Vulkan resolution scale, mipmap LOD bias, anisotropy, GPU scheduling, clocks, memory and frame pacing controls.")

# VFX/FPS backend audit instrumentation. Record real Vulkan capabilities only;
# do not pretend guest effects can be classified safely.
edit("app/src/main/cpp/skyline/gpu.cpp", [
    ("""        LOGI("Internal resolution scale: {}x (texture-cache scaling)", resolutionScale.Factor());
""", """        LOGI("Internal resolution scale: {}x (texture-cache scaling)", resolutionScale.Factor());
        LOGI("[PERF] InternalScale={}x mipmapLodBias={} anisotropyOverride={} shaderCache={} frameThrottling={}",
             resolutionScale.Factor(), MipmapLodBias(), MaxAnisotropy(),
             !*state.settings->disableShaderCache, !*state.settings->disableFrameThrottling);
        const auto deviceProperties{vkPhysicalDevice.getProperties()};
        LOGI("[VFX-OPT] GPU={} vendor=0x{:04X} device=0x{:04X} driverVersion={} VulkanApi={}.{}.{}",
             deviceProperties.deviceName, traits.vendorId, traits.deviceId, traits.driverVersion,
             VK_API_VERSION_MAJOR(deviceProperties.apiVersion), VK_API_VERSION_MINOR(deviceProperties.apiVersion),
             VK_API_VERSION_PATCH(deviceProperties.apiVersion));
        LOGI("[VFX-OPT] capabilities shaderFloat16={} anisotropy={} maxAnisotropy={} maxImage2D={} maxImageArrayLayers={}",
             traits.supportsFloat16, traits.supportsAnisotropicFiltering, deviceProperties.limits.maxSamplerAnisotropy,
             deviceProperties.limits.maxImageDimension2D, deviceProperties.limits.maxImageArrayLayers);
        LOGI("[VFX-OPT] shadowScale=unsupported vfxScale=unsupported skipVolumetrics=unsupported disablePostProcessing=unsupported disableReflections=unsupported; native guest render targets remain unchanged");
""")
])

edit("app/src/main/cpp/skyline/gpu/shader_manager.cpp", [
    ("""        hostTranslateInfo = Shader::HostTranslateInfo{
""", """        LOGI("[VFX-OPT] shader FP16 capability={} (translator preserves guest shader precision semantics; no unsafe forced demotion)",
             traits.supportsFloat16);
        hostTranslateInfo = Shader::HostTranslateInfo{
""")
])

print("Applied exact-offset NVDEC frame retrieval and expanded VIC multi-slot/alpha/field/flip handling.")

# Detect the actual Vulkan GPU vendor and apply conservative vendor-aware defaults.
# Vulkan vendorID is authoritative here; Android model strings are not used.
edit("app/src/main/java/org/stratoemu/strato/settings/NativeSettings.kt", [
    ("    var maxAnisotropy : Int = 0\n", "    var maxAnisotropy : Int = 0,\n    var performanceProfile : Int = 0\n"),
    ("        pref.effectiveMaxAnisotropy\n", "        pref.effectiveMaxAnisotropy,\n        pref.performanceProfile\n")
])

edit("app/src/main/cpp/skyline/common/settings.h", [
    ("        Setting<int> maxAnisotropy; //!< 0 keeps the game's sampler anisotropy\n",
     "        Setting<int> maxAnisotropy; //!< 0 keeps the game's sampler anisotropy\n"
     "        Setting<int> performanceProfile; //!< 0 custom, 1 balanced, 2 performance, 3 automatic GPU-aware\n")
])

edit("app/src/main/cpp/skyline/common/android_settings.h", [
    ('            maxAnisotropy = ktSettings.GetInt<int>("maxAnisotropy");\n',
     '            maxAnisotropy = ktSettings.GetInt<int>("maxAnisotropy");\n'
     '            performanceProfile = ktSettings.GetInt<int>("performanceProfile");\n')
])

edit("app/src/main/cpp/skyline/gpu.cpp", [
    ("#include <dlfcn.h>\n", "#include <algorithm>\n#include <dlfcn.h>\n"),
    ("    int GPU::MipmapLodBias() const { return *state.settings->mipmapLodBias; }\n",
     "    int GPU::MipmapLodBias() const {\n"
     "        if (*state.settings->performanceProfile == 3 && (traits.vendorId == 0x5143U || traits.vendorId == 0x13B5U)) return 4;\n"
     "        return *state.settings->mipmapLodBias;\n"
     "    }\n"),
    ("    int GPU::MaxAnisotropy() const { return *state.settings->maxAnisotropy; }\n",
     "    int GPU::MaxAnisotropy() const {\n"
     "        if (*state.settings->performanceProfile == 3) {\n"
     "            if (traits.vendorId == 0x5143U) return 2; // Qualcomm Adreno\n"
     "            if (traits.vendorId == 0x13B5U) return 1; // ARM Mali: keep filtering lightweight\n"
     "        }\n"
     "        return *state.settings->maxAnisotropy;\n"
     "    }\n"),
    ("    GPU::GPU(const DeviceState &state)\n        : state(state),",
     "    static int SelectResolutionScale(const DeviceState &state, const TraitManager &traits) {\n"
     "        const int requested = *state.settings->resolutionScale;\n"
     "        if (*state.settings->performanceProfile != 3) return requested;\n"
     "        // 1 = 0.75x in Scale::FromSetting. Keep explicit lower user scales intact.\n"
     "        if (traits.vendorId == 0x5143U || traits.vendorId == 0x13B5U) return std::min(requested, 1);\n"
     "        return requested; // Unknown GPU: never guess or force a vendor profile.\n"
     "    }\n\n"
     "    GPU::GPU(const DeviceState &state)\n        : state(state),"),
    ("          resolutionScale(resolution::Scale::FromSetting(*state.settings->resolutionScale)),",
     "          resolutionScale(resolution::Scale::FromSetting(SelectResolutionScale(state, traits))),"),
    ('LOGI("[VFX-OPT] GPU={} vendor=0x{:04X} device=0x{:04X} driverVersion={} VulkanApi={}.{}.{}",\n',
     'LOGI("[VFX-OPT] GPU={} family={} vendor=0x{:04X} device=0x{:04X} driverVersion={} VulkanApi={}.{}.{}",\n'),
    ("             deviceProperties.deviceName, traits.vendorId, traits.deviceId, traits.driverVersion,\n",
     '             deviceProperties.deviceName, traits.vendorId == 0x5143U ? "Adreno" : traits.vendorId == 0x13B5U ? "Mali" : "Unknown",\n'
     "             traits.vendorId, traits.deviceId, traits.driverVersion,\n")
])

edit("app/src/main/res/values/dimm_advanced_graphics.xml", [
    ("<item>Custom</item><item>Balanced FPS (0.75x)</item><item>Performance (0.50x)</item>",
     "<item>Custom</item><item>Balanced FPS (0.75x)</item><item>Performance (0.50x)</item><item>Auto GPU (Adreno/Mali)</item><item>Low memory (may reload textures)</item>"),
    ("<item>0</item><item>1</item><item>2</item>\n    </integer-array>",
     "<item>0</item><item>1</item><item>2</item><item>3</item><item>4</item>\n    </integer-array>")
])

print("Applied Vulkan vendor detection: Qualcomm Adreno (0x5143), ARM Mali (0x13B5), conservative automatic resolution/LOD/anisotropy profile, and unknown-vendor fallback.");

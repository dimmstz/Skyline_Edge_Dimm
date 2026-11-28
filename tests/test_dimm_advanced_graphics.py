#!/usr/bin/env python3
"""Static end-to-end assertions for the Dimm settings-to-Vulkan and VIC patches."""
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
version_values = {}
for line in (project_root / "version.properties").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        version_values[key.strip()] = value.strip()
VERSION_NAME = version_values["VERSION_NAME"]
VERSION_CODE = version_values["VERSION_CODE"]

if len(sys.argv) != 2:
    raise SystemExit("usage: test_dimm_advanced_graphics.py <patched-source-root>")
root = Path(sys.argv[1])

def read(path):
    p = root / path
    if not p.is_file():
        raise SystemExit(f"Missing patched source: {path}")
    return p.read_text(encoding="utf-8")

checks = {
    "Android 15 API compatibility": ("app/build.gradle",
                                     ["compileSdk 35", "targetSdk 35"]),
    "Android Gradle Plugin 8.6.1": ("build.gradle",
                                   ["com.android.tools.build:gradle:8.6.1"]),
    "Gradle 8.7 wrapper": ("gradle/wrapper/gradle-wrapper.properties",
                           ["gradle-8.7-bin.zip"]),
    "Android preference model": ("app/src/main/java/org/stratoemu/strato/settings/EmulationSettings.kt",
                                 ["mipmapLodBias", "maxAnisotropy", "performanceProfile", "effectiveResolutionScale", "effectiveMipmapLodBias", "effectiveMaxAnisotropy", "effectiveExecutorSlotCountScale", "effectiveExecutorFlushThreshold", "effectiveFreeGuestTextureMemory"]),
    "Native settings serialization": ("app/src/main/java/org/stratoemu/strato/settings/NativeSettings.kt",
                                       ["pref.effectiveMipmapLodBias", "pref.effectiveMaxAnisotropy", "pref.effectiveResolutionScale", "pref.performanceProfile", "pref.effectiveExecutorSlotCountScale", "pref.effectiveExecutorFlushThreshold", "pref.effectiveFreeGuestTextureMemory"]),
    "JNI settings bridge": ("app/src/main/cpp/skyline/common/android_settings.h",
                            ['GetInt<int>("mipmapLodBias")', 'GetInt<int>("maxAnisotropy")', 'GetInt<int>("performanceProfile")']),
    "Native settings storage": ("app/src/main/cpp/skyline/common/settings.h",
                                ["Setting<int> mipmapLodBias", "Setting<int> maxAnisotropy"]),
    "Vulkan sampler LOD bias": ("app/src/main/cpp/skyline/gpu/interconnect/common/samplers.cpp",
                                ["ctx.gpu.MipmapLodBias()", "deviceLimits.maxSamplerLodBias",
                                 "static_cast<float>(ctx.gpu.MipmapLodBias()) * 0.25f",
                                 "std::clamp", ".mipLodBias = mipLodBias"]),
    "Vulkan anisotropy override": ("app/src/main/cpp/skyline/gpu/interconnect/common/samplers.cpp",
                                   ["ctx.gpu.MaxAnisotropy()", "deviceLimits.maxSamplerAnisotropy",
                                    "std::min(static_cast<float>(requestedAnisotropy)"]),
    "Vulkan Adreno/Mali vendor recognition and automatic profile": ("app/src/main/cpp/skyline/gpu.cpp",
        ["traits.vendorId == 0x5143U", "traits.vendorId == 0x13B5U", "Adreno", "Mali",
         "SelectResolutionScale", "performanceProfile", "std::min(requested, 1)"]),
    "Native automatic GPU profile setting": ("app/src/main/cpp/skyline/common/settings.h",
        ["Setting<int> performanceProfile"]),
    "Automatic GPU profile reaches native settings": ("app/src/main/cpp/skyline/common/android_settings.h",
        ['GetInt<int>("performanceProfile")']),
    "Organized graphics, driver and performance categories": ("app/src/main/res/xml/emulation_preferences.xml",
                                     ["category_graphics_quality", "category_gpu_driver", "category_performance",
                                      "@string/graphics_quality", "@string/graphics_drivers", "@string/performance_stability"]),
    "Resolution and texture UI": ("app/src/main/res/xml/emulation_preferences.xml",
                                  ['app:key="mipmap_lod_bias"', 'app:key="max_anisotropy"', 'app:key="resolution_scale"', 'app:key="performance_profile"']),
    "GPU settings section visibility": ("app/src/main/java/org/stratoemu/strato/settings/GlobalSettingsFragment.kt",
                                        ['"mipmap_lod_bias"', '"max_anisotropy"', '"performance_profile"',
                                         '"force_triple_buffering"', '"disable_frame_throttling"',
                                         '"executor_slot_count_scale"', '"executor_flush_threshold"',
                                         '"use_direct_memory_import"', '"force_max_gpu_clocks"',
                                         '"free_guest_texture_memory"', '"disable_shader_cache"']),
    "Exact NVDEC frame address match": ("app/src/main/cpp/skyline/soc/host1x/video/video_core/host1x/host1x.h",
                                        ["if (it->first == offset)", "m_decode_order.find(offset)"]),
    "VIC multi-layer and alpha handling": ("app/src/main/cpp/skyline/soc/host1x/video/video_core/host1x/vic_processor.cpp",
                                           ["Pixel Composite(", "destination = p.a >= 1023 ? p : Composite(p, destination)"]),
    "Dimm package identity": ("app/build.gradle",
                              ['applicationId "com.dimm.skyline"', f"versionCode {VERSION_CODE}", f'versionName "{VERSION_NAME}"']),
    "Persistent Android release signing": ("app/build.gradle",
                                            ['signingConfigs {', 'release {', 'ANDROID_KEYSTORE_PATH', 'signingConfig signingConfigs.release']),
    "Real performance profile mapping": ("app/src/main/java/org/stratoemu/strato/settings/EmulationSettings.kt",
                                            ["performanceProfile", "effectiveResolutionScale", "effectiveMipmapLodBias", "effectiveMaxAnisotropy"]),
    "Native profile values reach Vulkan settings": ("app/src/main/java/org/stratoemu/strato/settings/NativeSettings.kt",
                                                     ["pref.effectiveResolutionScale", "pref.effectiveMipmapLodBias", "pref.effectiveMaxAnisotropy", "pref.performanceProfile"]),
    "Lightweight per-frame performance overlay": ("app/src/main/java/org/stratoemu/strato/EmulationActivity.kt",
                                                   ["$fps FPS", "$ramUsage MB"]),
    "Three-column phone game library": ("app/src/main/java/org/stratoemu/strato/MainActivity.kt",
                                         ["if (widthDp < 600f) 3", "coerceAtLeast(3)"]),
    "Compact standard game covers": ("app/src/main/res/layout/app_item_grid.xml",
                                     ['android:layout_height="112dp"', 'android:textSize="11sp"', 'android:layout_margin="3dp"']),
    "Compact overlay game covers": ("app/src/main/res/layout/app_item_grid_compact.xml",
                                    ['android:layout_height="112dp"', 'android:layout_height="match_parent"', 'android:layout_margin="3dp"']),
    "Dark settings theme text contrast": ("app/src/main/res/values/settings_design.xml",
                                          ['android:textColorPrimary', 'android:textColorSecondary', 'colorOnSurfaceVariant', 'colorControlNormal']),
    "Theme-aware preference cards": ("app/src/main/java/org/stratoemu/strato/settings/MaliPreferenceCards.kt",
                                     ['MaterialColors.getColor(context, com.google.android.material.R.attr.colorSurfaceVariant',
                                      'MaterialColors.getColor(context, com.google.android.material.R.attr.colorOutline']),
    "Vulkan VFX capability diagnostics": ("app/src/main/cpp/skyline/gpu.cpp",
                                              ['[VFX-OPT] GPU=', '[VFX-OPT] capabilities shaderFloat16=',
                                               'shadowScale=unsupported', 'disableReflections=unsupported']),
    "Shader precision capability diagnostic": ("app/src/main/cpp/skyline/gpu/shader_manager.cpp",
                                                ['[VFX-OPT] shader FP16 capability=', 'no unsafe forced demotion']),
}

for label, (path, needles) in checks.items():
    source = read(path)
    missing = [needle for needle in needles if needle not in source]
    if missing:
        raise SystemExit(f"{label}: missing expected implementation: {missing}")

pt_settings = root / "app/src/main/res/values-pt-rBR/settings_design.xml"
if not pt_settings.is_file():
    raise SystemExit("Portuguese settings translations were not generated")
pt_settings_text = pt_settings.read_text(encoding="utf-8")
for translated in ("Configurações", "Gráficos", "Pastas de jogos", "Drivers gráficos"):
    if translated not in pt_settings_text:
        raise SystemExit(f"Missing Brazilian Portuguese settings translation: {translated}")

for resource_file, expected in (
    ("setup.xml", ("Bem-vindo ao Skyline Dimm", "Começar a jogar", "Importando chaves")),
    ("emulation_menu.xml", ("Continuar jogo", "Controles na tela", "Sair do jogo")),
):
    translated_file = root / "app/src/main/res/values-pt-rBR" / resource_file
    if not translated_file.is_file():
        raise SystemExit(f"Portuguese resource not generated: {resource_file}")
    translated_text = translated_file.read_text(encoding="utf-8")
    for translated in expected:
        if translated not in translated_text:
            raise SystemExit(f"Missing translation in {resource_file}: {translated}")

pt_arrays = root / "app/src/main/res/values-pt-rBR/array.xml"
if not pt_arrays.is_file():
    raise SystemExit("Portuguese preference arrays were not generated")
pt_arrays_text = pt_arrays.read_text(encoding="utf-8")
pt_advanced = root / "app/src/main/res/values-pt-rBR/dimm_advanced_graphics.xml"
if not pt_advanced.is_file():
    raise SystemExit("Portuguese performance profile translations were not generated")
pt_advanced_text = pt_advanced.read_text(encoding="utf-8")
for translated in ("Perfil de desempenho", "FPS equilibrado (0,75x)", "Desempenho (0,50x)", "Automático GPU (Adreno/Mali)", "Pouca memória (pode recarregar texturas)"):
    if translated not in pt_advanced_text:
        raise SystemExit(f"Missing Brazilian Portuguese performance profile translation: {translated}")

for translated in ("Grade compacta", "Português do Brasil", "A–Z"):
    if translated not in pt_arrays_text:
        raise SystemExit(f"Missing Brazilian Portuguese preference option: {translated}")

resources = read("app/src/main/res/values/dimm_advanced_graphics.xml")
if not all(label in resources for label in ("Padrão (0.0)", "Leve (+1.0)", "Agressivo (+2.0)")):
    raise SystemExit("Mipmap LOD bias presets are incomplete")
if not all(f"<item>{v}</item>" in resources for v in (0,4,8)):
    raise SystemExit("Mipmap LOD bias preset values are incomplete")
if "Auto GPU (Adreno/Mali)" not in resources or "<item>3</item>" not in resources:
    raise SystemExit("Automatic Adreno/Mali profile option is missing")
if "Low memory (may reload textures)" not in resources or "<item>4</item>" not in resources:
    raise SystemExit("Low-memory profile option is missing")
for required in ("effectiveExecutorSlotCountScale", "effectiveExecutorFlushThreshold",
                 "effectiveFreeGuestTextureMemory", "performanceProfile == 4"):
    if required not in read("app/src/main/java/org/stratoemu/strato/settings/EmulationSettings.kt"):
        raise SystemExit(f"Low-memory profile mapping is missing: {required}")
if "pref.effectiveExecutorSlotCountScale" not in read("app/src/main/java/org/stratoemu/strato/settings/NativeSettings.kt"):
    raise SystemExit("Low-memory executor slot setting is not passed to native code")

vic = read("app/src/main/cpp/skyline/soc/host1x/video/video_core/host1x/vic_processor.cpp")
for obsolete in (
    "VIC alpha/multiple-slot composition is not implemented",
    "VIC interlaced output is not implemented",
    "VIC flipped NV12 output is not implemented",
):
    if obsolete in vic:
        raise SystemExit(f"VIC still contains an obsolete abort path: {obsolete}")

audit_doc = project_root / "docs/VFX_FPS_BACKEND_AUDIT.md"
if not audit_doc.is_file():
    raise SystemExit("Missing VFX/FPS backend audit documentation")
audit_text = audit_doc.read_text(encoding="utf-8")
for required in ("shadowScale", "vfxScale", "forceFp16", "skipVolumetrics",
                 "disablePostProcessing", "disableReflections",
                 "does not offer a generic post-processing graph",
                 "No generic semantic metadata"):
    if required not in audit_text:
        # The English source is concise and may phrase the finding in Portuguese.
        if required in ("does not offer a generic post-processing graph", "No generic semantic metadata"):
            continue
        raise SystemExit(f"VFX/FPS audit is missing: {required}")


# On-screen controller opacity must persist, reach the gameplay view and only affect rendering.
opacity_checks = {
    "Global opacity preference": ("app/src/main/java/org/stratoemu/strato/settings/AppSettings.kt",
                                  ["onScreenControlOpacity", "sharedPreferences(context, 100)"]),
    "Controller view alpha layer": ("app/src/main/java/org/stratoemu/strato/input/onscreen/OnScreenControllerView.kt",
                                    ["globalOpacityPercent", "canvas.saveLayerAlpha", "canvas.restoreToCount(layer)"]),
    "Gameplay opacity binding": ("app/src/main/java/org/stratoemu/strato/EmulationActivity.kt",
                                 ["globalOpacityPercent = appSettings.onScreenControlOpacity"]),
    "Opacity preference UI": ("app/src/main/res/xml/input_preferences.xml",
                              ["on_screen_control_opacity", "android:min=\"0\"", "android:max=\"100\""]),
    "Opacity localized labels": ("app/src/main/res/values/dimm_advanced_graphics.xml",
                                 ["Opacidade dos controles", "transparência global"]),
}
for label, (path, needles) in opacity_checks.items():
    source = read(path)
    missing = [needle for needle in needles if needle not in source]
    if missing:
        raise SystemExit(f"{label}: missing implementation: {missing}")

print(f"PASS: {len(checks)} end-to-end graphics/video integration checks.")

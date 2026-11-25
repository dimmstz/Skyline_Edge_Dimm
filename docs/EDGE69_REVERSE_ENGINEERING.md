# Relatório de engenharia reversa — Skyline Edge 69

## Identificação e escopo

Inspeção estática e somente leitura do APK de referência `edge-69.apk`. Este documento não afirma que o código-fonte original foi recuperado.

| Item | Resultado observado |
|---|---:|
| APK | 27.103.127 bytes |
| Entradas ZIP | 1.544 |
| DEX | `classes.dex`, versão 039, 9.531.224 bytes |
| Classes totais no DEX | 6.389 |
| Classes em `emu.skyline` | 609 |
| Biblioteca principal | `lib/arm64-v8a/libskyline.so`, 10.083.000 bytes |
| Arquitetura | ELF64 / AArch64 |
| Build ID de `libskyline.so` | `60b260a3cc9a45449faa45f014d73fdeb86a583b` |

## Componentes identificados

- `MainActivity`, `MainViewModel`, `MainState`: tela principal e estado da biblioteca.
- `EmulationActivity`: atividade de execução e superfície gráfica.
- `RomProvider`, `loader.RomFile`, `KeyReader`: seleção de jogos e importação de arquivos/chaves.
- `settings.NativeSettings`, `settings.EmulationSettings`: configurações do núcleo.
- `utils.GpuDriverHelper`, `preference.GpuDriverActivity`: informações e gerenciamento de drivers gráficos.
- `input.InputHandler`: controles, eixos, movimento e toque.

Os subpacotes próprios incluem `input`, `preference`, `adapter`, `utils`, `databinding`, `applet`, `settings`, `data`, `views`, `loader`, `emulation`, `di` e `provider`.

## JNI e núcleo nativo

Sete métodos nativos próprios foram identificados no DEX:

```
InputHandler.Companion.setMotionState(int, int, ByteBuffer)
InputHandler.Companion.setAxisValue(int, int, int)
InputHandler.Companion.setButtonState(int, long, boolean)
InputHandler.Companion.setController(int, int, int)
InputHandler.Companion.setTouchState(int[])
InputHandler.Companion.updateControllers()
NativeSettings.Companion.setLogLevel(int)
```

A biblioteca principal exporta 19 símbolos JNI. Entre eles:

- `EmulationActivity.executeApplication`, `setSurface`, `stopEmulation`, `changeAudioStatus`, `updatePerformanceStatistics`.
- `SkylineApplication.initializeLog`.
- `RomFile.populate`.
- `NativeSettings.updateNative` e `NativeSettings.Companion.setLogLevel`.
- `GpuDriverHelper.getSystemDriverInfo`, `supportsCustomDriverLoading`, `supportsForceMaxGpuClocks`, `forceMaxGpuClocks`.
- Seis entradas JNI para o sistema de controles.

Dependências dinâmicas observadas: `libvulkan.so`, `libandroid.so`, `libOpenSLES.so`, `liblog.so`, `libm.so`, `libc.so` e `libdl.so`. Isso confirma dependência de Vulkan e OpenSL ES, mas não comprova desempenho ou compatibilidade em um dispositivo específico.

## Plano técnico para o Galaxy M23

1. Decompilar e revisar os fluxos de `EmulationActivity`, `NativeSettings`, `GpuDriverHelper`, `RomFile` e `InputHandler`.
2. Comparar as classes com uma base Skyline pública e compatível com a licença, sem assumir equivalência exata com Edge 69.
3. Mapear chamadas JNI e pontos de entrada da biblioteca nativa.
4. Integrar o núcleo real ao novo aplicativo Android ARM64.
5. Medir FPS sustentado, frametime, temperatura, memória, cache/compilação de shaders e estabilidade no M23 (Snapdragon 750G / Adreno 619).

O primeiro perfil deve priorizar resolução interna ajustável (incluindo 0,5x), cache persistente de shaders e redução de trabalho redundante na renderização. Forçar clocks continuamente pode aumentar a temperatura e causar throttling; deve ser experimental, não padrão garantido.

## Limitações

- Metadados DEX, nomes de classes, assinaturas JNI e símbolos exportados não equivalem ao código-fonte Kotlin/C++.
- `libskyline.so` está stripped; análise de símbolos e strings não substitui desassemblagem/decompilação nativa.
- O app atual ainda é um scaffold e não contém o núcleo de emulação.
- Build verde do scaffold não comprova que jogos iniciam ou rodam.
- Reutilização de código deve respeitar licenças, atribuições e direitos de terceiros.

## Reproduzir a auditoria

O script `tools/edge69_apk_audit.py` usa a biblioteca padrão do Python para ler ZIP/DEX. Com `readelf` instalado, também coleta arquitetura ELF, dependências e exports JNI.

```bash
python3 tools/edge69_apk_audit.py /caminho/edge-69.apk --output edge69-audit.json
```

# Correlação do Edge 69 com a base Skyline pública

## Resultado

Foi localizada uma correspondência estrutural forte entre o APK Edge 69 analisado e o código-fonte Android/C++ do repositório público [im030/skyline-emu](https://github.com/im030/skyline-emu).

A comparação dos símbolos JNI observados no APK com os arquivos C++ da base pública encontrou os mesmos nomes e classes Java/Kotlin. Os pontos de correspondência incluem:

| Camada | Símbolos observados no APK | Arquivo-fonte correspondente |
|---|---|---|
| Inicialização e execução | `SkylineApplication.initializeLog`, `EmulationActivity.executeApplication`, `stopEmulation`, `setSurface`, `changeAudioStatus`, `updatePerformanceStatistics` | [emu_jni.cpp](https://github.com/im030/skyline-emu/blob/master/app/src/main/cpp/emu_jni.cpp) |
| Controles | `InputHandler.Companion.setController`, `updateControllers`, `setButtonState`, `setAxisValue`, `setMotionState`, `setTouchState` | [emu_jni.cpp](https://github.com/im030/skyline-emu/blob/master/app/src/main/cpp/emu_jni.cpp) |
| Configurações nativas | `NativeSettings.updateNative`, `NativeSettings.Companion.setLogLevel` | [emu_jni.cpp](https://github.com/im030/skyline-emu/blob/master/app/src/main/cpp/emu_jni.cpp) |
| Importação de jogos | `RomFile.populate` | [loader_jni.cpp](https://github.com/im030/skyline-emu/blob/master/app/src/main/cpp/loader_jni.cpp) |
| Driver gráfico | `GpuDriverHelper.getSystemDriverInfo`, `supportsCustomDriverLoading`, `supportsForceMaxGpuClocks`, `forceMaxGpuClocks` | [driver_jni.cpp](https://github.com/im030/skyline-emu/blob/master/app/src/main/cpp/driver_jni.cpp) |

A árvore Kotlin também contém classes com os mesmos nomes e pacotes identificados no DEX, incluindo:

- [EmulationActivity.kt](https://github.com/im030/skyline-emu/blob/master/app/src/main/java/emu/skyline/EmulationActivity.kt)
- [MainActivity.kt](https://github.com/im030/skyline-emu/blob/master/app/src/main/java/emu/skyline/MainActivity.kt)
- [MainViewModel.kt](https://github.com/im030/skyline-emu/blob/master/app/src/main/java/emu/skyline/MainViewModel.kt)
- [InputHandler.kt](https://github.com/im030/skyline-emu/blob/master/app/src/main/java/emu/skyline/input/InputHandler.kt)
- [NativeSettings.kt](https://github.com/im030/skyline-emu/blob/master/app/src/main/java/emu/skyline/settings/NativeSettings.kt)
- [RomFile.kt](https://github.com/im030/skyline-emu/blob/master/app/src/main/java/emu/skyline/loader/RomFile.kt)
- [GpuDriverHelper.kt](https://github.com/im030/skyline-emu/blob/master/app/src/main/java/emu/skyline/utils/GpuDriverHelper.kt)

## O que isso permite concluir

1. O APK Edge 69 pertence à mesma família de arquitetura Android/JNI da base Skyline examinada.
2. A base pública fornece implementações de referência para a ponte JNI e para os fluxos Android que antes só eram conhecidos pelos nomes no DEX.
3. O núcleo C++ da base pública inclui componentes de CPU, kernel/HLE, loader, GPU/Vulkan, áudio e serviços do sistema; não é apenas uma interface vazia.
4. A correspondência de nomes não prova que Edge 69 foi compilado exatamente daquele commit, nem que seus binários nativos são idênticos. Também não prova equivalência de comportamento ou desempenho.

## Riscos e compatibilidade

O repositório [im030/skyline-emu](https://github.com/im030/skyline-emu) é um snapshot antigo: a revisão fixada para validação é `35fb874a42cb548cbd3d66a00d65e4b2a4c1516b` (2 de maio de 2023). O projeto declara licença MPL-2.0. A árvore usa CMake/C++20, NDK 25.0.8775105, CMake 3.22.1 e vários submódulos Git (incluindo LLVM/libc++, Boost, Vulkan-Hpp, shader compiler, libadrenotools, áudio e outras bibliotecas).

Por isso, não é seguro copiar somente `libskyline.so` ou apenas os três arquivos JNI. A integração exige a árvore nativa completa, os commits exatos dos submódulos, as classes Kotlin correspondentes, recursos/manifesto e configuração de build compatível. O snapshot deve ser compilado isoladamente antes de qualquer migração para o app Dimm.

## Validação de build isolada

O workflow do Skyline Dimm ganhou a entrada manual opcional `build_reference_core`. Ao ativá-la em **Actions → Android CI and Release → Run workflow**, o CI baixa a revisão fixa acima com os submódulos recursivos, instala JDK 17, Android API 33, NDK 25.0.8775105 e CMake 3.22.1, e tenta compilar `:app:assembleFullDebug`. Se a compilação passar, publica o APK de referência no artefato separado `Skyline-Reference-Core-APK`; não cria Release e não altera o app Dimm.

Essa etapa serve para descobrir se o snapshot ainda compila em um runner atual e gerar um APK-base para teste. Ainda não é a integração do núcleo no pacote `com.dimm.skyline`.

## Próximas etapas verificáveis

1. Fixar um commit exato da base pública e validar seus submódulos.
2. Compilar o APK original da base pública em CI, ARM64, sem alterar o scaffold atual.
3. Confirmar se a build instala e abre no Galaxy M23.
4. Comparar classes/recursos e comportamento com o Edge 69, sem presumir identidade binária.
5. Só então migrar o núcleo e a camada Android para o pacote do Skyline Dimm.
6. Implementar otimizações específicas do M23 e medir FPS/frametime/temperatura em jogos reais.

## Limite atual

O repositório `Skyline_Edge_Dimm` continua com uma tela de diagnóstico mínima. Nenhum núcleo de emulação foi integrado ainda. Os workflows #20 e #21 compilaram com sucesso o scaffold, mas não executaram testes de jogos.

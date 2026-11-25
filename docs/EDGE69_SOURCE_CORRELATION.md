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


## CI validation update

The isolated reference build now uses the runner-provided Android SDK command-line tools directly. This avoids the obsolete `tools` package request made by the setup action and installs only the pinned Android 33, NDK 25.0.8775105, and CMake 3.22.1 components required by this historical source tree.


## Auditoria do vídeo das cutscenes (25/11/2026)

### Causa confirmada na revisão nativa fixada

Na revisão `im030/skyline-emu@35fb874a42cb548cbd3d66a00d65e4b2a4c1516b`, os pontos de entrada de vídeo do Host1x não implementam decodificação:

- `app/src/main/cpp/skyline/soc/host1x/classes/nvdec.cpp`: `NvDecClass::CallMethod` apenas registra métodos como desconhecidos; não decodifica H.264/VP8/VP9 nem produz quadros.
- `app/src/main/cpp/skyline/soc/host1x/classes/vic.cpp`: `VicClass::CallMethod` também só registra métodos desconhecidos; não realiza composição/formatação dos quadros.
- `app/src/main/cpp/skyline/soc/host1x/classes/host1x.cpp`: a classe geral trata syncpoints, mas não substitui os comandos NVDEC/VIC.

Isso é compatível com o sintoma observado: o áudio da sequência pode continuar enquanto a imagem do vídeo não é decodificada/apresentada. Não é evidência de defeito no codec de áudio ou de uma simples opção gráfica.

### Por que não foi aplicado um patch superficial

O Skyline Edge Dimm ainda não contém o núcleo C++/Host1x: a árvore do projeto contém somente a base Android de diagnóstico, documentação e workflows. Portanto, não existe neste repositório um arquivo NVDEC/VIC integrado que possa ser corrigido isoladamente.

Uma implementação funcional exige integrar uma pilha coerente de:
1. parsing dos métodos e estruturas de contexto NVDEC enviados pelo jogo;
2. leitura segura dos bitstreams e superfícies na memória GPU emulada;
3. decodificação H.264/VP8/VP9 compatível com os formatos usados pelo jogo;
4. sinalização correta de fences/syncpoints;
5. composição/conversão VIC e entrega da imagem ao caminho de apresentação Vulkan;
6. testes de regressão para evitar travamentos, corrupção de memória e regressões de FPS.

Foi localizado um projeto público com implementação mais completa desses componentes, mas ele usa uma arquitetura e dependências diferentes. A migração não é um transplante de dois arquivos: precisa de revisão de licença, dependências (incluindo FFmpeg), tipos de memória, sincronização e integração de renderização. Não copiar código incompatível sem essa auditoria.

### Validação de CI iniciada

A execução nativa isolada deve compilar a revisão Skyline fixada e validar o APK de referência. Isso valida a toolchain e o ponto de partida, mas **não corrige nem comprova a reprodução das cutscenes**. A confirmação final depende de integrar NVDEC/VIC e testar o Resident Evil 4 no dispositivo Android.

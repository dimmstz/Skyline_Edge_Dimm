# Auditoria técnica da integração Skyline

Data da auditoria: 2026-11-25  
Fonte analisada: `im030/skyline-emu` no commit `35fb874a42cb548cbd3d66a00d65e4b2a4c1516b`.

## 1. Resultado da inspeção

A base é um aplicativo Android completo, não uma biblioteca independente. A árvore inclui:

- Aplicativo Kotlin em `app/src/main/java/emu/skyline`.
- Manifesto, recursos, assets, shaders e componentes de interface.
- Implementação C++ em `app/src/main/cpp`.
- Build nativo em `app/CMakeLists.txt`.
- Dependências C/C++ em submódulos Git.

A build nativa cria a biblioteca compartilhada `libskyline.so` a partir de três arquivos JNI (`emu_jni.cpp`, `loader_jni.cpp`, `driver_jni.cpp`) e do núcleo C++ completo. Portanto, copiar somente o .so ou apenas os três arquivos JNI não constitui integração.

## 2. Contrato JNI que precisa ser preservado

O núcleo exporta funções JNI vinculadas aos nomes de pacote/classes abaixo:

| Classe Kotlin | Funções nativas principais |
|---|---|
| `emu.skyline.SkylineApplication` | Inicialização de logs |
| `emu.skyline.EmulationActivity` | Executar ROM, parar emulação, atualizar Surface, áudio e estatísticas |
| `emu.skyline.loader.RomFile` | Analisar/popular metadados de ROM |
| `emu.skyline.settings.NativeSettings` | Atualizar configurações nativas e nível de log |
| `emu.skyline.input.InputHandler.Companion` | Controles, eixos, movimento, toque e atualização de controles |
| `emu.skyline.utils.GpuDriverHelper.Companion` | Identificar driver Vulkan, carregamento de driver customizado e turbo KGSL |

**Decisão de migração:** preservar o namespace Kotlin/Java `emu.skyline` inicialmente. O `applicationId` Android pode ser alterado separadamente para `com.dimm.skyline`, mas não se deve renomear as classes JNI sem atualizar simultaneamente os símbolos exportados no C++.

## 3. Formatos de arquivo e execução

O carregador JNI desta revisão declara suporte a NRO, NSO, NCA, XCI e NSP. A Activity abre o arquivo via `ContentResolver`, entrega um file descriptor ao núcleo e inicia a execução numa thread dedicada. A Activity também administra a Surface de vídeo, o áudio, o ciclo de vida e a entrada.

Isso exige migrar em conjunto:
- seleção de arquivo e permissões URI/SAF;
- classes de biblioteca e metadados;
- Activity de emulação e Surface;
- configurações serializadas Kotlin/C++;
- controles touchscreen, sensores e gamepads;
- recursos, assets, shaders e provedores Android.

## 4. Requisitos confirmados na configuração original

| Item | Configuração |
|---|---|
| Android minSdk | 29 |
| Android targetSdk | 33 |
| ABI | `arm64-v8a` apenas |
| Vulkan | Feature Vulkan 1.1 obrigatória |
| Android Gradle Plugin | 7.2.2 |
| Gradle Wrapper | 7.4.2 |
| Kotlin | 1.7.21 |
| NDK | 25.0.8775105 |
| CMake | 3.22.1+ |
| C++ | C++20 |
| Native Release | `-Ofast`, LTO full |
| Namespace original | `emu.skyline` |
| Application ID original | `skyline.emu` |

O Galaxy M23 com Android 14 satisfaz a versão mínima do Android e é ARM64. Isso não comprova compatibilidade do driver Vulkan, nem desempenho ou compatibilidade de jogos; esses pontos exigem teste no aparelho.

## 5. Dependências nativas identificadas

A configuração CMake compila o núcleo com dependências de LLVM libc++/libc++abi, Boost, fmt, tzcode, LZ4, Vulkan-Hpp/Headers, Vulkan Memory Allocator, Frozen, Mbed TLS, Opus, Cubeb, Perfetto, range-v3, Sirit, libadrenotools, robin-map, thread-pool, shader-compiler e audio-core.

A árvore também inclui bibliotecas auxiliares como Oboe e outras dependências fixadas por gitlink. Os submódulos precisam ser inicializados nas revisões exatas; não atualizar automaticamente para HEAD das branches.

## 6. Incompatibilidades e riscos de integração

1. A árvore original usa AGP 7.2.2/Gradle 7.4.2, enquanto o scaffold Dimm usa Gradle 8.9/SDK 35. A migração direta para o build moderno pode quebrar plugins, CMake e dependências antigas.
2. O namespace JNI `emu.skyline` é parte do contrato binário.
3. O ID original `skyline.emu` conflita com instalações de versões originais assinadas por outra chave. O Dimm deve usar um ID próprio, por exemplo `com.dimm.skyline`.
4. O Manifesto original exige Vulkan 1.1. É necessário verificar a capacidade real reportada pelo driver do aparelho antes de habilitar a instalação como compatível.
5. O recurso de turbo GPU depende de KGSL/adrenotools. Não deve ser forçado por padrão: pode aumentar consumo e temperatura e não garante FPS sustentado.
6. O projeto usa várias bibliotecas nativas e assets. O .so isolado não é suficiente.
7. A base analisada é uma revisão pública antiga e correlacionada ao Edge 69; não há prova de que seja exatamente a revisão usada para compilar o APK Edge 69 enviado.

## 7. Pipeline de validação criado

O workflow `.github/workflows/skyline-core-validation.yml` compila a fonte fixada a partir do submódulo, restaura os dois espelhos de dependências históricas removidas, usa JDK 17 + NDK 25 + CMake 3.22.1 e valida o APK Release, assinatura e presença de `lib/arm64-v8a/libskyline.so`.

A execução do workflow é a validação de compilação da fonte original. Mesmo com sucesso, ela não prova que o código já foi migrado para o app Dimm nem que jogos executam no M23.

## 8. Próxima sequência de implementação

1. Obter build verde do workflow de integração.
2. Auditar diferenças entre o scaffold Dimm e a árvore completa original.
3. Migrar o app completo preservando namespace JNI e recursos.
4. Separar o applicationId Dimm e atualizar authorities/identificadores de integração.
5. Integrar os perfis de hardware de forma gradual e conservadora.
6. Compilar e testar instalação, inicialização do núcleo, leitura de jogos e controles.
7. Testar áudio, Vulkan, estabilidade e FPS sustentado no M23.
8. Publicar uma versão de teste apenas após os testes funcionais mínimos.

## Licença

A fonte Skyline declara MPL-2.0. Preservar os avisos SPDX/copyright existentes e incluir a licença e as fontes correspondentes em qualquer distribuição derivada do núcleo. As licenças de cada submódulo também devem ser respeitadas.

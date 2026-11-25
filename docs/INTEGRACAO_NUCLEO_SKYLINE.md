# Integração do núcleo Skyline — etapa 1

## Estado

Esta branch inicia a integração de forma reproduzível e reversível. A fonte pública Skyline foi adicionada como submódulo Git, fixada no commit:

`35fb874a42cb548cbd3d66a00d65e4b2a4c1516b`

Origem: https://github.com/im030/skyline-emu

Licença declarada pela base: MPL-2.0. As dependências continuam fixadas nos gitlinks originais. Dois endereços históricos removidos (Sirit e Shader Compiler) já são espelhados no workflow de compilação de referência; ao inicializar o submódulo, pode ser necessário aplicar os mesmos espelhos antes de `git submodule update --init --recursive`.

## Por que ainda não é o emulador Dimm final

O módulo Android atual em `app/` é um scaffold Kotlin com identificador `com.dimm.skyline`. O projeto Skyline importado é um aplicativo Android independente, com Gradle/AGP, JNI, C++ e bibliotecas nativas próprias. Não é seguro copiar somente `libskyline.so`: a biblioteca depende do contrato JNI, das demais bibliotecas nativas, dos assets e do ciclo de vida do app original.

## Próximas etapas técnicas

1. Compilar a fonte vendorizada exatamente no commit fixado, com submódulos e toolchain históricos.
2. Fazer inventário de módulos Gradle, bibliotecas nativas, assets, permissões e classes JNI.
3. Escolher uma estratégia de integração que preserve o build moderno Dimm sem misturar versões incompatíveis do AGP/Gradle.
4. Migrar o aplicativo Android completo e trocar o applicationId para `com.dimm.skyline` apenas após revisar conflitos de recursos e componentes.
5. Adaptar SAF/URI, seleção de ROM, controllers, áudio e Surface/Vulkan.
6. Criar os perfis de hardware e ajustes específicos para Adreno 619.
7. Validar builds e executar testes reais no aparelho. A CI não consegue provar compatibilidade de jogos nem FPS sustentado sem testes em hardware.

## Comandos de checkout

```bash
git submodule update --init --recursive
```

Se a inicialização falhar por URLs históricos removidos, configure os espelhos Sirit e Shader Compiler conforme `.github/workflows/android-build.yml` antes de atualizar os submódulos.

**Não publicar este estado como versão final:** a inclusão da fonte não integra automaticamente o núcleo ao scaffold e não constitui uma build funcional do emulador.

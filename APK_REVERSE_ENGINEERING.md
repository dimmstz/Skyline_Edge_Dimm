# Análise técnica do APK Edge 69

## Identificação do pacote analisado

- Arquivo analisado: `edge-69.apk`
- Tamanho: 27.103.127 bytes
- SHA-256: `354b06220688bd1a8cfe8cece607b2005e09f892f2cc49070edbe3ae46404ae`
- Entradas ZIP: 1.544
- DEX: `classes.dex` (9.531.224 bytes; DEX 039)
- Classes do pacote `emu.skyline` identificadas na tabela DEX: 609
- ABI nativa observada: `arm64-v8a`

## Estrutura Android identificada

O DEX preserva nomes de classes e pacotes. Entre os componentes próprios identificados:

- `emu.skyline.MainActivity`
- `emu.skyline.EmulationActivity`
- `emu.skyline.MainViewModel`
- `emu.skyline.SkylineApplication`
- `emu.skyline.KeyReader`
- `emu.skyline.RomProvider`
- `emu.skyline.settings.GlobalSettingsFragment`
- `emu.skyline.settings.GameSettingsFragment`
- `emu.skyline.settings.EmulationSettings`
- `emu.skyline.preference.GpuDriverActivity`
- `emu.skyline.preference.GpuDriverPreference`
- `emu.skyline.input.ControllerActivity`
- `emu.skyline.input.onscreen.OnScreenEditActivity`

Também foram encontrados componentes de gerenciamento de drivers gráficos, configurações globais e por jogo, importação de chaves, carregamento de ROMs, controles e interface de emulação.

## Bibliotecas nativas encontradas

Todas as bibliotecas abaixo estão no diretório `lib/arm64-v8a/` do APK:

| Biblioteca | Tamanho |
|---|---:|
| `libskyline.so` | 10.083.000 bytes |
| `libhook_impl.so` | 456.104 bytes |
| `librenderscript-toolkit.so` | 387.256 bytes |
| `libgsl_alloc_hook.so` | 4.232 bytes |
| `libmain_hook.so` | 4.232 bytes |
| `libfile_redirect_hook.so` | 3.968 bytes |

A biblioteca principal é ELF64/AArch64. A tabela ELF consultada contém `.dynsym`, mas não apresenta `.symtab` nem seções de depuração; portanto, os nomes de funções e a lógica nativa não podem ser recuperados integralmente apenas por extração de strings.

## Relação com o código-fonte Skyline

Foi localizado um espelho público do projeto Skyline em `https://github.com/im030/skyline-emu`, declarado sob MPL-2.0. A árvore de código contém classes Kotlin com o mesmo pacote e nomes centrais observados no DEX, como `emu.skyline.MainActivity` e `emu.skyline.EmulationActivity`.

Esse repositório é uma referência de código-fonte da família Skyline, não uma prova de que cada arquivo corresponda exatamente ao Edge 69. A versão Edge pode conter alterações próprias. Qualquer integração deve preservar os avisos MPL-2.0, atribuições e arquivos de licença, e deve ser comparada com o APK antes de substituir o scaffold atual.

## Limites desta etapa

- A extração ZIP recupera recursos e binários originais, não transforma bytecode DEX em Kotlin/Java editável.
- O scaffold Kotlin atualmente no repositório é código novo e mínimo, não código original decompilado.
- A biblioteca `libskyline.so` ainda precisa de análise nativa específica.
- A build do scaffold verifica apenas a configuração de compilação Android; não comprova que o emulador original foi reconstruído.

## Próximos passos técnicos

1. Concluir a decompilação Java/Kotlin do DEX e revisar manualmente as classes críticas.
2. Decodificar o Manifest e os recursos compilados.
3. Comparar os fontes do espelho MPL-2.0 com os componentes encontrados no DEX.
4. Identificar as modificações Edge 69 e as chamadas JNI.
5. Reintegrar os componentes de forma incremental e testar em dispositivo ARM64.

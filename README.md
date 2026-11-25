# Skyline Dimm

[![Android CI and Release](https://github.com/dimmstz/Skyline_Edge_Dimm/actions/workflows/android-build.yml/badge.svg?branch=main)](https://github.com/dimmstz/Skyline_Edge_Dimm/actions/workflows/android-build.yml)
[![Latest Release](https://img.shields.io/github/v/release/dimmstz/Skyline_Edge_Dimm?display_name=tag)](https://github.com/dimmstz/Skyline_Edge_Dimm/releases)

Projeto de reconstrução e estudo do aplicativo Skyline Edge 69 para Android. O repositório contém atualmente uma base Android mínima, documentação da análise do APK e automação de compilação. **Ainda não é uma reconstrução funcional do emulador.**

## Estado do projeto

- APK de referência analisado: `edge-69.apk`, 27.103.127 bytes.
- SHA-256 do APK: `354b06220688bd1a8cfe8cece607b2005e09f892f2cc49070edbe3ae46404ae`.
- 1.544 entradas ZIP identificadas na extração local.
- DEX principal: `classes.dex`.
- Bibliotecas ARM64 encontradas: `libskyline.so`, `libhook_impl.so`, `libmain_hook.so`, `libgsl_alloc_hook.so`, `libfile_redirect_hook.so` e `librenderscript-toolkit.so`.
- Package ID atual da base: `com.dimm.skyline`.
- Min SDK: Android 6.0 (API 23); compile/target SDK: API 35.
- JDK: 17; Gradle usado no CI: 8.9.

A tela Kotlin atual é uma implementação nova de diagnóstico. Não é código original recuperado do APK. Foi encontrada uma correspondência dos 19 pontos JNI exportados com a base pública Skyline; veja [a correlação de código-fonte](docs/EDGE69_SOURCE_CORRELATION.md). Essa base é antiga e ainda precisa ser compilada e validada antes da integração.

Consulte [APK_REVERSE_ENGINEERING.md](APK_REVERSE_ENGINEERING.md) para os achados técnicos iniciais, [docs/EDGE69_REVERSE_ENGINEERING.md](docs/EDGE69_REVERSE_ENGINEERING.md) para o mapeamento DEX/JNI/ELF e [docs/EDGE69_SOURCE_CORRELATION.md](docs/EDGE69_SOURCE_CORRELATION.md) para a comparação com a implementação pública. O script [tools/edge69_apk_audit.py](tools/edge69_apk_audit.py) reproduz a auditoria estrutural usando Python padrão.

## Downloads

A cada execução válida do workflow, o GitHub Actions publica um artefato ZIP com:

| Arquivo | Finalidade |
|---|---|
| `SkylineDimm-debug.apk` | APK de depuração assinado automaticamente pelo Android Gradle Plugin; indicado para instalação e teste. |
| `SkylineDimm-release.apk` | APK de release. Será assinado se as credenciais de assinatura estiverem configuradas; caso contrário, ficará sem assinatura. |
| `SkylineDimm-release.aab` | Android App Bundle, assinado quando as credenciais estiverem configuradas. |
| `SHA256SUMS.txt` | Hash SHA-256 dos arquivos publicados. |
| `SIGNING_STATUS.txt` | Informa se a variante release foi assinada. |

Os artefatos temporários de Actions expiram após 30 dias. Releases criadas por tag permanecem na página [Releases](https://github.com/dimmstz/Skyline_Edge_Dimm/releases).

**Atenção:** sem assinatura de release configurada, use o APK debug para testar no aparelho. O APK release sem assinatura não pode ser instalado diretamente e o AAB não está pronto para publicação na Play Store.

## Compilar localmente

Requisitos: JDK 17, Android SDK com plataforma 35 e Build Tools 35.0.0, Gradle 8.9.

Na raiz do repositório:

```bash
gradle --version
gradle --no-daemon clean testDebugUnitTest assembleDebug assembleRelease bundleRelease
```

Saídas principais:

- `app/build/outputs/apk/debug/app-debug.apk`
- `app/build/outputs/apk/release/app-release-unsigned.apk` (quando não há assinatura)
- `app/build/outputs/bundle/release/app-release.aab`

## GitHub Actions: fluxo completo

Arquivo: [`.github/workflows/android-build.yml`](.github/workflows/android-build.yml)

O workflow executa automaticamente em:

- Push para `main`.
- Pull requests.
- Push de tags no padrão `v*`.
- Execução manual em **Actions → Android CI and Release → Run workflow**.

Etapas do pipeline:

1. Checkout do código.
2. Configuração do JDK 17.
3. Instalação/verificação das Android Command-line Tools e SDK API 35.
4. Configuração do Gradle 8.9.
5. Execução dos testes unitários disponíveis.
6. Compilação APK debug, APK release e AAB.
7. Validação dos arquivos, Manifest, estrutura AAB e assinatura quando habilitada.
8. Geração dos hashes SHA-256.
9. Upload dos artefatos.
10. Publicação de GitHub Release quando executado por uma tag `v*` ou quando solicitado no disparo manual.\n11. Auditoria opcional do APK Edge 69 quando a execução manual recebe `apk_url`; o JSON é anexado aos artefatos.

### Criar uma tag e uma Release

Opção automática pelo GitHub:

1. Abra a aba **Actions** do repositório.
2. Selecione **Android CI and Release**.
3. Clique em **Run workflow** na branch `main`.
4. Marque `publish_release`.
5. Informe a tag, por exemplo `v0.1.0`.
6. Execute. O workflow compila, cria a tag caso ainda não exista e publica APK, AAB e checksums.

### Executar a engenharia reversa do APK Edge 69

1. Disponibilize o arquivo original `edge-69.apk` como asset de uma GitHub Release pública que você tenha autorização para usar.
2. Copie a URL direta do asset (não a página HTML da Release).
3. Em **Actions → Android CI and Release → Run workflow**, cole a URL no campo opcional `apk_url`.
4. O pipeline executa a auditoria DEX/ELF e o JADX 1.5.7, gerando `edge69-audit.json` e `jadx-source.zip` nos artefatos da execução.

O APK não é armazenado no repositório. A etapa de decompilação só é executada quando `apk_url` é preenchido.

Também é possível criar e enviar uma tag Git manualmente:

```bash
git tag v0.1.0
git push origin v0.1.0
```

O push da tag dispara o pipeline e publica os arquivos na Release correspondente.

Para solicitar uma versão a partir de um commit na branch `main`, use a mensagem de commit no formato `release: v0.1.0`. Após a build e as validações, o workflow cria a tag e a GitHub Release automaticamente. A versão deve seguir o padrão semântico `vMAJOR.MINOR.PATCH`.

### Assinatura estável para releases (recomendado)

Para distribuir atualizações instaláveis sobre versões anteriores ou publicar na Play Store, configure os seguintes **GitHub Actions Secrets** em **Settings → Secrets and variables → Actions**:

- `ANDROID_KEYSTORE_BASE64`: arquivo keystore codificado em Base64.
- `ANDROID_STORE_PASSWORD`: senha do keystore.
- `ANDROID_KEY_ALIAS`: alias da chave.
- `ANDROID_KEY_PASSWORD`: senha da chave.

Exemplo local para converter o keystore em Base64:

```bash
base64 -w 0 release-key.jks
```

Nunca coloque keystore, senhas ou chaves privadas no Git. Sem esses quatro secrets, o pipeline continua compilando e publica o APK debug assinado para testes, mas a variante release fica sem assinatura. Use sempre o mesmo keystore para manter a possibilidade de atualização entre versões.

## Estrutura

```text
.
├── .github/workflows/android-build.yml
├── app/
│   ├── build.gradle.kts
│   └── src/main/
│       ├── AndroidManifest.xml
│       └── java/com/dimm/skyline/MainActivity.kt
├── APK_ANALYSIS.json
├── APK_REVERSE_ENGINEERING.md
├── build.gradle.kts
├── gradle.properties
└── settings.gradle.kts
```

## Próximas etapas de engenharia reversa

1. Decompilar o DEX e revisar as classes principais.
2. Decodificar Manifest e recursos Android do APK.
3. Mapear JNI, símbolos e dependências de `libskyline.so`.
4. Comparar os componentes com fontes Skyline compatíveis e respeitar suas licenças.
5. Reintegrar módulos progressivamente.
6. Concluir a decompilação de bytecode e análise da biblioteca nativa stripped.\n7. Integrar o núcleo real ao app Android (Kotlin/JNI/C++/Vulkan), substituindo o scaffold atual.\n8. Validar inicialização, drivers gráficos, FPS sustentado, frametime, temperatura e execução de jogos no Galaxy M23.

## Licenças e atribuições

Este repositório ainda não declara uma licença global para os arquivos novos. O APK de referência e suas bibliotecas podem ter direitos e condições de redistribuição próprios. Não publique binários extraídos sem confirmar que possui autorização.

Um espelho público da família Skyline consultado durante a análise declara MPL-2.0; isso não significa que todos os componentes do APK Edge 69 tenham a mesma licença. Preserve os avisos de copyright e licenças de cada componente utilizado.

## Aviso

Skyline Dimm é um projeto independente de estudo e reconstrução. Não é afiliado nem endossado pelos autores originais do Skyline ou por fabricantes de dispositivos.

# Skyline Dimm

Reconstrução inicial do aplicativo Android a partir do APK Edge 69 fornecido.

## Estado real da recuperação

- APK de origem: `edge-69.apk` (27.103.127 bytes).
- SHA-256: `354b06220688bd1a8cfe8cece607b2005e09f892f2cc49070edbe3ae46404ae`.
- 1.544 entradas ZIP identificadas e extraídas no pacote de reconstrução local.
- DEX: `classes.dex`.
- Bibliotecas ARM64: `libskyline.so`, `libhook_impl.so`, `libmain_hook.so`, `libgsl_alloc_hook.so`, `libfile_redirect_hook.so` e `librenderscript-toolkit.so`.

**Importante:** o código Kotlin deste repositório é uma base Android mínima criada para iniciar a reconstrução. Não é o código original decompilado. O DEX e as bibliotecas nativas são binários compilados; a recuperação completa exige decompilação, engenharia reversa nativa e validação funcional.

## Build

O workflow `.github/workflows/android-build.yml` compila APK debug, APK release e AAB em GitHub Actions. Os artefatos ficam disponíveis na execução do workflow. Tags `v*` publicam os artefatos em uma GitHub Release.

## Pacote extraído

O pacote completo com os arquivos extraídos e o APK original foi gerado separadamente como `skyline_dimm-reconstruction.zip`. Ele não está incluído neste commit porque excede o limite prático de envio de arquivos grandes pela API de conteúdo do GitHub. Não descarte o APK original.

## Próximas etapas técnicas

1. Decompilar `classes.dex` com JADX e mapear classes, pacotes e chamadas JNI.
2. Decodificar o Manifest e recursos Android.
3. Mapear símbolos e dependências das bibliotecas ARM64.
4. Recriar módulos e dependências gradualmente.
5. Validar instalação, inicialização e execução de jogos em dispositivo real.

Verifique os direitos de redistribuição antes de publicar APKs, bibliotecas ou recursos proprietários.

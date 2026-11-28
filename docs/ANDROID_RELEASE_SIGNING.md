# Assinatura permanente dos APKs Android

O Android só permite atualizar um aplicativo quando o APK novo usa o mesmo certificado de assinatura da instalação existente. Builds assinados automaticamente com a chave debug de cada runner do GitHub Actions não são atualizáveis entre execuções, porque essa chave temporária muda.

## Configuração única dos secrets

Crie uma chave de release e guarde uma cópia segura do arquivo JKS. **Não publique o JKS nem envie a chave privada ao repositório.**

```bash
keytool -genkeypair -v \
  -keystore skyline-release.jks \
  -alias skyline-dimm \
  -keyalg RSA -keysize 2048 -validity 10000
base64 -w 0 skyline-release.jks
```

No GitHub, abra **Settings → Secrets and variables → Actions → New repository secret** e cadastre os quatro secrets:

- `ANDROID_KEYSTORE_BASE64`: saída do comando base64
- `ANDROID_STORE_PASSWORD`: senha do arquivo JKS
- `ANDROID_KEY_ALIAS`: `skyline-dimm` (ou o alias escolhido)
- `ANDROID_KEY_PASSWORD`: senha da chave

O workflow valida os quatro secrets e a chave antes de compilar o APK nativo. Releases sem assinatura persistente são bloqueadas para evitar entregar APKs que não possam receber atualizações futuras.

## Importante para quem já tem o Skyline Dimm instalado

As versões anteriores foram assinadas com a chave debug temporária do runner. Como essa chave não foi preservada, não é possível reconstruir a chave privada a partir do APK. **A primeira instalação desta nova linha de assinatura exigirá desinstalar a versão antiga** (o Android apagará os dados locais do app). Depois de instalar a primeira versão assinada com o JKS permanente, as próximas atualizações poderão ser instaladas normalmente, sem desinstalar.

Se você ainda tiver o arquivo JKS original usado para assinar a instalação existente, use-o em vez de gerar uma chave nova; assim, a atualização pode preservar o app e seus dados.

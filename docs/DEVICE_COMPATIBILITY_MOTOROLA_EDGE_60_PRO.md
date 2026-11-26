# Compatibilidade do Skyline Dimm — Motorola Edge 60 Pro

Data da análise: 2026-11-26
Dispositivo-alvo: Motorola Edge 60 Pro (codinome reportado: cybert).
Fonte oficial de hardware: Motorola Support, especificações do Edge 60 Pro.

## Hardware de referência

- SoC: MediaTek Dimensity 8350 / 8350 Extreme.
- CPU: 1x Cortex-A715 até 3,35 GHz + 3x Cortex-A715 até 3,2 GHz + 4x Cortex-A510 até 2,2 GHz.
- GPU: Arm Mali-G615 MC6 (seis núcleos).
- RAM: variantes de 8 GB e 12 GB LPDDR5X, conforme mercado.
- Armazenamento: UFS 4.0.
- Tela: 2712 x 1220, 120 Hz.
- Sistema de lançamento: Android 15; a versão atualmente instalada deve ser confirmada no próprio aparelho.

O Edge 60 Pro NÃO usa Qualcomm Adreno. Portanto, caminhos proprietários Qualcomm/KGSL não podem ser presumidos nem ativados nesse aparelho.

## Compatibilidade da implementação atual

A aplicação usa Vulkan e consulta propriedades/limites da GPU no dispositivo. Isso permite executar o caminho Vulkan genérico na Mali, sem identificar o Edge como Adreno.

| Recurso | Estratégia para Edge 60 Pro |
|---|---|
| Escala de resolução interna | Caminho Vulkan genérico já existente; perfil exige reiniciar jogo |
| Mipmap LOD bias | Ajuste de sampler Vulkan com limite do dispositivo |
| Anisotropia | Aplicar somente se a extensão/feature estiver habilitada e limitar a maxSamplerAnisotropy reportada |
| Cache de shader/pipeline | Manter habilitado; cache deve continuar separado por identidade de GPU/driver |
| Frame pacing | Manter relógio de apresentação; não desativar para perseguir FPS artificial |
| Importação direta de memória Adreno | Não ativar; é específico de driver proprietário Adreno |
| Forçar clocks máximos Adreno/KGSL | Não suportado como estratégia genérica Mali; manter desligado |
| FP16 forçado | Não forçar; respeitar feature e semântica de precisão do shader |
| Shadow/VFX/volumétricos/reflexos | Permanecem nativos enquanto o backend não identificar passes/recursos com segurança |
| Vídeos/cutscenes | Não alterar NVDEC/VIC nem o caminho de apresentação de vídeo para este perfil |

## Plano de validação no aparelho

1. Instalar o APK ARM64 produzido pelo workflow.
2. Abrir Configurações > GPU e verificar no Logcat o nome real da GPU, vendor/device ID, versão Vulkan e driver.
3. Confirmar que a identificação reporta Arm/Mali e que nenhum caminho Qualcomm é ativado.
4. Executar uma mesma cena por pelo menos 3 minutos em Personalizado, FPS equilibrado e Desempenho.
5. Registrar FPS, frametime/jitter, RAM e temperatura; repetir após 10–15 minutos para avaliar throttling.
6. Testar pelo menos um jogo com vídeos/cutscenes e transparências.
7. Testar Android 15 e, caso o aparelho esteja atualizado, a versão do Android efetivamente instalada.

## Critérios de aprovação

- Sem crash, tela preta, erro Vulkan ou perda de vídeo.
- A escala interna e os samplers devem refletir os valores selecionados nos logs.
- Anisotropia deve ser limitada pelos recursos realmente expostos pelo driver.
- Nenhum recurso Adreno-only deve ser chamado em Mali.
- Não declarar ganho de FPS sem medição física comparável no Edge 60 Pro.

## Limitações

O GitHub Actions compila para ARM64, mas não reproduz o driver proprietário do Motorola, o controle térmico nem a tela do Edge 60 Pro. A compilação bem-sucedida é validação de build, não certificação física do dispositivo. O usuário deverá fornecer Logcat/medidas do Edge para confirmar a compatibilidade em execução.

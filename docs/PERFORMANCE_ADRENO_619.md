# Estratégia de desempenho sustentado — Skyline Dimm / Adreno 619

Data: 2026-11-26
Alvo prioritário: Galaxy M23, Snapdragon 750G, Adreno 619.
Fonte nativa fixada: `LukeValen/Strato-Mali-Public-Build@9249ea351ad7bd7b0e7d4a319e1ad1c56dae865c`.

## Resumo da arquitetura já existente

1. O backend possui compilação assíncrona de pipelines gráficos em `GraphicsPipelineAssembler`.
2. O backend mantém `VkPipelineCache` persistente, com arquivo separado por vendor ID, device ID, driver version e pipeline cache UUID; os dados serializados têm hash para detectar corrupção.
3. O `PipelineManager` espera a compilação assíncrona terminar antes de salvar o cache. Desativar `disableShaderCache` (isto é, manter o cache habilitado) é importante para reduzir stutter após o primeiro uso.
4. `PresentationEngine` já separa a thread de apresentação, usa uma fila de frames e aplica `GuestFrameClock` com intervalos absolutos para evitar acúmulo de jitter. A opção `disableFrameThrottling` remove esse controle e pode aumentar carga sem aumentar os frames efetivamente exibidos.
5. A escala interna é fixa durante a sessão (`const resolution::Scale resolutionScale`). A escala de apresentação/swapchain é separada. Portanto, mudar dinamicamente a escala durante um jogo exigiria redesenhar o ciclo de vida dos caches e render targets; não é seguro apenas trocar um número em runtime.

## Alterações entregues nesta etapa

### Perfis de desempenho reais

O novo seletor é aplicado antes da criação de `NativeSettings`; ele não cria um caminho gráfico fictício e reutiliza os controles existentes que já chegam ao backend Vulkan:

| Perfil | Escala interna | Mipmap LOD bias | Anisotropia |
|---|---:|---:|---:|
| Personalizado | valor escolhido | valor escolhido | valor escolhido |
| FPS equilibrado | 0,75x | +0,25 mip | 2x |
| Desempenho | 0,50x | +0,75 mip | 1x |

A resolução final da janela e a proporção da imagem não são alteradas. Passes que o backend não consegue escalar continuam em resolução nativa, conforme o comportamento existente. Os perfis exigem reiniciar o jogo. Eles não desligam cache de shader/pipeline, não desativam frame pacing, não forçam clocks máximos e não alteram NVDEC/VIC ou apresentação de vídeos.

### Diagnóstico de frame pacing

A sobreposição de desempenho passa a exibir:
- FPS medido pelo PresentationEngine;
- frametime médio em milissegundos;
- desvio médio do frametime (jitter);
- RAM do processo.

Isso permite distinguir aumento de FPS de uma melhoria real de regularidade. Os logs `[PERF]` registram escala interna, Mipmap LOD bias, anisotropia, estado do shader cache e throttling; `[VFX-OPT]` registra as capacidades Vulkan identificadas.

## Estratégia recomendada de otimização

### Prioridade 1 — reduzir fragment/pixel workload sem quebrar jogos

Usar primeiro os perfis existentes. A resolução interna menor reduz o número de pixels nos passes que suportam a transformação. Mipmap bias positivo pode selecionar mip levels menores à distância e reduzir tráfego de textura; anisotropia reduzida limita custo de filtragem em ângulos oblíquos. Isso não garante ganho em jogos limitados por CPU.

### Prioridade 2 — preservar caches e evitar recompilação durante jogo

Manter o shader cache e o pipeline cache habilitados. O código já compila pipelines de forma assíncrona e persiste o cache Vulkan por GPU/driver/UUID. Não desativar cache para tentar melhorar FPS: isso tende a aumentar travamentos de compilação, especialmente na primeira visita a cenas.

### Prioridade 3 — frame pacing e temperatura

Manter `disableFrameThrottling=false` como padrão. O relógio de apresentação existente evita submissões em rajada e mantém cadência previsível. Forçar clocks máximos é uma opção separada, suportada apenas em alguns caminhos Qualcomm/KGSL; não deve ser ligado por padrão porque pode aumentar temperatura e provocar thermal throttling, reduzindo o desempenho sustentado.

### Prioridade 4 — otimizações futuras com evidência

- Instrumentar tempos CPU/GPU por etapa antes de mexer em `executorSlotCountScale` e `executorFlushThreshold`; os dois parâmetros controlam concorrência e batching, e ajustes globais sem profiling podem piorar latência/memória.
- Avaliar ADPF/PerformanceHintManager para threads de emulação após identificar e medir os TIDs críticos. O ADPF pode ajudar o escalonamento de CPU e o controle térmico, mas não substitui otimização de GPU nem garante clock fixo.
- Avaliar resolução dinâmica apenas depois de remover a imutabilidade de `resolutionScale` e projetar invalidação/recriação de caches, recursos de textura, render targets e sincronização. Não aplicar alteração direta no swapchain.
- Auditar load/store ops, barreiras e attachments com capturas Vulkan antes de modificar render passes. Em GPUs mobile tipo tiler, tráfego de memória e round-trips para DRAM são frequentemente mais caros que aritmética isolada; entretanto, este emulador reproduz a semântica de renderização do jogo convidado, então não pode substituir load/store ops sem comprovar equivalência.

## Como medir no Galaxy M23

1. Ativar estatísticas de desempenho e selecionar o mesmo jogo/cena/tempo de teste.
2. Repetir a cena três vezes com cache aquecido para cada perfil.
3. Anotar FPS médio, frametime médio, desvio/jitter, RAM e temperatura do dispositivo.
4. Descartar o primeiro teste se estiver compilando pipelines ou carregando shaders novos.
5. Comparar a estabilidade após 10–15 minutos, não apenas os primeiros 30 segundos, para revelar throttling térmico.
6. Verificar Logcat por `[PERF]`, `[VFX-OPT]`, avisos de compilação de pipeline e erros Vulkan.

Não existe benchmark físico automatizado no GitHub Actions. Build verde comprova compilação e verificações estáticas, não ganho de FPS nem compatibilidade visual no M23.

## Referências técnicas

- Vulkan TBR best practices: https://docs.vulkan.org/guide/latest/tile_based_rendering_best_practices.html
- Android Frame Pacing / Swappy: https://developer.android.com/games/sdk/frame-pacing/
- Android Vulkan frame pacing extensions: https://developer.android.com/games/develop/vulkan/frame-pacing-extensions
- Android slow sessions, ADPF e throttling térmico: https://developer.android.com/topic/performance/issues/slow-session
- Khronos Vulkan pipeline cache: https://docs.vulkan.org/guide/latest/pipeline_cache.html
- Qualcomm Adreno tile memory e bandwidth: https://www.qualcomm.com/developer/blog/2026/05/high-performance-memory-extension-optimize-memory

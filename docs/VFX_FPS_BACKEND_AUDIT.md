# Auditoria técnica — Otimização Gráfica (VFX e FPS)

Data: 2026-11-26
Fonte nativa auditada: `LukeValen/Strato-Mali-Public-Build`, revisão fixa `9249ea351ad7bd7b0e7d4a319e1ad1c56dae865c`.
Projeto de integração: `dimmstz/Skyline_Edge_Dimm`, branch `feat/advanced-graphics-video-m23`.

## Arquitetura encontrada

O workflow baixa a árvore nativa Strato/Mali em uma revisão fixa e aplica os patches do Skyline Dimm antes de compilar. O diretório `app/src/main/cpp/skyline/` contém o backend Vulkan real; o repositório de integração, isoladamente, não contém essa árvore inteira.

Fluxo de configurações existente:

1. `EmulationSettings.kt` persiste preferências globais e por jogo com `SharedPreferences`.
2. `NativeSettings.kt` constrói o objeto serializável que é enviado à biblioteca nativa.
3. `AndroidSettings::Update()` em `skyline/common/android_settings.h` lê os campos por JNI (`KtSettings`).
4. `skyline::Settings` expõe configurações nativas; `GPU`, `ShaderManager` e demais componentes consomem essas configurações.

A interface usa `PreferenceFragmentCompat` e os recursos XML `emulation_preferences.xml`; a navegação de seções é filtrada por chaves em `GlobalSettingsFragment.kt`.

## Renderização e limites identificados

- `GPU` inicializa Vulkan, consulta propriedades e recursos por `TraitManager`, cria o dispositivo, a fila, o agendador, a apresentação, os caches de render pass/framebuffer, o gerenciador de texturas e os gerenciadores de pipelines.
- `Maxwell3D` converte estado de comandos do Switch em estado de pipeline Vulkan. `ColorRenderTargetState` e `DepthRenderTargetState` obtêm dimensões/formato dos alvos de renderização a partir dos registradores e da memória do jogo.
- `ShaderManager` traduz programas Maxwell de cada jogo para SPIR-V. O código recebe informações de capacidades como `supportsFloat16`; o compilador preserva a semântica e a precisão do shader convidado.
- `FramebufferCache` e `RenderPassCache` armazenam recursos derivados dos attachments e render passes enviados pelo jogo. A apresentação final é gerenciada separadamente por `PresentationEngine`.
- A árvore não oferece um grafo genérico de pós-processamento com nós nomeados como Bloom, SSR, Depth of Field ou volumetric fog, nem metadados semânticos confiáveis que identifiquem shadow maps, partículas, água ou reflexos nos render targets arbitrários dos jogos.

## Resultado por opção solicitada

| Opção | Resultado da auditoria | Decisão segura |
|---|---|---|
| `shadowScale` | Não há classificador semântico confiável de shadow maps. Alvos de profundidade também são usados para Z-buffer, depth prepass e outras operações. | Não alterar dimensões de depth/color attachments com heurísticas. |
| `vfxScale` | O backend recebe draws e attachments genéricos; transparência/blending não prova que o draw seja partícula ou VFX. | Não reduzir render targets ou viewport de draws transparentes. |
| `forceFp16` | `TraitManager` consulta `VK_KHR_shader_float16_int8`/feature `shaderFloat16`; `ShaderManager` passa essa capacidade ao tradutor. Isso permite FP16 quando exigido pela semântica do shader convidado, não uma conversão segura de operações FP32 arbitrárias. | Não adicionar demotion FP16 global nem alegar ganho automático. |
| `skipVolumetrics` | Não há identificação semântica confiável de fog/god rays/volumetrics nos shaders ou passes. | Manter os shaders e passes originais. |
| `disablePostProcessing` | Não há cadeia de pós-processamento separada com passes nomeados; filtros podem estar embutidos em shaders e draws normais. | Não suprimir pipelines ou draws por heurística. |
| `disableReflections` | SSR/reflexos planares/água podem estar integrados em shaders, compute e render targets indistinguíveis de outros usos. | Não desabilitar shaders, imagens ou passes sem classificação por jogo. |

## O que foi implementado nesta etapa

Foi adicionado diagnóstico de capacidades reais no início da sessão Vulkan e no início da configuração do compilador de shaders. Os registros `[VFX-OPT]` incluem GPU, vendor/device ID, versão do driver/API, suporte a shaderFloat16, anisotropia e limites de imagem. O log também informa explicitamente que as cinco classes de efeitos não são controláveis com segurança nesta revisão.

Esses registros são diagnóstico, não alegação de que as opções de efeito foram aplicadas. Nenhum controle fictício foi adicionado à interface. As otimizações já existentes de escala de resolução interna, mipmap LOD bias e anisotropia continuam separadas e não são alteradas por esta auditoria.

## Próxima etapa necessária para controles reais de VFX

A implementação segura requer instrumentação e classificação verificável por jogo: capturar metadados de attachments, estado de pipeline, shader hash, formato/uso do recurso e sequência de passes; validar os alvos identificados em títulos de teste; e somente então aplicar recursos auxiliares com dimensões próprias, sincronização e cache de descritores. Para FP16, é necessário um passe SPIR-V consciente de tipos/estágios e regras de precisão, seguido de testes de conformidade por shader. A arquitetura genérica atual não fornece evidência suficiente para ativar esses seis toggles globalmente.

## Integridade de vídeo

Esta etapa não altera NVDEC, VIC, FFmpeg, a apresentação de frames de vídeo, o swapchain, render-pass/framebuffer cache ou dimensões dos attachments. Isso evita introduzir regressões nas cutscenes enquanto os efeitos ainda não podem ser classificados.

#!/usr/bin/env python3
"""Generate a Brazilian Portuguese Android resource overlay without changing source locales."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

if len(sys.argv) != 2:
    raise SystemExit("Uso: generate_pt_br_localization.py <raiz-do-Strato>")
root = Path(sys.argv[1]).resolve()
base = root / "app/src/main/res/values"
locale = root / "app/src/main/res/values-pt-rBR"
locale.mkdir(parents=True, exist_ok=True)

# Every key below is an Android resource name; placeholders and technical identifiers
# are deliberately preserved. Missing keys remain available through Android's English fallback.
STRINGS = {
"mali_kofi_title":"Apoie o Strato Mali 🫐",
"mali_kofi_message":"O desenvolvedor do Strato Mali preparou este aplicativo para você. Se quiser, ofereça um café pelo Ko-fi. ☕🫐",
"mali_kofi_button":"Ko-fi","mali_kofi_not_now":"Agora não","mali_kofi_open_failed":"Não foi possível encontrar um navegador para abrir o Ko-fi.",
"search":"Pesquisar","error":"Ocorreu um erro","copied_to_clipboard":"Copiado para a área de transferência",
"emulator":"Emulador","enabled":"Ativado","settings":"Configurações","share_logs":"Compartilhar registros","refresh":"Atualizar",
"log_share_prompt":"Compartilhar arquivo de registro","logs_not_found":"Nenhum registro foi criado durante a última execução",
"all":"Todos","metadata_missing":"Metadados ausentes","icon":"Ícone","no_rom":"Nenhuma ROM encontrada","pin":"Fixar","play":"Jogar",
"save_management":"Gerenciar salvamentos","delete_save":"Excluir salvamento","import_save":"Importar","export_save":"Exportar",
"save_export_success":"Arquivo ZIP de salvamento exportado com sucesso","save_export_failed":"Não foi possível exportar o ZIP de salvamento",
"searching_roms":"Procurando jogos","invalid_file":"Arquivo inválido","missing_title_key":"Chave de título ausente",
"incomplete_prod_keys":"Chaves de produção incompletas","pause":"Pausar","mute":"Silenciar",
"content":"Conteúdo","open_data_directory":"Abrir diretório interno",
"open_data_directory_summary":"Abre o diretório interno do Skyline Dimm em um gerenciador de arquivos",
"open_data_directory_failed":"Não foi possível encontrar um gerenciador de arquivos para abrir o diretório interno do Skyline Dimm",
"search_location":"Pesquisar local","keys":"Chaves","prod_keys":"Chaves de produção","title_keys":"Chaves de título",
"import_keys_success":"Chaves importadas com sucesso","import_keys_invalid_input_path":"O caminho informado para as chaves é inválido",
"import_keys_invalid_keys":"As chaves que você tentou importar são inválidas",
"import_keys_delete_previous_failed":"Falha ao excluir as chaves instaladas atualmente",
"import_keys_move_failed":"Falha ao mover as chaves para o diretório interno",
"firmware":"Firmware","import_firmware_in_progress":"Instalando firmware","import_firmware_success":"Firmware importado com sucesso",
"import_firmware_failure":"Falha ao instalar o firmware",
"import_firmware_invalid_contents":"O pacote de firmware informado não contém um firmware válido",
"firmware_keys_needed":"São necessárias chaves válidas para instalar o firmware","firmware_not_installed":"Nenhum firmware instalado",
"appearance":"Aparência","theme":"Tema","use_material_you":"Usar Material You",
"use_material_you_desc_off":"Serão usadas as cores do Skyline Dimm","use_material_you_desc_on":"Será usado o Material You",
"app_language":"Idioma do aplicativo","app_language_default":"Usar idioma padrão do sistema",
"layout_type":"Layout de exibição dos jogos","sort_apps_by":"Ordem de classificação dos jogos",
"select_action":"Sempre mostrar informações do jogo",
"select_action_desc_on":"As informações do jogo serão exibidas ao tocar nele",
"select_action_desc_off":"As informações do jogo serão exibidas somente ao tocar e segurar nele",
"filter_invalid_files_desc_off":"Mostrar arquivos identificados como inválidos",
"filter_invalid_files_desc_on":"Ocultar arquivos identificados como inválidos","filter_invalid_files":"Ocultar arquivos inválidos",
"game":"Jogo","use_custom_settings":"Ativar configurações personalizadas",
"use_custom_settings_desc_on":"As configurações personalizadas estão ativadas para este jogo",
"use_custom_settings_desc_off":"As configurações personalizadas estão desativadas para este jogo",
"export_custom_settings":"Exportar configurações personalizadas como texto",
"export_custom_settings_desc":"Copie um texto com suas configurações atuais para compartilhar na internet",
"reset_custom_settings":"Redefinir configurações personalizadas",
"reset_custom_settings_desc":"Restaurar as configurações personalizadas para os valores padrão",
"reset_settings_warning":"Tem certeza de que deseja restaurar todas as configurações padrão? <b>As configurações atuais serão perdidas</b>",
"copy_global_settings":"Copiar configurações globais","copy_global_settings_desc":"Copiar as configurações globais para este jogo",
"copy_global_settings_warning":"Tem certeza de que deseja copiar as configurações globais para este jogo? <b>As configurações atuais serão perdidas</b>",
"system":"Sistema","use_docked":"Usar modo de console na base",
"handheld_enabled":"O sistema simulará o modo portátil","docked_enabled":"O sistema simulará o modo de console na base",
"username":"Nome de usuário","profile_picture":"Foto do perfil","profile_picture_not_selected":"Nenhuma imagem selecionada",
"system_language":"Idioma do sistema","system_region":"Região do sistema","internet":"O sistema poderá acessar a internet",
"display":"Tela","graphics_quality":"Qualidade gráfica e texturas","graphics_drivers":"Drivers gráficos","performance_stability":"Desempenho e estabilidade","perf_stats":"Mostrar estatísticas de desempenho",
"perf_stats_desc_off":"As estatísticas de desempenho não serão exibidas",
"perf_stats_desc_on":"As estatísticas de desempenho serão exibidas no canto superior esquerdo",
"max_refresh_rate":"Usar taxa máxima de atualização da tela",
"max_refresh_rate_enabled":"Define a maior taxa de atualização possível (pode causar problemas na maioria dos jogos)",
"max_refresh_rate_disabled":"Define a taxa de atualização da tela em 60 Hz",
"screen_orientation":"Orientação da tela","aspect_ratio":"Proporção da tela",
"respect_display_cutout":"Respeitar recorte da tela",
"respect_display_cutout_enabled":"Não desenhar elementos da interface na área do recorte",
"respect_display_cutout_disabled":"Permitir elementos da interface na área do recorte",
"enable_foldable_layout":"Ativar layout para dobráveis",
"enable_foldable_layout_enabled":"Em dispositivos dobráveis, o jogo e o controle serão exibidos separadamente",
"enable_foldable_layout_disabled":"Exibir o controle sobre o jogo mesmo quando o dispositivo estiver dobrado",
"show_pause_button":"Mostrar botão de pausa","show_pause_button_disabled":"O botão de pausa não será exibido",
"show_pause_button_enabled":"O botão de pausa será exibido","audio":"Áudio","disable_audio_output":"Desativar saída de áudio",
"disable_audio_output_enabled":"A saída de áudio está desativada","disable_audio_output_disabled":"A saída de áudio está ativada",
"gpu":"GPU","gpu_driver_config":"Configuração do driver da GPU","gpu_driver_config_desc":"Driver ativo: %1$s",
"gpu_driver_config_desc_unsupported":"Seu dispositivo não oferece suporte a drivers personalizados",
"force_triple_buffering":"Forçar buffer triplo",
"triple_buffering_enabled":"Usar pelo menos três buffers na swapchain (mais FPS, porém maior atraso nos comandos)",
"triple_buffering_disabled":"Usar pelo menos dois buffers na swapchain (menos FPS, porém menor atraso nos comandos)",
"disable_frame_throttling":"Desativar limitação de quadros",
"disable_frame_throttling_enabled":"O jogo poderá enviar quadros o mais rápido possível (somente para testes de desempenho)\\n\\n<b>Observação:</b> com esta opção ativada, o FPS é medido por outro método e não deve ser comparado ao FPS com limitação ativada",
"disable_frame_throttling_disabled":"Respeitar o intervalo de quadros nativo do jogo, independentemente da taxa de atualização da tela",
"executor_slot_count_scale":"Escala de slots de execução",
"executor_slot_count_scale_desc":"Controla o número máximo de execuções simultâneas da GPU (valores maiores podem melhorar o desempenho, mas usam mais RAM)",
"executor_flush_threshold":"Limite de envio do executor","executor_flush_threshold_desc":"Controla a frequência com que o trabalho é enviado à GPU",
"use_direct_memory_import":"Usar importação direta de memória",
"use_direct_memory_import_desc":"Pode alterar o desempenho e a estabilidade em alguns jogos\\n<b>NOTA:</b> esta opção funciona somente com drivers proprietários da Adreno",
"force_max_gpu_clocks":"Forçar frequência máxima da GPU",
"force_max_gpu_clocks_desc":"Força a GPU a operar na frequência máxima possível (pode causar aquecimento excessivo e maior consumo de energia)",
"force_max_gpu_clocks_desc_unsupported":"Seu dispositivo não oferece suporte ao uso forçado da frequência máxima da GPU",
"free_guest_texture_memory":"Liberar memória de texturas do sistema convidado",
"free_guest_texture_memory_desc":"Permite liberar da memória dados de texturas do sistema convidado quando não são necessários (raramente pode causar falhas)",
"shader_cache":"Desativar cache de shaders","shader_cache_disabled":"Os shaders em cache não serão carregados; isso causará travamentos na renderização",
"shader_cache_enabled":"Os shaders em cache serão carregados e podem reduzir bastante os engasgos",
"hacks":"Ajustes avançados","enable_fast_gpu_readback":"Ativar leitura rápida da GPU",
"enable_fast_gpu_readback_enabled":"A leitura rápida da GPU está ativada (pode causar falhas em alguns jogos, mas melhorar o desempenho em outros)",
"enable_fast_gpu_readback_disabled":"A leitura rápida da GPU está desativada (prioriza a precisão)",
"enable_fast_readback_writes":"Ativar gravações rápidas de leitura","enable_fast_readback_writes_enabled":"As gravações rápidas de leitura estão ativadas",
"enable_fast_readback_writes_disabled":"As gravações rápidas de leitura estão desativadas",
"disable_subgroup_shuffle":"Desativar operações Subgroup Shuffle da GPU",
"disable_subgroup_shuffle_enabled":"As operações Subgroup Shuffle dos shaders estão desativadas; isso pode causar problemas gráficos graves",
"disable_subgroup_shuffle_disabled":"As operações Subgroup Shuffle dos shaders estão ativadas, garantindo a maior precisão",
"debug":"Depuração","log_level":"Nível de registro","validation_layer":"Ativar camada de validação",
"validation_layer_enabled":"A camada de validação do Vulkan está ativada; espere grandes quedas de desempenho",
"validation_layer_disabled":"A camada de validação do Vulkan está desativada",
"gpu_driver":"Driver da GPU","add_gpu_driver":"Adicionar um driver de GPU","delete_gpu_driver":"Excluir este driver de GPU",
"system_driver":"Driver do sistema","system_driver_desc":"Driver de GPU fornecido pelo sistema","install":"Instalar",
"gpu_driver_install_inprogress":"Instalando o driver da GPU…","gpu_driver_install_success":"Driver da GPU instalado com sucesso",
"gpu_driver_install_invalid_archive":"Falha ao descompactar o pacote de driver informado",
"gpu_driver_install_missing_metadata":"O pacote de driver informado é inválido porque faltam metadados",
"gpu_driver_install_invalid_metadata":"O pacote de driver informado contém metadados inválidos e pode estar corrompido",
"gpu_driver_install_unsupported_android_version":"Seu dispositivo não atende aos requisitos mínimos de versão do Android para este driver",
"gpu_driver_install_already_installed":"O pacote de driver informado já está instalado",
"input":"Entrada","osc":"Controles na tela","osc_enable":"Ativar controles na tela",
"osc_not_shown":"Os controles na tela não serão exibidos","osc_shown":"Os controles na tela serão exibidos",
"osc_feedback":"Ativar resposta tátil","osc_feedback_description":"Não se aplica aos direcionais analógicos e controles físicos",
"osc_edit":"Editar layout dos controles na tela","osc_text_color":"Cor do texto","osc_background_color":"Cor do plano de fundo",
"osc_reset":"Redefinir botão: %1$s","osc_reset_confirm":"Tem certeza de que deseja redefinir este botão?",
"osc_toggle_mode":"Modo alternável","osc_current_button":"Botão atual: %1$s","select_all":"Selecionar tudo",
"osc_scale":"Escala","osc_opacity":"Opacidade","osc_activation_radius":"Raio de ativação","button_color":"Cor do botão",
"toggle_grid":"Alternar grade","setup_guide":"Guia de configuração",
"setup_guide_description":"Mapeie sequencialmente cada direcional analógico e botão","joystick":"Direcional analógico",
"confirm":"Confirmar","cancel":"Cancelar","osc_recenter_sticks":"Centralizar analógicos ao tocar",
"osc_recenter_sticks_desc":"Reposiciona os direcionais analógicos no local pressionado quando são tocados",
"osc_use_stick_regions":"Usar áreas dos analógicos",
"osc_use_stick_regions_desc":"Amplia a área de ativação dos analógicos para retângulos que cobrem a metade correspondente da tela",
"controller":"Controle","config_controller":"Configurar controle","controller_type":"Tipo de controle","none":"Nenhum",
"handheld_procon":"Portátil + Pro Controller","procon":"Pro Controller","ljoycon":"Joy-Con esquerdo","rjoycon":"Joy-Con direito",
"general":"Geral","partner_joycon":"Joy-Con parceiro","rumble_device":"Dispositivo de vibração",
"supported":"Compatível","not_supported":"Não compatível","press_any_button":"Pressione qualquer botão do controle",
"confirm_button_again":"Confirme a escolha pressionando um botão novamente","builtin":"Integrado",
"builtin_vibrator":"Vibrador integrado","reset":"Redefinir","buttons":"Botões",
"use_button_axis":"Use qualquer botão ou eixo do controle","release_confirm":"Solte para confirmar a seleção",
"hold_confirm":"Mantenha pressionado para confirmar a seleção","sticks":"Direcionais analógicos","stick_button":"Botão do analógico",
"next":"Avançar","x_plus":"Eixo X+ do analógico (direita)","y_plus":"Eixo Y+ do analógico (cima)",
"x_minus":"Eixo X- do analógico (esquerda)","y_minus":"Eixo Y- do analógico (baixo)",
"a_button":"A","b_button":"B","x_button":"X","y_button":"Y","left_shoulder":"Botão superior esquerdo",
"right_shoulder":"Botão superior direito","left_trigger":"Gatilho esquerdo","right_trigger":"Gatilho direito",
"plus_button":"Mais","minus_button":"Menos","emu_menu_button":"Menu do emulador","stick_preview":"Prévia do analógico",
"done":"Concluído","use_non_stick":"Use qualquer botão ainda não mapeado para finalizar","button":"Botão",
"up":"Cima","down":"Baixo","left":"Esquerda","right":"Direita","dpad":"Direcional digital",
"left_stick":"Analógico esquerdo","right_stick":"Analógico direito","left_stick_button":"Botão do analógico esquerdo",
"right_stick_button":"Botão do analógico direito","face_buttons":"Botões frontais",
"shoulder_trigger":"Botões superiores e gatilhos","shoulder_rail":"Botões superiores no trilho do Joy-Con",
"misc_buttons":"Outros botões","credits":"Créditos","licenses":"Licenças",
"skyline_license_description":"O Skyline é licenciado sob a Mozilla Public License 2.0",
"ryujinx_description":"O Ryujinx foi usado como referência durante o projeto devido à alta precisão de suas implementações\\n\\n<b>Observação: o Skyline não é baseado no Ryujinx</b>",
"shader_compiler_description":"O compilador de shaders do Skyline é um <b>fork</b> do compilador de shaders do <i>yuzu</i>, com alterações específicas do Skyline; outras alterações são compartilhadas entre os projetos para beneficiar ambos\\n\\n<b>Observação:</b> seu uso no Skyline só é possível devido à exceção de licença concedida pela equipe do <i>yuzu</i>",
"sirit_description":"O compilador de shaders do Skyline usa internamente o Sirit para gerar SPIR-V de forma eficiente",
"vkhpp_description":"O Vulkan-Hpp fornece uma API C++ para Vulkan",
"vkma_description":"O Vulkan Memory Allocator fornece um alocador de memória de GPU de alta qualidade com suporte a UMA",
"khvkval_description":"A camada de validação Vulkan da Khronos verifica erros nas chamadas da API Vulkan em compilações de depuração",
"oboe_description":"O Oboe é usado para saída de áudio de alto desempenho",
"perfetto_description":"O Perfetto é usado para criar perfis e depurar com rastreamento detalhado",
"fmtlib_description":"O {fmt} fornece uma API moderna de formatação de strings em C++",
"boost_description":"O Boost fornece implementações de alta qualidade de contêineres e outras funções auxiliares em C++",
"rangev3_description":"O Range v3 é uma implementação de referência dos ranges do ISO C++20, permitindo seu uso enquanto são desenvolvidos na libc++ do LLVM",
"frozen_description":"O Frozen fornece mapas hash imutáveis em tempo de compilação, com função hash perfeita para buscas mais rápidas",
"pugixml_description":"O pugixml é usado para analisar o XML de preferências e recuperar configurações no C++",
"opus_description":"O Opus Audio Codec fornece um decodificador Opus de alta qualidade para decodificar o áudio recebido do sistema convidado",
"mbedtls_description":"O Mbed TLS é usado para descriptografar NCAs protegidos por AES",
"lz4_description":"O LZ4 é usado para extrair seções ELF compactadas em LZ4 de um NSO",
"tzcode_description":"O tzcode fornece uma API C para acessar o tzdb e os dados de fuso horário",
"jssim_description":"O Java String Similarity dá suporte à função de pesquisa",
"andx_description":"O AndroidX oferece uma experiência consistente entre diferentes versões do Android",
"amat_description":"O Android Material Components oferece uma interface consistente com o Material Design",
"ktstd_description":"A Kotlin Standard Library fornece funções auxiliares para Kotlin",
"dagger_description":"O Dagger fornece uma estrutura de injeção de dependências em tempo de compilação",
"mtico_description":"O Material Design Icons fornece ícones consistentes em todo o aplicativo",
"noto_sans_description":"O Noto Sans é usado como fonte livre compartilhada para latim, japonês e chinês tradicional",
"roboto_description":"O Roboto é usado como fonte livre compartilhada para coreano e o conjunto de caracteres estendido da Nintendo",
"input_hint":"Digite o texto","compiling_cached_pipelines":"Compilando pipelines em cache...",
"expand_button_title":"Expandir","undo":"Desfazer","per_game_settings_active_message":"As configurações específicas deste jogo estão ativas",
"save_data_manager":"Gerenciar dados salvos","save_data_found":"Dados salvos encontrados. O que deseja fazer?",
"save_data_not_found":"Nenhum dado salvo encontrado. O que deseja fazer?",
"delete_save_confirmation_message":"Tem certeza de que deseja excluir este salvamento?",
"action_irreversible":"Esta ação não pode ser desfeita","yes":"Sim","no":"Não",
"save_file_imported_ok":"Arquivo de salvamento importado com sucesso",
"save_file_invalid_zip_structure":"Estrutura de diretórios ZIP inválida: o nome da primeira subpasta deve ser o ID do jogo.",
"save_file_share":"Compartilhar arquivo de salvamento","global_save_data_zip_name":"Dados salvos do Skyline Dimm",
"game_crash":"O jogo travou","game_crash_message":"Ocorreu um erro fatal. Consulte o registro para obter detalhes.",
"game_content":"DLC/Atualização","game_mods":"Trapaças / Mods","game_mods_install":"Selecionar pasta","game_mods_install_zip":"Importar ZIP",
"game_mods_manage_short":"Gerenciar","game_mods_manage":"Gerenciar trapaças / mods","game_mods_count":"%1$d mod(s) instalado(s)",
"game_mods_empty":"Nenhum mod instalado. Selecione uma pasta de mod que contenha romfs, exefs ou cheats (ZIP opcional).",
"game_mods_fail":"Não foi possível instalar o mod","game_mods_remove":"Excluir mod",
"game_mods_imported":"Mod importado. Reinicie o jogo para aplicar os mods ativados.",
"game_mods_notes":"São aceitas substituições de ExeFS e RomFS. Arquivos de trapaça podem ser gerenciados, mas sua execução exige um mecanismo de cheats compatível.",
"game_content_batch_summary":"Instalados: %1$d, já existentes: %2$d, falharam: %3$d",
"game_content_batch_failed":"Não foi possível instalar alguns pacotes",
"game_content_install":"Instalar","game_content_manage":"Gerenciar DLCs/atualizações instalados",
"game_content_remove":"Remover este DLC/esta atualização?","game_content_count":"%1$d pacote(s) instalado(s)",
"game_content_installing":"Instalando DLC/atualização","game_content_copying":"Copiando conteúdo…",
"game_content_verifying":"Verificando conteúdo e compatibilidade…",
"game_content_installed":"DLC/atualização instalada. Ela será aplicada quando você iniciar o jogo.",
"game_content_already_installed":"Este conteúdo já está instalado.",
"game_content_install_failed":"Não foi possível instalar o DLC/a atualização"
}

MALI = {
"mali_ready":"Pronto para jogar","mali_play":"Jogar","mali_details":"Detalhes",
"mali_games":"Jogos","mali_install":"Instalar","mali_add":"Adicionar"
}

SETTINGS = {
"settings_hub_title":"Configurações",
"settings_version_label":"Versão %1$s",
"settings_tab_graphics":"Gráficos",
"settings_tab_gpu":"GPU",
"settings_tab_folders":"Pastas de jogos",
"settings_tab_drivers":"Drivers gráficos",
"settings_tab_general":"Geral",
"settings_graphics_summary":"Tela, proporção, estatísticas de desempenho e cache de shaders.",
"settings_gpu_summary":"Buffering, memória da GPU e opções avançadas de compatibilidade.",
"settings_folders_summary":"Escolha a pasta de jogos e controle quais arquivos aparecem na biblioteca.",
"settings_drivers_summary":"Importe, selecione ou remova pacotes de drivers gráficos.",
"settings_general_summary":"Sistema, áudio, controles, chaves, firmware e preferências do aplicativo."
}

SETUP = {
"setup_welcome":"Bem-vindo ao Skyline Dimm",
"setup_intro":"Selecione suas chaves, o firmware e a pasta de jogos para começar.",
"setup_keys":"1. Selecionar prod.keys",
"setup_firmware":"2. Instalar firmware",
"setup_games":"3. Selecionar pasta de jogos",
"setup_keys_help":"Obrigatório · Importe seu arquivo prod.keys.",
"setup_firmware_help":"Recomendado · Selecione um arquivo ZIP de firmware. Você também pode instalá-lo depois em Configurações.",
"setup_games_help":"Escolha a pasta que contém seus jogos.",
"setup_keys_ready":"Chaves importadas",
"setup_folder_ready":"Pasta de jogos selecionada",
"setup_firmware_installed":"Firmware %1$s instalado",
"setup_start":"Começar a jogar",
"setup_back":"Voltar",
"setup_importing_keys":"Importando chaves…",
"setup_checking_folder":"Verificando pasta de jogos…",
"setup_unreadable_folder":"Não foi possível ler a pasta selecionada",
"setup_failed":"Falha na importação: %1$s",
"setup_open":"Abrir configuração inicial"
}

EMULATION_MENU = {
"emulation_menu":"Skyline Dimm",
"emulation_resume":"Continuar jogo",
"emulation_controls":"Controles na tela",
"emulation_fps":"Mostrar FPS",
"emulation_mute":"Silenciar áudio",
"emulation_exit":"Sair do jogo",
"emulation_exit_message":"Deseja sair deste jogo? O progresso não salvo será perdido."
}

ARRAYS = {
"log_level":["Detalhado","Depuração","Informações","Aviso","Erro","Desativado"],
"layout_type":["Lista","Grade","Grade compacta"],
"sort_apps_by":["A–Z","Z–A"],
"app_theme":["Claro","Escuro","Usar padrão do sistema"],
"system_languages":["Inglês (Estados Unidos)","Inglês (Reino Unido)","Francês","Francês canadense","Alemão","Espanhol","Espanhol latino-americano","Italiano","Holandês","Português","Português do Brasil","Russo","Japonês","Chinês","Chinês tradicional","Chinês simplificado","Coreano","Taiwanês"],
"system_region":["Automático","Japão","Américas","Europa","Austrália / Nova Zelândia","Hong Kong / Taiwan / Coreia do Sul","China"],
"aspect_ratios":["16:9 (Switch, recomendado)","21:9 (mods ultrawide)","Proporção da tela do dispositivo (esticar para preencher)"],
"orientation_entries":["Automática","Paisagem","Paisagem (invertida)"]
}

def write_strings(filename, mapping):
    source = base / filename
    original = ET.parse(source).getroot()
    available = {node.attrib["name"] for node in original.findall("string")}
    missing = sorted(set(mapping) - available)
    if missing:
        raise SystemExit(f"Chaves inexistentes em {filename}: {missing}")
    resources = ET.Element("resources")
    for key, value in mapping.items():
        node = ET.SubElement(resources, "string", {"name": key})
        node.text = value
    ET.indent(resources, space="    ")
    ET.ElementTree(resources).write(locale / filename, encoding="utf-8", xml_declaration=True)

def write_arrays():
    original = ET.parse(base / "array.xml").getroot()
    resources = ET.Element("resources")
    for key, values in ARRAYS.items():
        source = original.find(f"string-array[@name='{key}']")
        if source is None or len(source) != len(values):
            raise SystemExit(f"Array {key} ausente ou com quantidade diferente de itens")
        target = ET.SubElement(resources, "string-array", {"name": key})
        for value in values:
            ET.SubElement(target, "item").text = value
    ET.indent(resources, space="    ")
    ET.ElementTree(resources).write(locale / "array.xml", encoding="utf-8", xml_declaration=True)

write_strings("strings.xml", STRINGS)
write_strings("strings_mali_library.xml", MALI)
write_strings("settings_design.xml", SETTINGS)
write_strings("setup.xml", SETUP)
write_strings("emulation_menu.xml", EMULATION_MENU)
write_arrays()

advanced = {
    "mipmap_lod_bias":"Ajuste de nível de detalhe (Mipmaps)",
    "mipmap_lod_bias_desc":"Valores positivos selecionam mipmaps de menor resolução à distância e podem reduzir o uso de banda de memória. Valores negativos deixam texturas distantes mais nítidas, mas podem causar cintilação. Reinicie o jogo após alterar.",
    "max_anisotropy":"Filtragem anisotrópica",
    "max_anisotropy_desc":"Substitui a anisotropia definida pelo jogo quando compatível com a GPU. Valores maiores podem melhorar superfícies em ângulo, mas reduzir o desempenho. Reinicie o jogo após alterar.",
    "performance_profile":"Perfil de desempenho",
    "performance_profile_desc":"Aplica um perfil aos controles existentes de resolução interna, Mipmap LOD bias e anisotropia. As alterações entram em vigor ao reiniciar o jogo. Personalizado mantém seus valores individuais."
}
res = ET.Element("resources")
for key, value in advanced.items():
    ET.SubElement(res, "string", {"name":key}).text = value
profile_entries = ET.SubElement(res, "string-array", {"name":"performance_profile_entries"})
for value in ("Personalizado", "FPS equilibrado (0,75x)", "Desempenho (0,50x)", "Automático GPU (Adreno/Mali)"):
    ET.SubElement(profile_entries, "item").text = value
ET.indent(res, space="    ")
ET.ElementTree(res).write(locale / "dimm_advanced_graphics.xml", encoding="utf-8", xml_declaration=True)

# Verify all translated source keys exist and that untranslated strings safely fall back to English.
for filename, mapping in (("strings.xml", STRINGS), ("strings_mali_library.xml", MALI)):
    original = {n.attrib["name"] for n in ET.parse(base / filename).getroot().findall("string")}
    translated = {n.attrib["name"] for n in ET.parse(locale / filename).getroot().findall("string")}
    if not set(mapping).issubset(original) or translated != set(mapping):
        raise SystemExit(f"Falha de validação da tradução: {filename}")
# Register pt-BR in the app's language picker while preserving every existing locale.
locale_config = root / "app/src/main/res/xml/locales_config.xml"
if not locale_config.is_file():
    raise SystemExit("Arquivo locales_config.xml não encontrado")
locale_data = locale_config.read_text(encoding="utf-8")
if 'android:name="pt-BR"' not in locale_data:
    closing = "</locale-config>"
    if locale_data.count(closing) != 1:
        raise SystemExit("Não foi possível localizar o fechamento de locales_config.xml")
    locale_data = locale_data.replace(closing, '    <locale android:name="pt-BR" /> <!-- Português do Brasil -->\n' + closing, 1)
    locale_config.write_text(locale_data, encoding="utf-8")
if 'android:name="pt-BR"' not in locale_config.read_text(encoding="utf-8"):
    raise SystemExit("O idioma pt-BR não foi registrado no seletor de idiomas")

print(f"Recursos pt-BR gerados: {len(STRINGS)} textos, {len(MALI)} textos auxiliares e {len(ARRAYS)} listas.")

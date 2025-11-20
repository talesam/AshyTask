from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Emojis para status e prioridades
STATUS_EMOJI = {
    "pendente": "⏳",
    "em_andamento": "🔄",
    "concluido": "✅"
}

PRIORIDADE_EMOJI = {
    "alta": "🔴",
    "media": "🟡",
    "baixa": "🟢"
}

def menu_principal():
    """Teclado do menu principal de filtros"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Todas", callback_data="lista_todas"),
            InlineKeyboardButton("⏳ Pendentes", callback_data="lista_pendente")
        ],
        [
            InlineKeyboardButton("🔄 Em Andamento", callback_data="lista_em_andamento"),
            InlineKeyboardButton("✅ Concluídas", callback_data="lista_concluido")
        ],
        [
            InlineKeyboardButton("🖥️ Por Categoria", callback_data="menu_categorias")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def menu_categorias(categorias):
    """Teclado com lista de categorias"""
    keyboard = []
    for cat in categorias:
        keyboard.append([
            InlineKeyboardButton(f"🖥️ {cat['nome']}", callback_data=f"cat_{cat['id']}")
        ])
    keyboard.append([InlineKeyboardButton("➕ Nova Categoria", callback_data="nova_categoria")])
    keyboard.append([InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu")])
    return InlineKeyboardMarkup(keyboard)

def acoes_tarefa(tarefa_id, autor_id, user_id):
    """Botões de ação para uma tarefa específica"""
    keyboard = []
    
    # Botões de status (todos podem mudar status)
    keyboard.append([
        InlineKeyboardButton("⏳ Pendente", callback_data=f"status_{tarefa_id}_pendente"),
        InlineKeyboardButton("🔄 Em Andamento", callback_data=f"status_{tarefa_id}_em_andamento"),
    ])
    keyboard.append([
        InlineKeyboardButton("✅ Concluir", callback_data=f"status_{tarefa_id}_concluido")
    ])
    
    # Botões de ação (apenas autor pode editar/deletar)
    if autor_id == user_id:
        keyboard.append([
            InlineKeyboardButton("✏️ Editar", callback_data=f"editar_{tarefa_id}"),
            InlineKeyboardButton("🗑️ Deletar", callback_data=f"deletar_{tarefa_id}")
        ])
    
    # Botão de comentários
    keyboard.append([
        InlineKeyboardButton("💬 Ver Comentários", callback_data=f"comentarios_{tarefa_id}")
    ])
    
    keyboard.append([
        InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def keyboard_confirmar_delecao(tarefa_id):
    """Teclado de confirmação de deleção"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Sim, deletar", callback_data=f"confirma_del_{tarefa_id}"),
            InlineKeyboardButton("❌ Cancelar", callback_data=f"cancelar_del_{tarefa_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def selecionar_categoria_nova_tarefa(categorias):
    """Teclado para selecionar categoria ao criar tarefa"""
    keyboard = []
    for cat in categorias:
        keyboard.append([
            InlineKeyboardButton(cat['nome'], callback_data=f"newcat_{cat['id']}")
        ])
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancelar_nova")])
    return InlineKeyboardMarkup(keyboard)

def selecionar_prioridade():
    """Teclado para selecionar prioridade"""
    keyboard = [
        [
            InlineKeyboardButton("🔴 Alta", callback_data="prior_alta"),
            InlineKeyboardButton("🟡 Média", callback_data="prior_media"),
            InlineKeyboardButton("🟢 Baixa", callback_data="prior_baixa")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def menu_edicao(tarefa_id):
    """Menu de opções de edição"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Editar Título", callback_data=f"edit_titulo_{tarefa_id}"),
        ],
        [
            InlineKeyboardButton("📄 Editar Descrição", callback_data=f"edit_desc_{tarefa_id}"),
        ],
        [
            InlineKeyboardButton("🎯 Editar Prioridade", callback_data=f"edit_prior_{tarefa_id}"),
        ],
        [
            InlineKeyboardButton("⬅️ Cancelar", callback_data=f"ver_{tarefa_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def voltar_tarefa(tarefa_id):
    """Botão simples para voltar à visualização da tarefa"""
    keyboard = [
        [InlineKeyboardButton("➕ Adicionar Comentário", callback_data=f"add_comentario_{tarefa_id}")],
        [InlineKeyboardButton("⬅️ Voltar", callback_data=f"ver_{tarefa_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def paginacao(pagina_atual, total_paginas, prefixo="pag"):
    """Botões de paginação"""
    keyboard = []
    buttons = []
    
    if pagina_atual > 0:
        buttons.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"{prefixo}_{pagina_atual-1}"))
    
    buttons.append(InlineKeyboardButton(f"{pagina_atual+1}/{total_paginas}", callback_data="ignore"))
    
    if pagina_atual < total_paginas - 1:
        buttons.append(InlineKeyboardButton("➡️ Próximo", callback_data=f"{prefixo}_{pagina_atual+1}"))
    
    if buttons:
        keyboard.append(buttons)
    
    keyboard.append([InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data="voltar_menu")])
    
    return InlineKeyboardMarkup(keyboard)

def formatar_tarefa_texto(tarefa, mostrar_descricao=True):
    """Formata uma tarefa para exibição em texto"""
    status_emoji = STATUS_EMOJI.get(tarefa['status'], "❓")
    prior_emoji = PRIORIDADE_EMOJI.get(tarefa['prioridade'], "⚪")

    texto = f"*#{tarefa['id']} - {tarefa['titulo']}*\n"
    texto += f"{status_emoji} Status: {tarefa['status'].replace('_', ' ').title()}\n"
    texto += f"{prior_emoji} Prioridade: {tarefa['prioridade'].title()}\n"
    texto += f"🖥️ Categoria: {tarefa['categoria']}\n"
    texto += f"👤 Criado por: {tarefa['autor_nome']}\n"

    if tarefa.get('atribuido_nome'):
        texto += f"👥 Atribuído: {tarefa['atribuido_nome']}\n"

    texto += f"📅 Data: {tarefa['data_criacao'][:16]}\n"

    if mostrar_descricao and tarefa.get('descricao'):
        texto += f"\n📝 *Descrição:*\n{tarefa['descricao']}\n"

    return texto

# ============ CHANGELOG KEYBOARDS ============

def menu_changelog_principal():
    """Menu principal de changelogs"""
    keyboard = [
        [InlineKeyboardButton("📝 Novo Changelog", callback_data="changelog_novo")],
        [
            InlineKeyboardButton("📋 Todos", callback_data="changelog_listar_todos"),
            InlineKeyboardButton("📌 Pinados", callback_data="changelog_listar_pinados")
        ],
        [
            InlineKeyboardButton("🖥️ Por Categoria", callback_data="changelog_categorias"),
            InlineKeyboardButton("📊 Estatísticas", callback_data="changelog_stats")
        ],
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_voltar")]
    ]
    return InlineKeyboardMarkup(keyboard)

def selecionar_categoria_changelog(categorias):
    """Teclado para selecionar categoria do changelog"""
    keyboard = []

    for idx, cat in enumerate(categorias):
        emoji = "📍"
        keyboard.append([InlineKeyboardButton(f"{emoji} {cat}", callback_data=f"newlog_idx_{idx}")])

    keyboard.append([InlineKeyboardButton("➕ Nova Categoria", callback_data="changelog_nova_cat")])
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="changelog_menu")])
    return InlineKeyboardMarkup(keyboard)

def menu_filtro_categoria_changelog(categorias):
    """Menu para filtrar changelogs por categoria"""
    keyboard = []

    for idx, cat in enumerate(categorias):
        emoji = "📍"
        keyboard.append([InlineKeyboardButton(f"{emoji} {cat}", callback_data=f"changelog_catidx_{idx}")])

    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="changelog_menu")])
    return InlineKeyboardMarkup(keyboard)

def acoes_changelog(changelog_id: int, autor_id: int, user_id: int, pinado: bool):
    """Botões de ação para um changelog específico"""
    keyboard = []

    # Botão de pinagem (todos podem pinar/despinar)
    pin_emoji = "📌" if not pinado else "📍"
    pin_text = "Pinar" if not pinado else "Despinar"
    keyboard.append([InlineKeyboardButton(f"{pin_emoji} {pin_text}", callback_data=f"changelog_pin_{changelog_id}")])

    # Botões de edição/deleção (apenas autor)
    if autor_id == user_id:
        keyboard.append([
            InlineKeyboardButton("✏️ Editar", callback_data=f"changelog_editar_{changelog_id}"),
            InlineKeyboardButton("🗑️ Deletar", callback_data=f"changelog_deletar_{changelog_id}")
        ])

    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="changelog_menu")])

    return InlineKeyboardMarkup(keyboard)

def menu_edicao_changelog(changelog_id: int):
    """Menu de opções de edição de changelog"""
    keyboard = [
        [InlineKeyboardButton("📝 Editar Descrição", callback_data=f"changelog_edit_desc_{changelog_id}")],
        [InlineKeyboardButton("📁 Editar Categoria", callback_data=f"changelog_edit_cat_{changelog_id}")],
        [InlineKeyboardButton("⬅️ Cancelar", callback_data=f"changelog_ver_{changelog_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirmar_delecao_changelog(changelog_id: int):
    """Teclado de confirmação de deleção de changelog"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Sim, deletar", callback_data=f"changelog_confirma_del_{changelog_id}"),
            InlineKeyboardButton("❌ Cancelar", callback_data=f"changelog_ver_{changelog_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

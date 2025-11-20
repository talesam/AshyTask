from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from database import Database
import keyboards
import math

# Estados da conversa para criar nova tarefa
ESCOLHER_CATEGORIA, DIGITAR_TITULO, DIGITAR_DESCRICAO, ESCOLHER_PRIORIDADE, ENVIAR_IMAGEM = range(5)

# Estados para edição
EDITAR_TITULO, EDITAR_DESCRICAO, EDITAR_PRIORIDADE = range(5, 8)

# Estado para comentário
ADICIONAR_COMENTARIO = 8

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /start"""
    texto = """
🤖 *Bot de Gerenciamento de Tarefas - BigCommunity*

Comandos disponíveis:

/tarefas - Lista todas as tarefas
/nova - Cria uma nova tarefa
/minhas - Mostra suas tarefas
/buscar [termo] - Busca tarefas
/comentar [id] [texto] - Adiciona comentário
/addcategoria [nome] - Adiciona nova categoria
/ajuda - Mostra esta mensagem

Use os botões inline para navegar e gerenciar as tarefas!
"""
    await update.message.reply_text(texto, parse_mode=ParseMode.MARKDOWN)

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /ajuda"""
    await start(update, context)

async def listar_tarefas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /tarefas"""
    query = update.callback_query
    
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    texto = "*📋 Gerenciador de Tarefas*\n\nSelecione uma opção:"
    keyboard = keyboards.menu_principal()
    
    if query:
        await message.edit_text(texto, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply_text(texto, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def minhas_tarefas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /minhas"""
    user_id = update.effective_user.id
    tarefas = db.listar_tarefas(autor_id=user_id)
    
    if not tarefas:
        await update.message.reply_text("Você não tem tarefas cadastradas.")
        return
    
    texto = "*📋 Suas Tarefas:*\n\n"
    for tarefa in tarefas[:10]:  # Limita a 10 tarefas
        texto += keyboards.formatar_tarefa_texto(tarefa, mostrar_descricao=False)
        texto += "─" * 30 + "\n"
    
    if len(tarefas) > 10:
        texto += f"\n_...e mais {len(tarefas) - 10} tarefas_"
    
    await update.message.reply_text(texto, parse_mode=ParseMode.MARKDOWN)

async def buscar_tarefas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /buscar"""
    if not context.args:
        await update.message.reply_text("Use: /buscar [termo]")
        return
    
    termo = " ".join(context.args)
    tarefas = db.buscar_tarefas(termo)
    
    if not tarefas:
        await update.message.reply_text(f"Nenhuma tarefa encontrada para '{termo}'")
        return
    
    texto = f"*🔍 Resultados para '{termo}':*\n\n"
    for tarefa in tarefas[:10]:
        texto += keyboards.formatar_tarefa_texto(tarefa, mostrar_descricao=False)
        texto += "─" * 30 + "\n"
    
    if len(tarefas) > 10:
        texto += f"\n_...e mais {len(tarefas) - 10} resultados_"
    
    await update.message.reply_text(texto, parse_mode=ParseMode.MARKDOWN)

async def adicionar_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /addcategoria"""
    if not context.args:
        await update.message.reply_text("Use: /addcategoria [nome da categoria]")
        return
    
    nome = " ".join(context.args)
    
    if db.adicionar_categoria(nome):
        await update.message.reply_text(f"✅ Categoria '{nome}' adicionada com sucesso!")
    else:
        await update.message.reply_text(f"❌ Categoria '{nome}' já existe!")

# === CONVERSAÇÃO PARA CRIAR NOVA TAREFA ===

async def nova_tarefa_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de criar nova tarefa"""
    categorias = db.listar_categorias()
    keyboard = keyboards.selecionar_categoria_nova_tarefa(categorias)
    
    await update.message.reply_text(
        "*📝 Nova Tarefa*\n\nEscolha a categoria:",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return ESCOLHER_CATEGORIA

async def categoria_escolhida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuário escolheu a categoria"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancelar_nova":
        await query.message.edit_text("❌ Criação de tarefa cancelada.")
        return ConversationHandler.END
    
    # Extrai o ID da categoria
    categoria_id = int(query.data.split("_")[1])
    context.user_data['nova_tarefa'] = {'categoria_id': categoria_id}
    
    await query.message.edit_text(
        "*📝 Nova Tarefa*\n\nDigite o *título* da tarefa:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return DIGITAR_TITULO

async def titulo_recebido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuário digitou o título"""
    titulo = update.message.text
    context.user_data['nova_tarefa']['titulo'] = titulo
    
    await update.message.reply_text(
        "*📝 Nova Tarefa*\n\nDigite a *descrição* da tarefa:\n\n_(Ou envie /pular para pular esta etapa)_",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return DIGITAR_DESCRICAO

async def descricao_recebida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuário digitou a descrição"""
    descricao = update.message.text
    
    if descricao != "/pular":
        context.user_data['nova_tarefa']['descricao'] = descricao
    else:
        context.user_data['nova_tarefa']['descricao'] = ""
    
    keyboard = keyboards.selecionar_prioridade()
    await update.message.reply_text(
        "*📝 Nova Tarefa*\n\nEscolha a *prioridade*:",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return ESCOLHER_PRIORIDADE

async def prioridade_escolhida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuário escolheu a prioridade"""
    query = update.callback_query
    await query.answer()
    
    prioridade = query.data.split("_")[1]
    context.user_data['nova_tarefa']['prioridade'] = prioridade
    
    await query.message.edit_text(
        "*📝 Nova Tarefa*\n\n📸 Envie uma *imagem* (opcional)\n\n_Ou envie /pular para finalizar_",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return ENVIAR_IMAGEM

async def imagem_recebida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuário enviou uma imagem"""
    if update.message.text == "/pular":
        return await finalizar_nova_tarefa(update, context)
    
    if update.message.photo:
        # Pega a foto de maior resolução
        photo = update.message.photo[-1]
        context.user_data['nova_tarefa']['imagem_file_id'] = photo.file_id
    
    return await finalizar_nova_tarefa(update, context)

async def finalizar_nova_tarefa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finaliza a criação da tarefa"""
    dados = context.user_data['nova_tarefa']
    user = update.effective_user
    
    tarefa_id = db.criar_tarefa(
        titulo=dados['titulo'],
        descricao=dados.get('descricao', ''),
        categoria_id=dados['categoria_id'],
        autor_id=user.id,
        autor_nome=user.first_name,
        prioridade=dados.get('prioridade', 'media'),
        imagem_file_id=dados.get('imagem_file_id')
    )
    
    tarefa = db.obter_tarefa(tarefa_id)
    texto = "✅ *Tarefa criada com sucesso!*\n\n" + keyboards.formatar_tarefa_texto(tarefa)
    
    await update.message.reply_text(texto, parse_mode=ParseMode.MARKDOWN)
    
    # Limpa os dados temporários
    context.user_data.pop('nova_tarefa', None)
    
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela a conversa"""
    await update.message.reply_text("❌ Operação cancelada.")
    context.user_data.clear()
    return ConversationHandler.END

# === CALLBACKS DE NAVEGAÇÃO ===

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler geral para callbacks inline"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Ignorar callbacks de paginação placeholder
    if data == "ignore":
        return
    
    # Menu principal
    if data == "voltar_menu":
        await listar_tarefas(update, context)
        return
    
    # Listagens
    if data.startswith("lista_"):
        status = data.split("_", 1)[1] if data != "lista_todas" else None
        await mostrar_lista_tarefas(update, context, status=status)
        return
    
    # Menu de categorias
    if data == "menu_categorias":
        categorias = db.listar_categorias()
        keyboard = keyboards.menu_categorias(categorias)
        await query.message.edit_text(
            "*🖥️ Selecione uma categoria:*",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Filtrar por categoria
    if data.startswith("cat_"):
        categoria_id = int(data.split("_")[1])
        await mostrar_lista_tarefas(update, context, categoria_id=categoria_id)
        return
    
    # Ver detalhes de uma tarefa
    if data.startswith("ver_"):
        tarefa_id = int(data.split("_")[1])
        await mostrar_detalhes_tarefa(update, context, tarefa_id)
        return
    
    # Mudar status
    if data.startswith("status_"):
        parts = data.split("_")
        tarefa_id = int(parts[1])
        novo_status = parts[2]
        
        if db.atualizar_status(tarefa_id, novo_status):
            await query.answer(f"✅ Status atualizado para {novo_status.replace('_', ' ')}!")
            await mostrar_detalhes_tarefa(update, context, tarefa_id)
        else:
            await query.answer("❌ Erro ao atualizar status", show_alert=True)
        return
    
    # Deletar tarefa
    if data.startswith("deletar_"):
        tarefa_id = int(data.split("_")[1])
        keyboard = keyboards.confirmar_delecao(tarefa_id)
        await query.message.edit_text(
            "⚠️ *Confirma a exclusão desta tarefa?*\n\nEsta ação não pode ser desfeita!",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Confirmar deleção
    if data.startswith("confirma_del_"):
        tarefa_id = int(data.split("_")[2])
        tarefa = db.obter_tarefa(tarefa_id)
        
        if tarefa and tarefa['autor_id'] == update.effective_user.id:
            if db.deletar_tarefa(tarefa_id):
                await query.message.edit_text("✅ Tarefa deletada com sucesso!")
            else:
                await query.message.edit_text("❌ Erro ao deletar tarefa")
        else:
            await query.answer("❌ Você não tem permissão para deletar esta tarefa", show_alert=True)
        return
    
    # Cancelar deleção
    if data.startswith("cancelar_del_"):
        tarefa_id = int(data.split("_")[2])
        await mostrar_detalhes_tarefa(update, context, tarefa_id)
        return
    
    # Menu de edição
    if data.startswith("editar_"):
        tarefa_id = int(data.split("_")[1])
        keyboard = keyboards.menu_edicao(tarefa_id)
        await query.message.edit_text(
            "*✏️ O que deseja editar?*",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Ver comentários
    if data.startswith("comentarios_"):
        tarefa_id = int(data.split("_")[1])
        await mostrar_comentarios(update, context, tarefa_id)
        return

async def mostrar_lista_tarefas(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                status=None, categoria_id=None, pagina=0):
    """Mostra lista de tarefas com paginação"""
    query = update.callback_query
    
    tarefas = db.listar_tarefas(categoria_id=categoria_id, status=status)
    
    if not tarefas:
        await query.message.edit_text(
            "📭 Nenhuma tarefa encontrada.",
            reply_markup=keyboards.menu_principal()
        )
        return
    
    # Paginação
    itens_por_pagina = 5
    total_paginas = math.ceil(len(tarefas) / itens_por_pagina)
    inicio = pagina * itens_por_pagina
    fim = inicio + itens_por_pagina
    tarefas_pagina = tarefas[inicio:fim]
    
    texto = f"*📋 Tarefas* (Página {pagina+1}/{total_paginas})\n\n"
    
    keyboard = []
    for tarefa in tarefas_pagina:
        status_emoji = keyboards.STATUS_EMOJI.get(tarefa['status'], "❓")
        prior_emoji = keyboards.PRIORIDADE_EMOJI.get(tarefa['prioridade'], "⚪")
        
        botao_texto = f"{status_emoji}{prior_emoji} #{tarefa['id']} - {tarefa['titulo'][:30]}"
        keyboard.append([
            InlineKeyboardButton(botao_texto, callback_data=f"ver_{tarefa['id']}")
        ])
    
    # Adiciona botões de paginação
    if total_paginas > 1:
        pag_buttons = []
        if pagina > 0:
            pag_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"pag_{pagina-1}"))
        pag_buttons.append(InlineKeyboardButton(f"{pagina+1}/{total_paginas}", callback_data="ignore"))
        if pagina < total_paginas - 1:
            pag_buttons.append(InlineKeyboardButton("➡️", callback_data=f"pag_{pagina+1}"))
        keyboard.append(pag_buttons)
    
    keyboard.append([InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data="voltar_menu")])
    
    await query.message.edit_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def mostrar_detalhes_tarefa(update: Update, context: ContextTypes.DEFAULT_TYPE, tarefa_id: int):
    """Mostra detalhes completos de uma tarefa"""
    query = update.callback_query
    tarefa = db.obter_tarefa(tarefa_id)
    
    if not tarefa:
        await query.message.edit_text("❌ Tarefa não encontrada.")
        return
    
    texto = keyboards.formatar_tarefa_texto(tarefa, mostrar_descricao=True)
    keyboard = keyboards.acoes_tarefa(tarefa_id, tarefa['autor_id'], update.effective_user.id)
    
    # Se tem imagem, envia separadamente
    if tarefa.get('imagem_file_id'):
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=tarefa['imagem_file_id'],
            caption=texto,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await query.message.edit_text(
            texto,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

async def mostrar_comentarios(update: Update, context: ContextTypes.DEFAULT_TYPE, tarefa_id: int):
    """Mostra comentários de uma tarefa"""
    query = update.callback_query
    comentarios = db.listar_comentarios(tarefa_id)
    tarefa = db.obter_tarefa(tarefa_id)
    
    if not tarefa:
        await query.answer("❌ Tarefa não encontrada", show_alert=True)
        return
    
    texto = f"*💬 Comentários - Tarefa #{tarefa_id}*\n\n"
    
    if comentarios:
        for com in comentarios:
            texto += f"👤 *{com['autor_nome']}* ({com['data'][:16]})\n"
            texto += f"{com['comentario']}\n\n"
    else:
        texto += "_Nenhum comentário ainda._\n\n"
    
    texto += "\n💡 Para adicionar um comentário, use:\n`/comentar {tarefa_id} [seu comentário]`"
    
    keyboard = keyboards.voltar_tarefa(tarefa_id)
    
    await query.message.edit_text(
        texto,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

async def adicionar_comentario_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adiciona comentário via comando /comentar"""
    if len(context.args) < 2:
        await update.message.reply_text("Use: /comentar [id_tarefa] [comentário]")
        return
    
    try:
        tarefa_id = int(context.args[0])
        comentario = " ".join(context.args[1:])
        
        tarefa = db.obter_tarefa(tarefa_id)
        if not tarefa:
            await update.message.reply_text("❌ Tarefa não encontrada")
            return
        
        user = update.effective_user
        db.adicionar_comentario(tarefa_id, user.id, user.first_name, comentario)
        
        await update.message.reply_text(f"✅ Comentário adicionado à tarefa #{tarefa_id}!")
        
    except ValueError:
        await update.message.reply_text("❌ ID da tarefa inválido")

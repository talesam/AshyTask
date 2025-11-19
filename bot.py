import logging
import warnings
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from telegram.warnings import PTBUserWarning
from datetime import datetime

from database import Database
from keyboards import *

# Carregar variáveis de ambiente
load_dotenv()

# Filtrar aviso específico do ConversationHandler
warnings.filterwarnings("ignore", category=PTBUserWarning, message=".*per_message.*")

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados da conversação para criar tarefa
TITULO, DESCRICAO, CATEGORIA, PRIORIDADE, IMAGEM = range(5)

# Estados para edição
EDIT_TITULO, EDIT_DESCRICAO, EDIT_CATEGORIA, EDIT_PRIORIDADE, EDIT_IMAGEM = range(5, 10)

# Estado para comentário
ADD_COMENTARIO = 10

# Estados para changelog
CHANGELOG_CATEGORIA, CHANGELOG_DESCRICAO = range(11, 13)

# Inicializar banco de dados
db = Database()

# Constantes
CATEGORIAS = ["XFCE", "Cinnamon", "GNOME", "Geral"]
STATUS = ["pendente", "em_andamento", "concluido"]


def keyboard_filtros():
    """Teclado com filtros de status e categoria"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Todas", callback_data="filtro_refresh"),
        ],
        [
            InlineKeyboardButton("⏳ Pendentes", callback_data="filtro_status_pendente"),
            InlineKeyboardButton("🔄 Em Andamento", callback_data="filtro_status_em_andamento"),
        ],
        [
            InlineKeyboardButton("✅ Concluídas", callback_data="filtro_status_concluido"),
        ],
        [
            InlineKeyboardButton("🖥️ Por Categoria", callback_data="filtro_categorias"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============ COMANDOS PRINCIPAIS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    # Verificar tópico
    if not await verificar_topico(update):
        topico_id = db.obter_config('topico_permitido')
        await update.message.reply_text(
            f"⚠️ *Uso restrito*\n\n"
            f"Este bot só funciona no tópico configurado (ID: `{topico_id}`).\n"
            f"Por favor, use os comandos dentro do tópico apropriado.",
            parse_mode='Markdown'
        )
        return

    user = update.effective_user

    texto = f"""
👋 Olá {user.first_name}!

Bem-vindo ao *BigCommunity Task Manager*! 🚀

Este bot ajuda a organizar as tarefas da equipe de desenvolvimento.

*Comandos disponíveis:*
/nova - Criar nova tarefa
/tarefas - Ver todas as tarefas
/minhas - Ver suas tarefas
/changelog - Gerenciar mudanças do projeto
/stats - Ver estatísticas
/menu - Abrir menu principal
/topicoid - Ver ID do tópico atual
/settopico - Configurar tópico permitido
/ajuda - Ver esta mensagem

Use os botões inline para interagir com as tarefas! ✨
"""

    await update.message.reply_text(texto, parse_mode='Markdown')


async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ajuda"""
    # Verificar tópico
    if not await verificar_topico(update):
        topico_id = db.obter_config('topico_permitido')
        await update.message.reply_text(
            f"⚠️ *Uso restrito*\n\n"
            f"Este bot só funciona no tópico configurado (ID: `{topico_id}`).\n"
            f"Por favor, use os comandos dentro do tópico apropriado.",
            parse_mode='Markdown'
        )
        return

    texto = """
*📋 Comandos disponíveis:*

/nova - Criar uma nova tarefa
/tarefas - Listar todas as tarefas
/minhas - Ver apenas suas tarefas
/changelog - Gerenciar mudanças do projeto
/stats - Ver estatísticas do projeto
/menu - Abrir menu principal
/topicoid - Ver ID do tópico atual
/settopico - Configurar tópico permitido
/ajuda - Mostrar esta mensagem

*🎯 Como usar:*

1️⃣ *Criar tarefa:* Use /nova e siga os passos
2️⃣ *Ver tarefas:* Use /tarefas e filtre por categoria/status
3️⃣ *Gerenciar:* Clique na tarefa para ver opções
4️⃣ *Atualizar status:* Use os botões 🔄 ou ✅
5️⃣ *Editar/Deletar:* Botões ✏️ e 🗑️

*📌 Configurar Tópico:*
1️⃣ Entre no tópico desejado e use /topicoid
2️⃣ Copie o ID do tópico mostrado
3️⃣ Use /settopico [ID] para configurar
4️⃣ Para desabilitar: /settopico off

*🏷️ Categorias:*
• XFCE, Cinnamon, GNOME, Geral

*📊 Status:*
• ⏳ Pendente
• 🔄 Em andamento
• ✅ Resolvido

*⚡ Prioridades:*
• 🔴 Alta
• 🟡 Média
• 🟢 Baixa
"""

    await update.message.reply_text(texto, parse_mode='Markdown')


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - mostra estatísticas"""
    # Verificar tópico
    if not await verificar_topico(update):
        topico_id = db.obter_config('topico_permitido')
        await update.message.reply_text(
            f"⚠️ *Uso restrito*\n\n"
            f"Este bot só funciona no tópico configurado (ID: `{topico_id}`).\n"
            f"Por favor, use os comandos dentro do tópico apropriado.",
            parse_mode='Markdown'
        )
        return

    stats = db.estatisticas()

    texto = f"""
📊 *Estatísticas do BigCommunity*

📋 Total de tarefas: `{stats['total']}`

⏳ Pendentes: `{stats['pendentes']}`
🔄 Em andamento: `{stats['em_andamento']}`
✅ Resolvidas: `{stats['resolvidas']}`
"""

    # Estatísticas por categoria
    categorias = db.listar_categorias()
    for cat in categorias:
        tarefas_cat = db.listar_tarefas(categoria_id=cat['id'], status="pendente")
        if tarefas_cat:
            texto += f"\n{cat['nome']}: `{len(tarefas_cat)}` pendente(s)"

    await update.message.reply_text(texto, parse_mode='Markdown')


async def topicoid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /topicoid - mostra o ID do tópico atual"""
    message = update.message

    if message.is_topic_message:
        topic_id = message.message_thread_id
        texto = f"""
🔍 *Informações do Tópico*

📌 ID do Tópico: `{topic_id}`

_Use este ID para configurar o bot com /settopico {topic_id}_
"""
    else:
        texto = """
⚠️ *Este não é um tópico*

Este comando só funciona dentro de um tópico do grupo.
Por favor, execute-o dentro do tópico desejado.
"""

    await message.reply_text(texto, parse_mode='Markdown')


async def settopico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /settopico - configura o tópico permitido para o bot"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ Use: `/settopico <ID_do_tópico>`\n\n"
            "Para descobrir o ID, use /topicoid dentro do tópico desejado.",
            parse_mode='Markdown'
        )
        return

    try:
        topic_id = context.args[0]
        db.salvar_config('topico_permitido', topic_id)

        texto = f"""
✅ *Tópico configurado com sucesso!*

📌 ID do tópico permitido: `{topic_id}`

O bot agora só responderá comandos neste tópico.
Para desabilitar, use: `/settopico off`
"""
        await update.message.reply_text(texto, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(
            f"❌ Erro ao configurar tópico: {str(e)}",
            parse_mode='Markdown'
        )


async def verificar_topico(update: Update) -> bool:
    """Verifica se a mensagem está no tópico permitido"""
    topico_config = db.obter_config('topico_permitido')

    # Se não há configuração ou está desabilitado, permite tudo
    if not topico_config or topico_config == 'off':
        return True

    message = update.message or (update.callback_query.message if update.callback_query else None)

    if not message:
        return True

    # Verifica se a mensagem é de um tópico
    if message.is_topic_message:
        topic_id = str(message.message_thread_id)
        return topic_id == topico_config

    # Se não é tópico mas há configuração, bloqueia
    return False


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /menu - mostra menu de navegação completo"""
    # Verificar tópico
    if not await verificar_topico(update):
        topico_id = db.obter_config('topico_permitido')
        await update.message.reply_text(
            f"⚠️ *Uso restrito*\n\n"
            f"Este bot só funciona no tópico configurado (ID: `{topico_id}`).\n"
            f"Por favor, use os comandos dentro do tópico apropriado.",
            parse_mode='Markdown'
        )
        return

    texto = """
🏠 *Menu Principal - BigCommunity Task Manager*

_Escolha uma das opções abaixo para navegar:_
"""

    keyboard = [
        [InlineKeyboardButton("➕ Nova Tarefa", callback_data="menu_nova")],
        [
            InlineKeyboardButton("📋 Todas as Tarefas", callback_data="menu_tarefas"),
            InlineKeyboardButton("👤 Minhas Tarefas", callback_data="menu_minhas")
        ],
        [
            InlineKeyboardButton("📝 Changelog", callback_data="changelog_menu"),
            InlineKeyboardButton("📊 Estatísticas", callback_data="menu_stats")
        ],
        [
            InlineKeyboardButton("⏳ Pendentes", callback_data="menu_filtro_pendente"),
            InlineKeyboardButton("🔄 Em Andamento", callback_data="menu_filtro_em_andamento")
        ],
        [
            InlineKeyboardButton("✅ Concluídas", callback_data="menu_filtro_concluido"),
            InlineKeyboardButton("🖥️ Por Categoria", callback_data="menu_categorias")
        ],
        [InlineKeyboardButton("❓ Ajuda", callback_data="menu_ajuda")]
    ]

    await update.message.reply_text(
        texto,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============ CRIAR NOVA TAREFA ============

async def nova_tarefa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de criar nova tarefa"""
    # Verificar tópico
    if not await verificar_topico(update):
        topico_id = db.obter_config('topico_permitido')
        await update.message.reply_text(
            f"⚠️ *Uso restrito*\n\n"
            f"Este bot só funciona no tópico configurado (ID: `{topico_id}`).\n"
            f"Por favor, use os comandos dentro do tópico apropriado.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "📝 *Nova Tarefa*\n\n_Qual é o *título* da tarefa?_",
        parse_mode='Markdown'
    )
    return TITULO


async def receber_titulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe o título da tarefa"""
    context.user_data['titulo'] = update.message.text

    await update.message.reply_text(
        "📄 _Agora, descreva o problema/tarefa com mais detalhes:_",
        parse_mode='Markdown'
    )
    return DESCRICAO


async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a descrição da tarefa"""
    context.user_data['descricao'] = update.message.text

    # Buscar categorias do banco
    categorias = db.listar_categorias()
    keyboard = selecionar_categoria_nova_tarefa(categorias)

    await update.message.reply_text(
        "📁 Selecione a categoria:",
        reply_markup=keyboard
    )
    return CATEGORIA


async def receber_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a categoria via callback"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancelar_nova":
        await query.edit_message_text("❌ Criação de tarefa cancelada.")
        return ConversationHandler.END

    # Extrai o ID da categoria (formato: newcat_ID)
    categoria_id = int(query.data.replace("newcat_", ""))
    context.user_data['categoria_id'] = categoria_id

    # Buscar nome da categoria para mostrar
    categorias = db.listar_categorias()
    categoria_nome = next((c['nome'] for c in categorias if c['id'] == categoria_id), "Desconhecida")

    keyboard = selecionar_prioridade()

    await query.edit_message_text(
        f"✅ Categoria: *{categoria_nome}*\n\n⚡ Selecione a prioridade:",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return PRIORIDADE


async def receber_prioridade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a prioridade via callback"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancelar":
        await query.edit_message_text("❌ Criação de tarefa cancelada.")
        return ConversationHandler.END

    # Extrai a prioridade (formato: prior_NOME)
    prioridade = query.data.replace("prior_", "")
    context.user_data['prioridade'] = prioridade
    
    # Criar teclado para pular imagem
    keyboard = [[InlineKeyboardButton("⏭️ Pular", callback_data="pular_imagem")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Prioridade: *{prioridade}*\n\n_🖼️ Envie uma imagem (opcional) ou clique em Pular:_",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return IMAGEM


async def receber_imagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a imagem (opcional)"""
    if update.message and update.message.photo:
        # Pega a foto de maior qualidade
        photo = update.message.photo[-1]
        context.user_data['imagem_file_id'] = photo.file_id
        mensagem = "✅ Imagem recebida!"
    else:
        context.user_data['imagem_file_id'] = None
        mensagem = "✅ Sem imagem."
    
    # Criar a tarefa
    user = update.effective_user

    # Buscar nome da categoria para exibir
    categorias = db.listar_categorias()
    categoria_nome = next((c['nome'] for c in categorias if c['id'] == context.user_data['categoria_id']), "Desconhecida")

    tarefa_id = db.criar_tarefa(
        titulo=context.user_data['titulo'],
        descricao=context.user_data['descricao'],
        categoria_id=context.user_data['categoria_id'],
        autor_id=user.id,
        autor_nome=user.first_name,
        prioridade=context.user_data['prioridade'],
        imagem_file_id=context.user_data.get('imagem_file_id')
    )

    # Montar mensagem de sucesso
    emoji_pri = PRIORIDADE_EMOJI.get(context.user_data['prioridade'], '🟡')

    texto = f"""
✅ *Tarefa criada com sucesso!*

🆔 *ID:* #{tarefa_id}
📝 *Título:* {context.user_data['titulo']}
📁 *Categoria:* {categoria_nome}
⚡ *Prioridade:* {emoji_pri} {context.user_data['prioridade']}
👤 *Criada por:* {user.first_name}
"""
    
    await update.message.reply_text(texto, parse_mode='Markdown')
    
    # Limpar dados temporários
    context.user_data.clear()
    
    return ConversationHandler.END


async def pular_imagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pula o envio da imagem"""
    query = update.callback_query
    await query.answer()

    context.user_data['imagem_file_id'] = None

    # Criar a tarefa
    user = update.effective_user

    # Buscar nome da categoria para exibir
    categorias = db.listar_categorias()
    categoria_nome = next((c['nome'] for c in categorias if c['id'] == context.user_data['categoria_id']), "Desconhecida")

    tarefa_id = db.criar_tarefa(
        titulo=context.user_data['titulo'],
        descricao=context.user_data['descricao'],
        categoria_id=context.user_data['categoria_id'],
        autor_id=user.id,
        autor_nome=user.first_name,
        prioridade=context.user_data['prioridade'],
        imagem_file_id=None
    )

    emoji_pri = PRIORIDADE_EMOJI.get(context.user_data['prioridade'], '🟡')

    texto = f"""
✅ *Tarefa criada com sucesso!*

🆔 *ID:* #{tarefa_id}
📝 *Título:* {context.user_data['titulo']}
📁 *Categoria:* {categoria_nome}
⚡ *Prioridade:* {emoji_pri} {context.user_data['prioridade']}
👤 *Criada por:* {user.first_name}
"""

    await query.edit_message_text(texto, parse_mode='Markdown')
    
    context.user_data.clear()
    
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela a conversa atual"""
    await update.message.reply_text("❌ Operação cancelada.")
    context.user_data.clear()
    return ConversationHandler.END


# ============ CAPTURAR MENSAGENS DE TEXTO (edição/comentários) ============

async def processar_mensagem_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto para edição inline e comentários"""
    texto = update.message.text

    # Verificar se está criando tarefa via inline
    if context.user_data.get('aguardando') == 'titulo_tarefa':
        context.user_data['titulo'] = texto
        await update.message.reply_text(
            "📄 _Agora, descreva o problema/tarefa com mais detalhes:_",
            parse_mode='Markdown'
        )
        context.user_data['aguardando'] = 'descricao_tarefa'
        return

    if context.user_data.get('aguardando') == 'descricao_tarefa':
        context.user_data['descricao'] = texto
        categorias = db.listar_categorias()
        keyboard = selecionar_categoria_nova_tarefa(categorias)
        await update.message.reply_text(
            "📁 Selecione a categoria:",
            reply_markup=keyboard
        )
        context.user_data['aguardando'] = 'categoria_tarefa'
        return

    # Verificar se está processando changelog
    if 'editando_changelog_desc' in context.user_data or 'criando_changelog_cat' in context.user_data or 'criando_categoria_changelog' in context.user_data:
        await processar_changelog_texto(update, context)
        return

    # Verificar se está aguardando comentário
    if 'aguardando_comentario' in context.user_data:
        tarefa_id = context.user_data['aguardando_comentario']
        user = update.effective_user
        db.adicionar_comentario(tarefa_id, user.id, user.first_name, texto)
        await update.message.reply_text(f"✅ Comentário adicionado à tarefa #{tarefa_id}!")
        del context.user_data['aguardando_comentario']

        # Mostrar a tarefa novamente
        tarefa = db.obter_tarefa(tarefa_id)
        if tarefa:
            texto_tarefa = formatar_tarefa(tarefa)
            keyboard = acoes_tarefa(tarefa_id, tarefa['autor_id'], user.id)

            if tarefa['imagem_file_id']:
                await update.message.reply_photo(
                    photo=tarefa['imagem_file_id'],
                    caption=texto_tarefa,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    texto_tarefa,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
        return

    # Verificar se está editando título
    if 'editando_titulo' in context.user_data:
        tarefa_id = context.user_data['editando_titulo']
        user = update.effective_user
        db.atualizar_tarefa(tarefa_id, titulo=texto)
        await update.message.reply_text(f"✅ Título da tarefa #{tarefa_id} atualizado!")
        del context.user_data['editando_titulo']

        # Mostrar a tarefa novamente
        tarefa = db.obter_tarefa(tarefa_id)
        if tarefa:
            texto_tarefa = formatar_tarefa(tarefa)
            keyboard = acoes_tarefa(tarefa_id, tarefa['autor_id'], user.id)

            if tarefa['imagem_file_id']:
                await update.message.reply_photo(
                    photo=tarefa['imagem_file_id'],
                    caption=texto_tarefa,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    texto_tarefa,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
        return

    # Verificar se está editando descrição
    if 'editando_descricao' in context.user_data:
        tarefa_id = context.user_data['editando_descricao']
        user = update.effective_user
        db.atualizar_tarefa(tarefa_id, descricao=texto)
        await update.message.reply_text(f"✅ Descrição da tarefa #{tarefa_id} atualizada!")
        del context.user_data['editando_descricao']

        # Mostrar a tarefa novamente
        tarefa = db.obter_tarefa(tarefa_id)
        if tarefa:
            texto_tarefa = formatar_tarefa(tarefa)
            keyboard = acoes_tarefa(tarefa_id, tarefa['autor_id'], user.id)

            if tarefa['imagem_file_id']:
                await update.message.reply_photo(
                    photo=tarefa['imagem_file_id'],
                    caption=texto_tarefa,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    texto_tarefa,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
        return


# ============ CHANGELOG ============

async def menu_changelog(update_or_query, is_command=True):
    """Mostra o menu principal de changelogs"""
    # Verificar tópico se for comando
    if is_command:
        if not await verificar_topico(update_or_query):
            topico_id = db.obter_config('topico_permitido')
            await update_or_query.message.reply_text(
                f"⚠️ *Uso restrito*\n\n"
                f"Este bot só funciona no tópico configurado (ID: `{topico_id}`).\n"
                f"Por favor, use os comandos dentro do tópico apropriado.",
                parse_mode='Markdown'
            )
            return

    texto = "📝 *Changelog - BigCommunity*\n\n"
    texto += "_Gerencie as mudanças e atualizações do projeto:_"

    keyboard = menu_changelog_principal()

    if is_command:
        await update_or_query.message.reply_text(texto, parse_mode='Markdown', reply_markup=keyboard)
    else:
        # É um query (callback)
        if update_or_query.message.photo:
            chat_id = update_or_query.message.chat_id
            await update_or_query.message.delete()
            await update_or_query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown', reply_markup=keyboard)
        else:
            await update_or_query.edit_message_text(texto, parse_mode='Markdown', reply_markup=keyboard)


async def listar_changelogs_inline(query, filtro=None, categoria=None):
    """Lista changelogs com filtros"""
    if filtro == "pinados":
        changelogs = db.listar_changelogs(pinado=True)
        titulo = "📌 *Changelogs Pinados*"
    elif categoria:
        changelogs = db.listar_changelogs(categoria=categoria)
        titulo = f"📍 *Changelog - {categoria}*"
    else:
        changelogs = db.listar_changelogs()
        titulo = "📋 *Todos os Changelogs*"

    if not changelogs:
        texto = f"{titulo}\n\n❌ Nenhum changelog encontrado."
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="changelog_menu")]]
        await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    texto = f"{titulo}\n\n"

    for log in changelogs[:15]:  # Limita a 15
        pin_emoji = "📌 " if log['pinado'] else ""
        data = datetime.fromisoformat(log['data_criacao'])
        texto += f"{pin_emoji}📍 `{data.strftime('%d/%m/%Y %H:%M')}` - *{log['autor_nome']}*\n"
        texto += f"*{log['categoria']}:* {log['descricao'][:80]}{'...' if len(log['descricao']) > 80 else ''}\n\n"

    # Criar botões para cada changelog
    buttons = []
    for log in changelogs[:15]:
        pin_emoji = "📌 " if log['pinado'] else ""
        data = datetime.fromisoformat(log['data_criacao'])
        label = f"{pin_emoji}#{log['id']} - {log['categoria']} ({data.strftime('%d/%m %H:%M')})"
        buttons.append([InlineKeyboardButton(label, callback_data=f"changelog_ver_{log['id']}")])

    buttons.append([InlineKeyboardButton("🔙 Voltar", callback_data="changelog_menu")])

    await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(buttons))


async def mostrar_changelog(query, changelog_id: int):
    """Mostra detalhes de um changelog"""
    changelog = db.obter_changelog(changelog_id)

    if not changelog:
        await query.edit_message_text("❌ Changelog não encontrado.")
        return

    pin_emoji = "📌 " if changelog['pinado'] else ""
    data = datetime.fromisoformat(changelog['data_criacao'])

    texto = f"{pin_emoji}*Changelog #{changelog['id']}*\n\n"
    texto += f"📍 *Categoria:* `{changelog['categoria']}`\n"
    texto += f"👤 *Autor:* `{changelog['autor_nome']}`\n"
    texto += f"📅 *Data:* `{data.strftime('%d/%m/%Y %H:%M')}`\n\n"
    texto += f"📝 *Descrição:*\n{changelog['descricao']}"

    user_id = query.from_user.id
    keyboard = acoes_changelog(changelog_id, changelog['autor_id'], user_id, changelog['pinado'])

    if query.message.photo:
        chat_id = query.message.chat_id
        await query.message.delete()
        await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown', reply_markup=keyboard)
    else:
        await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=keyboard)


async def processar_changelog_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa entrada de texto para changelog inline"""
    texto = update.message.text
    user = update.effective_user

    # Criando nova categoria
    if 'criando_categoria_changelog' in context.user_data:
        sucesso = db.adicionar_categoria_changelog(texto)
        if sucesso:
            await update.message.reply_text(
                f"✅ Categoria *{texto}* criada com sucesso!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📝 Criar Changelog", callback_data="changelog_novo"),
                    InlineKeyboardButton("🔙 Menu", callback_data="changelog_menu")
                ]])
            )
        else:
            await update.message.reply_text(
                f"❌ Categoria *{texto}* já existe!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Menu", callback_data="changelog_menu")
                ]])
            )
        del context.user_data['criando_categoria_changelog']
        return

    # Editando descrição de changelog
    if 'editando_changelog_desc' in context.user_data:
        changelog_id = context.user_data['editando_changelog_desc']
        db.atualizar_changelog(changelog_id, descricao=texto)
        await update.message.reply_text(f"✅ Descrição do changelog #{changelog_id} atualizada!")
        del context.user_data['editando_changelog_desc']
        return

    # Criando novo changelog (aguardando descrição)
    if 'criando_changelog_cat' in context.user_data:
        categoria = context.user_data['criando_changelog_cat']
        changelog_id = db.criar_changelog(categoria, texto, user.id, user.first_name)

        pin_emoji = "📍"
        texto_sucesso = f"✅ *Changelog criado com sucesso!*\n\n"
        texto_sucesso += f"{pin_emoji} *Categoria:* {categoria}\n"
        texto_sucesso += f"📝 *Descrição:* {texto}\n"
        texto_sucesso += f"👤 *Por:* {user.first_name}"

        keyboard = [[InlineKeyboardButton("📝 Ver Changelog", callback_data=f"changelog_ver_{changelog_id}")],
                    [InlineKeyboardButton("🔙 Menu Changelog", callback_data="changelog_menu")]]

        await update.message.reply_text(texto_sucesso, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        del context.user_data['criando_changelog_cat']
        return


# ============ LISTAR E VISUALIZAR TAREFAS ============

async def listar_tarefas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todas as tarefas com filtros"""
    # Verificar tópico
    if not await verificar_topico(update):
        topico_id = db.obter_config('topico_permitido')
        await update.message.reply_text(
            f"⚠️ *Uso restrito*\n\n"
            f"Este bot só funciona no tópico configurado (ID: `{topico_id}`).\n"
            f"Por favor, use os comandos dentro do tópico apropriado.",
            parse_mode='Markdown'
        )
        return

    tarefas = db.listar_tarefas()

    if not tarefas:
        await update.message.reply_text(
            "📋 Nenhuma tarefa cadastrada ainda.\n\nUse /nova para criar a primeira tarefa!"
        )
        return
    
    texto = "📋 *Tarefas do BigCommunity*\n\n"
    texto += "_Use os filtros abaixo para organizar:_\n\n"

    # Mostrar resumo
    for status in STATUS:
        count = len([t for t in tarefas if t['status'] == status])
        emoji = STATUS_EMOJI.get(status, '📌')
        # Substituir underscore por espaço e capitalizar
        status_nome = status.replace('_', ' ').title()
        texto += f"{emoji} {status_nome}: `{count}`\n"
    
    await update.message.reply_text(
        texto,
        parse_mode='Markdown',
        reply_markup=keyboard_filtros()
    )


async def minhas_tarefas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista tarefas do usuário"""
    # Verificar tópico
    if not await verificar_topico(update):
        topico_id = db.obter_config('topico_permitido')
        await update.message.reply_text(
            f"⚠️ *Uso restrito*\n\n"
            f"Este bot só funciona no tópico configurado (ID: `{topico_id}`).\n"
            f"Por favor, use os comandos dentro do tópico apropriado.",
            parse_mode='Markdown'
        )
        return
    user = update.effective_user
    tarefas = db.listar_tarefas(autor_id=user.id)
    
    if not tarefas:
        await update.message.reply_text(
            "📋 Você ainda não criou nenhuma tarefa.\n\nUse /nova para criar uma!"
        )
        return
    
    texto = f"📋 *Suas tarefas ({len(tarefas)})*\n\n"
    
    for tarefa in tarefas[:10]:  # Limita a 10 tarefas
        emoji_status = STATUS_EMOJI.get(tarefa['status'], '📌')
        emoji_pri = PRIORIDADE_EMOJI.get(tarefa['prioridade'], '🟡')
        status_nome = tarefa['status'].replace('_', ' ').title()

        texto += f"{emoji_status} #{tarefa['id']} - {tarefa['titulo']}\n"
        texto += f"   {emoji_pri} {tarefa['categoria']} | {status_nome}\n\n"
    
    if len(tarefas) > 10:
        texto += f"... e mais {len(tarefas) - 10} tarefas.\n"
    
    await update.message.reply_text(texto, parse_mode='Markdown')


def formatar_tarefa(tarefa: dict) -> str:
    """Formata uma tarefa para exibição"""
    emoji_status = STATUS_EMOJI.get(tarefa['status'], '📌')
    emoji_pri = PRIORIDADE_EMOJI.get(tarefa['prioridade'], '🟡')
    status_nome = tarefa['status'].replace('_', ' ').title()
    prioridade_nome = tarefa['prioridade'].title()

    texto = f"*Tarefa #{tarefa['id']}*\n\n"
    texto += f"📝 *Título:* {tarefa['titulo']}\n"
    texto += f"📄 *Descrição:* {tarefa['descricao']}\n\n"
    texto += f"📁 *Categoria:* `{tarefa['categoria']}`\n"
    texto += f"{emoji_status} *Status:* `{status_nome}`\n"
    texto += f"{emoji_pri} *Prioridade:* `{prioridade_nome}`\n"
    texto += f"👤 *Criada por:* `{tarefa['autor_nome']}`\n"

    # Data de criação
    data_criacao = datetime.fromisoformat(tarefa['data_criacao'])
    texto += f"📅 *Criada em:* `{data_criacao.strftime('%d/%m/%Y %H:%M')}`\n"

    if tarefa['data_conclusao']:
        data_conclusao = datetime.fromisoformat(tarefa['data_conclusao'])
        texto += f"✅ *Concluída em:* `{data_conclusao.strftime('%d/%m/%Y %H:%M')}`\n"
    
    return texto


# ============ CALLBACKS ============

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para callbacks dos botões inline"""
    query = update.callback_query
    await query.answer()

    data = query.data

    # Filtros de listagem
    if data.startswith("filtro_"):
        await handle_filtro(query, context)
        return

    # Filtrar por categoria (vindo do menu de categorias)
    elif data.startswith("cat_") and not data.startswith("cancelar"):
        categoria_id = int(data.split("_")[1])
        tarefas = db.listar_tarefas(categoria_id=categoria_id)

        # Buscar nome da categoria
        categorias = db.listar_categorias()
        categoria_nome = next((c['nome'] for c in categorias if c['id'] == categoria_id), "Desconhecida")

        if not tarefas:
            await query.edit_message_text(
                f"📁 *Categoria: {categoria_nome}*\n\n❌ Nenhuma tarefa encontrada.",
                reply_markup=keyboard_filtros(),
                parse_mode='Markdown'
            )
            return

        # Mostrar lista de tarefas
        texto = f"*📁 Categoria: {categoria_nome}*\n\n"

        buttons = []
        for tarefa in tarefas[:20]:  # Limita a 20
            emoji_status = STATUS_EMOJI.get(tarefa['status'], '📌')
            emoji_pri = PRIORIDADE_EMOJI.get(tarefa['prioridade'], '🟡')

            label = f"{emoji_status} {emoji_pri} #{tarefa['id']} - {tarefa['titulo'][:30]}"
            buttons.append([InlineKeyboardButton(label, callback_data=f"ver_{tarefa['id']}")])

        buttons.append([InlineKeyboardButton("🔙 Voltar aos filtros", callback_data="voltar_filtros")])

        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Ver detalhes de uma tarefa
    elif data.startswith("ver_"):
        tarefa_id = int(data.split("_")[1])
        await mostrar_tarefa(query, tarefa_id)
        return

    # Mudar status
    elif data.startswith("status_"):
        parts = data.split("_")
        tarefa_id = int(parts[1])
        novo_status = "_".join(parts[2:])
        await mudar_status(query, tarefa_id, novo_status)
        return

    # Deletar tarefa
    elif data.startswith("deletar_"):
        tarefa_id = int(data.split("_")[1])
        await confirmar_delecao(query, tarefa_id)
        return

    # Confirmar deleção
    elif "confirma_del_" in data:
        tarefa_id = int(data.split("_")[2])
        await deletar_tarefa(query, tarefa_id)
        return
    
    elif "cancelar_del_" in data:
        tarefa_id = int(data.split("_")[2])
        await mostrar_tarefa(query, tarefa_id)
        return

    # Editar tarefa
    elif data.startswith("editar_"):
        tarefa_id = int(data.split("_")[1])
        await mostrar_opcoes_edicao(query, tarefa_id)
        return
    
    # Comentários
    elif data.startswith("comentarios_"):
        tarefa_id = int(data.split("_")[1])
        await mostrar_comentarios(query, tarefa_id)
        return

    # Adicionar comentário inline
    elif data.startswith("add_comentario_"):
        tarefa_id = int(data.split("_")[2])
        context.user_data['aguardando_comentario'] = tarefa_id
        await query.answer("✍️ Digite seu comentário agora...")
        texto = f"💬 *Comentar na Tarefa #{tarefa_id}*\n\n"
        texto += "_Digite seu comentário abaixo e envie:_"
        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown')
        else:
            await query.edit_message_text(texto, parse_mode='Markdown')
        return

    # Editar título
    elif data.startswith("edit_titulo_"):
        tarefa_id = int(data.split("_")[2])
        context.user_data['editando_titulo'] = tarefa_id
        await query.answer("✍️ Digite o novo título...")
        texto = f"📝 *Editar Título da Tarefa #{tarefa_id}*\n\n"
        texto += "_Digite o novo título e envie:_"
        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown')
        else:
            await query.edit_message_text(texto, parse_mode='Markdown')
        return

    # Editar descrição
    elif data.startswith("edit_desc_"):
        tarefa_id = int(data.split("_")[2])
        context.user_data['editando_descricao'] = tarefa_id
        await query.answer("✍️ Digite a nova descrição...")
        texto = f"📄 *Editar Descrição da Tarefa #{tarefa_id}*\n\n"
        texto += "_Digite a nova descrição e envie:_"
        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown')
        else:
            await query.edit_message_text(texto, parse_mode='Markdown')
        return

    # Editar prioridade
    elif data.startswith("edit_prior_"):
        tarefa_id = int(data.split("_")[2])
        texto = f"🎯 *Editar Prioridade da Tarefa #{tarefa_id}*\n\n"
        texto += "Selecione a nova prioridade:"
        keyboard = [
            [InlineKeyboardButton("🔴 Alta", callback_data=f"set_prior_{tarefa_id}_alta")],
            [InlineKeyboardButton("🟡 Média", callback_data=f"set_prior_{tarefa_id}_media")],
            [InlineKeyboardButton("🟢 Baixa", callback_data=f"set_prior_{tarefa_id}_baixa")],
            [InlineKeyboardButton("❌ Cancelar", callback_data=f"ver_{tarefa_id}")]
        ]
        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Salvar prioridade
    elif data.startswith("set_prior_"):
        parts = data.split("_")
        tarefa_id = int(parts[2])
        prioridade = parts[3]
        db.atualizar_tarefa(tarefa_id, prioridade=prioridade)
        await query.answer(f"✅ Prioridade atualizada para {prioridade}!")
        await mostrar_tarefa(query, tarefa_id)
        return

    # Voltar para lista
    elif data == "voltar_lista":
        await voltar_lista(query)
        return

    # Voltar para filtros (mesmo comportamento que voltar_lista)
    elif data == "voltar_filtros":
        await voltar_lista(query)
        return

    # Voltar ao menu principal
    elif data == "voltar_menu":
        await handle_menu(query, "menu_voltar", context)
        return

    # Seleção de categoria para nova tarefa inline
    elif data.startswith("newcat_") and context.user_data.get('aguardando') == 'categoria_tarefa':
        categoria_id = int(data.replace("newcat_", ""))
        context.user_data['categoria_id'] = categoria_id

        # Pedir prioridade
        await query.edit_message_text(
            "🎯 Selecione a prioridade:",
            reply_markup=selecionar_prioridade()
        )
        context.user_data['aguardando'] = 'prioridade_tarefa'
        return

    # Cancelar criação inline
    elif data == "cancelar_nova" and context.user_data.get('criando_tarefa_inline'):
        await query.edit_message_text("❌ Criação de tarefa cancelada.")
        context.user_data.clear()
        return

    # Seleção de prioridade para nova tarefa inline
    elif data.startswith("prior_") and context.user_data.get('aguardando') == 'prioridade_tarefa':
        prioridade = data.replace("prior_", "")
        context.user_data['prioridade'] = prioridade

        # Criar a tarefa
        user = query.from_user
        tarefa_id = db.criar_tarefa(
            titulo=context.user_data['titulo'],
            descricao=context.user_data.get('descricao', ''),
            categoria_id=context.user_data['categoria_id'],
            prioridade=prioridade,
            autor_id=user.id,
            autor_nome=user.first_name
        )

        await query.edit_message_text(
            f"✅ *Tarefa criada com sucesso!*\n\n"
            f"ID: #{tarefa_id}\n"
            f"Título: {context.user_data['titulo']}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("👁️ Ver tarefa", callback_data=f"ver_{tarefa_id}"),
                InlineKeyboardButton("📋 Ver todas", callback_data="menu_tarefas")
            ]])
        )

        # Limpar dados
        context.user_data.clear()
        return

    # Changelog
    elif data.startswith("changelog_") or data.startswith("newlog_"):
        await handle_changelog(query, data, context)
        return

    # Menu principal
    elif data.startswith("menu_"):
        await handle_menu(query, data, context)
        return


async def handle_menu(query, data: str, context):
    """Processa opções do menu principal"""
    user = query.from_user

    if data == "menu_nova":
        # Iniciar processo de criação de tarefa
        context.user_data['criando_tarefa_inline'] = True
        await query.edit_message_text(
            "📝 *Nova Tarefa*\n\n_Qual é o *título* da tarefa?_",
            parse_mode='Markdown'
        )
        context.user_data['aguardando'] = 'titulo_tarefa'

    elif data == "menu_tarefas":
        tarefas = db.listar_tarefas()

        if not tarefas:
            await query.edit_message_text(
                "📋 *Todas as Tarefas*\n\n❌ Nenhuma tarefa cadastrada ainda.\n\nUse /nova para criar a primeira tarefa!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_voltar")
                ]])
            )
            return

        texto = "📋 *Tarefas do BigCommunity*\n\n"
        texto += "_Use os filtros abaixo para organizar:_\n\n"

        for status in STATUS:
            count = len([t for t in tarefas if t['status'] == status])
            emoji = STATUS_EMOJI.get(status, '📌')
            status_nome = status.replace('_', ' ').title()
            texto += f"{emoji} {status_nome}: `{count}`\n"

        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=keyboard_filtros()
        )

    elif data == "menu_minhas":
        tarefas = db.listar_tarefas(autor_id=user.id)

        if not tarefas:
            await query.edit_message_text(
                "📋 *Minhas Tarefas*\n\n❌ Você ainda não criou nenhuma tarefa.\n\nUse /nova para criar uma!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_voltar")
                ]])
            )
            return

        texto = f"📋 *Suas tarefas ({len(tarefas)})*\n\n"

        buttons = []
        for tarefa in tarefas[:20]:
            emoji_status = STATUS_EMOJI.get(tarefa['status'], '📌')
            emoji_pri = PRIORIDADE_EMOJI.get(tarefa['prioridade'], '🟡')

            label = f"{emoji_status} {emoji_pri} #{tarefa['id']} - {tarefa['titulo'][:30]}"
            buttons.append([InlineKeyboardButton(label, callback_data=f"ver_{tarefa['id']}")])

        buttons.append([InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_voltar")])

        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "menu_stats":
        stats = db.estatisticas()

        texto = f"""
📊 *Estatísticas do BigCommunity*

📋 Total de tarefas: `{stats['total']}`

⏳ Pendentes: `{stats['pendentes']}`
🔄 Em andamento: `{stats['em_andamento']}`
✅ Resolvidas: `{stats['resolvidas']}`
"""

        categorias = db.listar_categorias()
        for cat in categorias:
            tarefas_cat = db.listar_tarefas(categoria_id=cat['id'], status="pendente")
            if tarefas_cat:
                texto += f"\n{cat['nome']}: `{len(tarefas_cat)}` pendente(s)"

        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_voltar")
            ]])
        )

    elif data == "menu_ajuda":
        texto = """
*📋 Comandos disponíveis:*

/nova - Criar uma nova tarefa
/tarefas - Listar todas as tarefas
/minhas - Ver apenas suas tarefas
/changelog - Gerenciar mudanças do projeto
/stats - Ver estatísticas do projeto
/menu - Abrir este menu
/topicoid - Ver ID do tópico atual
/settopico - Configurar tópico permitido
/ajuda - Mostrar esta mensagem

*🎯 Como usar:*

1️⃣ *Criar tarefa:* Use /nova e siga os passos
2️⃣ *Ver tarefas:* Use /tarefas e filtre por categoria/status
3️⃣ *Gerenciar:* Clique na tarefa para ver opções
4️⃣ *Atualizar status:* Use os botões 🔄 ou ✅
5️⃣ *Editar/Deletar:* Botões ✏️ e 🗑️

*📌 Configurar Tópico:*
1️⃣ Entre no tópico desejado e use /topicoid
2️⃣ Copie o ID do tópico mostrado
3️⃣ Use /settopico [ID] para configurar
4️⃣ Para desabilitar: /settopico off

*🏷️ Categorias:*
• XFCE, Cinnamon, GNOME, Geral

*📊 Status:*
• ⏳ Pendente
• 🔄 Em andamento
• ✅ Resolvido

*⚡ Prioridades:*
• 🔴 Alta
• 🟡 Média
• 🟢 Baixa
"""

        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_voltar")
            ]])
        )

    elif data == "menu_filtro_pendente":
        tarefas = db.listar_tarefas(status="pendente")
        await mostrar_lista_filtrada(query, tarefas, "⏳ Pendentes")

    elif data == "menu_filtro_em_andamento":
        tarefas = db.listar_tarefas(status="em_andamento")
        await mostrar_lista_filtrada(query, tarefas, "🔄 Em Andamento")

    elif data == "menu_filtro_concluido":
        tarefas = db.listar_tarefas(status="concluido")
        await mostrar_lista_filtrada(query, tarefas, "✅ Concluídas")

    elif data == "menu_categorias":
        categorias = db.listar_categorias()

        buttons = []
        for cat in categorias:
            buttons.append([InlineKeyboardButton(f"🖥️ {cat['nome']}", callback_data=f"cat_{cat['id']}")])

        buttons.append([InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_voltar")])

        await query.edit_message_text(
            "*🖥️ Selecione uma categoria:*",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )

    elif data == "menu_voltar":
        texto = """
🏠 *Menu Principal - BigCommunity Task Manager*

_Escolha uma das opções abaixo para navegar:_
"""

        keyboard = [
            [InlineKeyboardButton("➕ Nova Tarefa", callback_data="menu_nova")],
            [
                InlineKeyboardButton("📋 Todas as Tarefas", callback_data="menu_tarefas"),
                InlineKeyboardButton("👤 Minhas Tarefas", callback_data="menu_minhas")
            ],
            [
                InlineKeyboardButton("📝 Changelog", callback_data="changelog_menu"),
                InlineKeyboardButton("📊 Estatísticas", callback_data="menu_stats")
            ],
            [
                InlineKeyboardButton("⏳ Pendentes", callback_data="menu_filtro_pendente"),
                InlineKeyboardButton("🔄 Em Andamento", callback_data="menu_filtro_em_andamento")
            ],
            [
                InlineKeyboardButton("✅ Concluídas", callback_data="menu_filtro_concluido"),
                InlineKeyboardButton("🖥️ Por Categoria", callback_data="menu_categorias")
            ],
            [InlineKeyboardButton("❓ Ajuda", callback_data="menu_ajuda")]
        ]

        # Verificar se mensagem tem foto
        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(
                chat_id=chat_id,
                text=texto,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                texto,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )


async def handle_changelog(query, data: str, context):
    """Processa opções do menu de changelog"""
    if data == "changelog_menu":
        await menu_changelog(query, is_command=False)

    elif data == "changelog_novo":
        # Mostrar seleção de categoria
        texto = "📝 *Novo Changelog*\n\n_Selecione a categoria:_"
        categorias = db.listar_categorias_changelog()
        keyboard = selecionar_categoria_changelog(categorias)
        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown', reply_markup=keyboard)
        else:
            await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=keyboard)

    elif data == "changelog_nova_cat":
        # Criar nova categoria
        context.user_data['criando_categoria_changelog'] = True
        await query.answer("✍️ Digite o nome da nova categoria...")
        texto = "➕ *Nova Categoria de Changelog*\n\n_Digite o nome da nova categoria:_"
        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown')
        else:
            await query.edit_message_text(texto, parse_mode='Markdown')

    elif data.startswith("newlog_idx_"):
        # Categoria selecionada por índice, pedir descrição
        idx = int(data.replace("newlog_idx_", ""))
        categorias = db.listar_categorias_changelog()

        if idx >= len(categorias):
            await query.answer("❌ Categoria inválida!", show_alert=True)
            return

        categoria = categorias[idx]
        context.user_data['criando_changelog_cat'] = categoria

        texto = f"📝 *Novo Changelog - {categoria}*\n\n_Digite a descrição da mudança:_"

        try:
            if query.message.photo:
                chat_id = query.message.chat_id
                await query.message.delete()
                await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown')
            else:
                await query.edit_message_text(texto, parse_mode='Markdown')
            await query.answer("✍️ Digite a descrição do changelog...")
        except Exception as e:
            logger.error(f"Erro ao processar newlog_idx: {e}")
            await query.answer(f"Erro: {str(e)}", show_alert=True)

    elif data == "changelog_listar_todos":
        await listar_changelogs_inline(query)

    elif data == "changelog_listar_pinados":
        await listar_changelogs_inline(query, filtro="pinados")

    elif data == "changelog_categorias":
        # Mostrar menu de categorias
        texto = "*🖥️ Filtrar por Categoria:*"
        categorias = db.listar_categorias_changelog()
        keyboard = menu_filtro_categoria_changelog(categorias)
        await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=keyboard)

    elif data.startswith("changelog_catidx_"):
        idx = int(data.replace("changelog_catidx_", ""))
        categorias = db.listar_categorias_changelog()
        categoria = categorias[idx]
        await listar_changelogs_inline(query, categoria=categoria)

    elif data == "changelog_stats":
        # Mostrar estatísticas
        stats = db.estatisticas_changelog()

        texto = "📊 *Estatísticas de Changelog*\n\n"
        texto += f"📋 *Total de changelogs:* `{stats['total']}`\n"
        texto += f"📌 *Pinados:* `{stats['pinados']}`\n\n"

        # Por categoria
        if stats['por_categoria']:
            texto += "*📁 Por Categoria:*\n"
            for cat, count in stats['por_categoria'].items():
                texto += f"• {cat}: `{count}`\n"
            texto += "\n"

        # Por autor
        if stats['por_autor']:
            texto += "*👥 Por Autor:*\n"
            for autor, count in stats['por_autor'].items():
                texto += f"• {autor}: `{count}`\n"

        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="changelog_menu")]]
        await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("changelog_ver_"):
        changelog_id = int(data.split("_")[2])
        await mostrar_changelog(query, changelog_id)

    elif data.startswith("changelog_pin_"):
        changelog_id = int(data.split("_")[2])
        db.alternar_pinagem_changelog(changelog_id)
        changelog = db.obter_changelog(changelog_id)
        pin_status = "pinado" if changelog['pinado'] else "despinado"
        await query.answer(f"✅ Changelog {pin_status}!")
        await mostrar_changelog(query, changelog_id)

    elif data.startswith("changelog_editar_"):
        changelog_id = int(data.split("_")[2])
        texto = f"✏️ *Editar Changelog #{changelog_id}*\n\n_Selecione o que deseja editar:_"
        keyboard = menu_edicao_changelog(changelog_id)
        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown', reply_markup=keyboard)
        else:
            await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=keyboard)

    elif data.startswith("changelog_edit_desc_"):
        changelog_id = int(data.split("_")[3])
        context.user_data['editando_changelog_desc'] = changelog_id
        await query.answer("✍️ Digite a nova descrição...")
        texto = f"📝 *Editar Descrição - Changelog #{changelog_id}*\n\n_Digite a nova descrição:_"
        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown')
        else:
            await query.edit_message_text(texto, parse_mode='Markdown')

    elif data.startswith("changelog_edit_cat_"):
        changelog_id = int(data.split("_")[3])
        texto = f"📁 *Editar Categoria - Changelog #{changelog_id}*\n\n_Selecione a nova categoria:_"
        categorias = db.listar_categorias_changelog()
        buttons = []
        for idx, cat in enumerate(categorias):
            buttons.append([InlineKeyboardButton(f"📍 {cat}", callback_data=f"changelog_setcatidx_{changelog_id}_{idx}")])
        buttons.append([InlineKeyboardButton("❌ Cancelar", callback_data=f"changelog_ver_{changelog_id}")])

        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("changelog_setcatidx_"):
        parts = data.split("_")
        changelog_id = int(parts[2])
        idx = int(parts[3])
        categorias = db.listar_categorias_changelog()
        categoria = categorias[idx]
        db.atualizar_changelog(changelog_id, categoria=categoria)
        await query.answer(f"✅ Categoria atualizada para {categoria}!")
        await mostrar_changelog(query, changelog_id)

    elif data.startswith("changelog_deletar_"):
        changelog_id = int(data.split("_")[2])
        changelog = db.obter_changelog(changelog_id)
        texto = f"⚠️ *Confirmar exclusão*\n\n"
        texto += f"Tem certeza que deseja deletar o changelog:\n\n"
        texto += f"#{changelog_id} - {changelog['categoria']}\n"
        texto += f"{changelog['descricao'][:100]}...\n\n"
        texto += "Esta ação não pode ser desfeita!"
        keyboard = confirmar_delecao_changelog(changelog_id)

        if query.message.photo:
            chat_id = query.message.chat_id
            await query.message.delete()
            await query.get_bot().send_message(chat_id=chat_id, text=texto, parse_mode='Markdown', reply_markup=keyboard)
        else:
            await query.edit_message_text(texto, parse_mode='Markdown', reply_markup=keyboard)

    elif data.startswith("changelog_confirma_del_"):
        changelog_id = int(data.split("_")[3])
        db.deletar_changelog(changelog_id)
        await query.edit_message_text(
            f"✅ Changelog #{changelog_id} deletado com sucesso!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Menu Changelog", callback_data="changelog_menu")
            ]])
        )


async def mostrar_lista_filtrada(query, tarefas, titulo: str):
    """Mostra lista de tarefas filtrada"""
    if not tarefas:
        await query.edit_message_text(
            f"*{titulo}*\n\n❌ Nenhuma tarefa encontrada.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_voltar")
            ]])
        )
        return

    texto = f"*{titulo}*\n\n"

    buttons = []
    for tarefa in tarefas[:20]:
        emoji_status = STATUS_EMOJI.get(tarefa['status'], '📌')
        emoji_pri = PRIORIDADE_EMOJI.get(tarefa['prioridade'], '🟡')

        label = f"{emoji_status} {emoji_pri} #{tarefa['id']} - {tarefa['titulo'][:30]}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"ver_{tarefa['id']}")])

    buttons.append([InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_voltar")])

    await query.edit_message_text(
        texto,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def handle_filtro(query, context):
    """Processa filtros de tarefas"""
    data = query.data
    
    # Extrair filtro
    if "filtro_cat_" in data:
        categoria = data.replace("filtro_cat_", "")
        tarefas = db.listar_tarefas(categoria=categoria if categoria != "Todas" else None)
        titulo = f"📁 Categoria: {categoria}"
    
    elif "filtro_status_" in data:
        status = data.replace("filtro_status_", "")
        tarefas = db.listar_tarefas(status=status)
        status_nome = status.replace('_', ' ').title()
        titulo = f"{STATUS_EMOJI.get(status, '📌')} Status: {status_nome}"
    
    elif data == "filtro_refresh":
        tarefas = db.listar_tarefas()
        titulo = "📋 Todas as tarefas"

    elif data == "filtro_categorias":
        # Mostrar menu de categorias
        categorias = db.listar_categorias()
        keyboard = menu_categorias(categorias)
        await query.edit_message_text(
            "*🖥️ Selecione uma categoria:*",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return

    else:
        return
    
    if not tarefas:
        await query.edit_message_text(
            f"{titulo}\n\n❌ Nenhuma tarefa encontrada.",
            reply_markup=keyboard_filtros()
        )
        return
    
    # Mostrar lista de tarefas
    texto = f"*{titulo}*\n\n"
    
    buttons = []
    for tarefa in tarefas[:20]:  # Limita a 20
        emoji_status = STATUS_EMOJI.get(tarefa['status'], '📌')
        emoji_pri = PRIORIDADE_EMOJI.get(tarefa['prioridade'], '🟡')
        
        label = f"{emoji_status} {emoji_pri} #{tarefa['id']} - {tarefa['titulo'][:30]}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"ver_{tarefa['id']}")])
    
    buttons.append([InlineKeyboardButton("🔙 Voltar aos filtros", callback_data="voltar_filtros")])
    
    await query.edit_message_text(
        texto,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def mostrar_tarefa(query, tarefa_id: int):
    """Mostra detalhes de uma tarefa"""
    tarefa = db.obter_tarefa(tarefa_id)

    if not tarefa:
        await query.edit_message_text("❌ Tarefa não encontrada.")
        return

    texto = formatar_tarefa(tarefa)

    # Obter ID do usuário que está visualizando
    user_id = query.from_user.id

    # Criar keyboard de ações
    keyboard = acoes_tarefa(tarefa_id, tarefa['autor_id'], user_id)

    # Se tem imagem, envia como caption
    if tarefa['imagem_file_id']:
        # Deletar mensagem anterior e enviar nova com foto
        chat_id = query.message.chat_id
        await query.message.delete()
        await query.get_bot().send_photo(
            chat_id=chat_id,
            photo=tarefa['imagem_file_id'],
            caption=texto,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    else:
        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=keyboard
        )


async def mudar_status(query, tarefa_id: int, novo_status: str):
    """Muda o status de uma tarefa"""
    db.atualizar_status(tarefa_id, novo_status)
    
    emoji = STATUS_EMOJI.get(novo_status, '📌')
    status_nome = novo_status.replace('_', ' ').title()
    await query.answer(f"{emoji} Status atualizado para: {status_nome}")
    
    # Atualiza a visualização
    await mostrar_tarefa(query, tarefa_id)


async def confirmar_delecao(query, tarefa_id: int):
    """Pede confirmação para deletar"""
    tarefa = db.obter_tarefa(tarefa_id)

    texto = f"⚠️ *Confirmar exclusão*\n\n"
    texto += f"Tem certeza que deseja deletar a tarefa:\n\n"
    texto += f"#{tarefa_id} - {tarefa['titulo']}\n\n"
    texto += "Esta ação não pode ser desfeita!"

    # Verificar se a mensagem tem foto
    if query.message.photo:
        chat_id = query.message.chat_id
        await query.message.delete()
        await query.get_bot().send_message(
            chat_id=chat_id,
            text=texto,
            parse_mode='Markdown',
            reply_markup=keyboard_confirmar_delecao(tarefa_id)
        )
    else:
        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=keyboard_confirmar_delecao(tarefa_id)
        )


async def deletar_tarefa(query, tarefa_id: int):
    """Deleta uma tarefa"""
    db.deletar_tarefa(tarefa_id)
    
    await query.edit_message_text(
        f"✅ Tarefa #{tarefa_id} deletada com sucesso!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📋 Ver tarefas", callback_data="voltar_lista")
        ]])
    )


async def mostrar_opcoes_edicao(query, tarefa_id: int):
    """Mostra opções de edição"""
    texto = f"✏️ *Editar Tarefa #{tarefa_id}*\n\n"
    texto += "Selecione o que deseja editar:"

    # Verificar se a mensagem tem foto
    if query.message.photo:
        chat_id = query.message.chat_id
        await query.message.delete()
        await query.get_bot().send_message(
            chat_id=chat_id,
            text=texto,
            parse_mode='Markdown',
            reply_markup=menu_edicao(tarefa_id)
        )
    else:
        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=menu_edicao(tarefa_id)
        )


async def mostrar_comentarios(query, tarefa_id: int):
    """Mostra comentários de uma tarefa"""
    comentarios = db.listar_comentarios(tarefa_id)

    texto = f"💬 *Comentários da Tarefa #{tarefa_id}*\n\n"

    if not comentarios:
        texto += "Nenhum comentário ainda.\n"
    else:
        for com in comentarios:
            data = datetime.fromisoformat(com['data'])
            texto += f"👤 *{com['autor_nome']}* - `{data.strftime('%d/%m %H:%M')}`\n"
            texto += f"{com['comentario']}\n\n"

    # Verificar se a mensagem tem foto (não tem texto para editar)
    if query.message.photo:
        # Se tem foto, deletar e enviar nova mensagem de texto
        chat_id = query.message.chat_id
        await query.message.delete()
        await query.get_bot().send_message(
            chat_id=chat_id,
            text=texto,
            parse_mode='Markdown',
            reply_markup=voltar_tarefa(tarefa_id)
        )
    else:
        # Se não tem foto, apenas editar o texto
        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=voltar_tarefa(tarefa_id)
        )


async def adicionar_comentario_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adiciona comentário via comando /comentar"""
    # Verificar tópico
    if not await verificar_topico(update):
        topico_id = db.obter_config('topico_permitido')
        await update.message.reply_text(
            f"⚠️ *Uso restrito*\n\n"
            f"Este bot só funciona no tópico configurado (ID: `{topico_id}`).\n"
            f"Por favor, use os comandos dentro do tópico apropriado.",
            parse_mode='Markdown'
        )
        return

    if len(context.args) < 2:
        await update.message.reply_text("Use: `/comentar [id_tarefa] [comentário]`\n\n*Exemplo:* `/comentar 1 Já comecei a trabalhar nisso!`", parse_mode='Markdown')
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


async def iniciar_adicionar_comentario(query, tarefa_id: int):
    """Mostra instruções para adicionar comentário"""
    texto = f"💬 *Adicionar Comentário à Tarefa #{tarefa_id}*\n\n"
    texto += "Para adicionar um comentário, use o comando:\n\n"
    texto += f"`/comentar {tarefa_id} Seu comentário aqui`\n\n"
    texto += "*Exemplo:*\n"
    texto += f"`/comentar {tarefa_id} Já comecei a trabalhar nisso!`\n\n"
    texto += "_Os comentários serão exibidos em ordem cronológica com seu nome e horário._"

    # Verificar se a mensagem tem foto
    if query.message.photo:
        chat_id = query.message.chat_id
        await query.message.delete()
        await query.get_bot().send_message(
            chat_id=chat_id,
            text=texto,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Voltar aos Comentários", callback_data=f"comentarios_{tarefa_id}")
            ]])
        )
    else:
        await query.edit_message_text(
            texto,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Voltar aos Comentários", callback_data=f"comentarios_{tarefa_id}")
            ]])
        )


async def voltar_lista(query):
    """Volta para a lista de tarefas com filtros"""
    tarefas = db.listar_tarefas()
    
    texto = "📋 *Tarefas do BigCommunity*\n\n"
    texto += "_Use os filtros abaixo para organizar:_\n\n"

    for status in STATUS:
        count = len([t for t in tarefas if t['status'] == status])
        emoji = STATUS_EMOJI.get(status, '📌')
        # Substituir underscore por espaço e capitalizar
        status_nome = status.replace('_', ' ').title()
        texto += f"{emoji} {status_nome}: `{count}`\n"

    await query.edit_message_text(
        texto,
        parse_mode='Markdown',
        reply_markup=keyboard_filtros()
    )


# ============ MAIN ============

def main():
    """Função principal"""
    # Carregar token do arquivo .env
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN não encontrado no arquivo .env")
        logger.error("Por favor, crie um arquivo .env com seu token do Telegram")
        logger.error("Exemplo: TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return

    # Criar aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Handlers de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ajuda", ajuda))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("changelog", lambda u, c: menu_changelog(u, is_command=True)))
    application.add_handler(CommandHandler("tarefas", listar_tarefas))
    application.add_handler(CommandHandler("minhas", minhas_tarefas))
    application.add_handler(CommandHandler("comentar", adicionar_comentario_cmd))
    application.add_handler(CommandHandler("topicoid", topicoid))
    application.add_handler(CommandHandler("settopico", settopico))
    
    # ConversationHandler para criar nova tarefa
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("nova", nova_tarefa)],
        states={
            TITULO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_titulo)],
            DESCRICAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)],
            CATEGORIA: [CallbackQueryHandler(receber_categoria)],
            PRIORIDADE: [CallbackQueryHandler(receber_prioridade)],
            IMAGEM: [
                MessageHandler(filters.PHOTO, receber_imagem),
                CallbackQueryHandler(pular_imagem, pattern="^pular_imagem$")
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )
    
    application.add_handler(conv_handler)

    # Handler de callbacks
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Handler para capturar mensagens de texto (edição inline e comentários)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_mensagem_texto))

    # Iniciar bot
    logger.info("Bot iniciado!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

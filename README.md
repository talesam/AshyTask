# 🤖 Bot de Gerenciamento de Tarefas - BigCommunity

Bot para Telegram desenvolvido para gerenciar tarefas do projeto BigCommunity (XFCE, Cinnamon, GNOME).

## 📋 Funcionalidades

- ✅ Criar tarefas com título, descrição, categoria e prioridade
- 🖼️ Suporte a imagens nas tarefas
- 🏷️ Categorias customizáveis (padrão: XFCE, Cinnamon, GNOME, Geral)
- 📊 Status de tarefas: Pendente, Em Andamento, Concluído
- 🎯 Prioridades: Alta, Média, Baixa
- 💬 Sistema de comentários
- 🔍 Busca de tarefas
- 👤 Controle de autoria (apenas o criador pode editar/deletar)
- 📱 Interface intuitiva com inline keyboards

## 🚀 Instalação

### 1. Pré-requisitos
- Python 3.8 ou superior
- Uma conta no Telegram

### 2. Criar o bot no Telegram
1. Abra o Telegram e fale com [@BotFather](https://t.me/BotFather)
2. Envie `/newbot`
3. Escolha um nome e username para seu bot
4. Copie o **token** fornecido

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (copie do `.env.example`):

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione seu token do Telegram:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

**⚠️ IMPORTANTE:** Nunca compartilhe seu arquivo `.env` ou faça commit dele no Git. Ele está no `.gitignore` para sua segurança.

### 5. Executar o bot

```bash
python bot.py
```

## 📱 Comandos

### Comandos Principais
- `/start` - Inicia o bot e mostra menu de ajuda
- `/tarefas` - Abre o menu principal de tarefas
- `/nova` - Cria uma nova tarefa (processo guiado)
- `/minhas` - Lista suas tarefas
- `/buscar [termo]` - Busca tarefas por palavra-chave

### Comandos Administrativos
- `/addcategoria [nome]` - Adiciona nova categoria
- `/comentar [id] [texto]` - Adiciona comentário a uma tarefa

### Comandos de Ajuda
- `/ajuda` - Mostra todos os comandos disponíveis
- `/cancelar` - Cancela operação em andamento

## 🎮 Como Usar

### Criar uma Nova Tarefa

1. Digite `/nova`
2. Escolha a categoria (XFCE, Cinnamon, GNOME, Geral)
3. Digite o título
4. Digite a descrição (ou `/pular`)
5. Escolha a prioridade (Alta, Média, Baixa)
6. Envie uma imagem (opcional, ou `/pular`)
7. Tarefa criada! ✅

### Gerenciar Tarefas

Use `/tarefas` para abrir o menu principal. Você pode:

- **Filtrar** por status (Pendentes, Em Andamento, Concluídas)
- **Filtrar** por categoria
- **Clicar** em uma tarefa para ver detalhes
- **Mudar status** usando os botões ⏳ 🔄 ✅
- **Editar** tarefa (apenas criador) ✏️
- **Deletar** tarefa (apenas criador) 🗑️
- **Ver comentários** 💬

### Status das Tarefas

- ⏳ **Pendente** - Tarefa criada, aguardando início
- 🔄 **Em Andamento** - Tarefa sendo trabalhada
- ✅ **Concluído** - Tarefa finalizada

### Prioridades

- 🔴 **Alta** - Urgente, requer atenção imediata
- 🟡 **Média** - Prioridade normal
- 🟢 **Baixa** - Pode aguardar

## 📁 Estrutura do Projeto

```
.
├── bot.py           # Arquivo principal
├── handlers.py      # Lógica dos comandos e callbacks
├── keyboards.py     # Layouts dos botões inline
├── database.py      # Gerenciamento do SQLite
├── requirements.txt # Dependências Python
└── tarefas_bot.db  # Banco de dados (criado automaticamente)
```

## 🗄️ Banco de Dados

O bot usa SQLite com 3 tabelas:

- **categorias** - Armazena as categorias (XFCE, Cinnamon, etc.)
- **tarefas** - Armazena todas as tarefas
- **comentarios** - Armazena comentários das tarefas

O banco é criado automaticamente na primeira execução.

## 🎨 Personalização

### Adicionar Novas Categorias

Pelo bot:
```
/addcategoria KDE
```

Ou edite `database.py` e adicione na lista `categorias_padrao`:
```python
categorias_padrao = ["XFCE", "Cinnamon", "GNOME", "KDE", "Geral"]
```

### Modificar Status Disponíveis

Edite `keyboards.py` no dicionário `STATUS_EMOJI`:
```python
STATUS_EMOJI = {
    "pendente": "⏳",
    "em_andamento": "🔄",
    "concluido": "✅",
    "bloqueado": "🚫"  # adicione novos status aqui
}
```

## 🔒 Segurança

- Apenas o criador da tarefa pode editá-la ou deletá-la
- Todos os membros do grupo podem ver e comentar
- Todos podem mudar o status das tarefas (colaborativo)

## 🐛 Troubleshooting

### Bot não responde
- Verifique se o token está correto
- Certifique-se que o bot está rodando (`python bot.py`)
- Verifique os logs no terminal

### Erro de permissão no grupo
- Adicione o bot ao grupo
- Dê permissão de admin ao bot (para apagar mensagens se necessário)

### Banco de dados corrompido
```bash
rm tarefas_bot.db
python bot.py  # Recria o banco
```

## 📝 Notas de Desenvolvimento

- Python-telegram-bot v20+ (API assíncrona)
- SQLite para persistência simples e portável
- Inline keyboards para UX fluida
- ConversationHandler para fluxos guiados
- Suporte completo a emojis

## 🤝 Contribuindo

Sinta-se livre para melhorar o bot! Algumas ideias:

- [ ] Exportar tarefas para CSV/JSON
- [ ] Relatórios estatísticos
- [ ] Notificações por menções
- [ ] Integração com GitHub Issues
- [ ] Lembretes automáticos
- [ ] Tags/labels adicionais

## 📜 Licença

Código livre para uso no projeto BigCommunity e derivados.

---

Desenvolvido com ❤️ para a comunidade BigCommunity

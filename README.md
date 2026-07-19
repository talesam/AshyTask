# 🤖 Ashy Task - Bot de Gerenciamento de Tarefas

Bot para Telegram desenvolvido para gerenciar tarefas de projetos (XFCE, Cinnamon, GNOME, etc.).

## 📋 Funcionalidades

- ✅ Criar tarefas com título, descrição, categoria e prioridade
- 🖼️ Suporte a imagens nas tarefas
- 🏷️ Categorias customizáveis (padrão: XFCE, Cinnamon, GNOME, Geral)
- 📊 Status de tarefas: Pendente, Em Andamento, Concluído
- 🎯 Prioridades: Alta, Média, Baixa
- 💬 Sistema de comentários
- 🔍 Busca de tarefas
- 👤 Controle de autoria (apenas o criador pode editar/deletar)
- 📝 Sistema de Changelog para documentar mudanças do projeto
- 📤 Exportação de changelog em HTML e PDF
- 🎨 Botões com estilos da Bot API 9.4+ (azul, verde, vermelho)
- 📌 Restrição a tópico específico (ideal para grupos com múltiplos tópicos)
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
- `/menu` - Abre menu de navegação completo
- `/stats` - Mostra estatísticas do projeto
- `/buscar [termo]` - Busca tarefas por palavra-chave
- `/comentar [id] [texto]` - Adiciona comentário a uma tarefa

### Comandos de Changelog
- `/changelog` - Abre menu de gerenciamento de changelogs
  - Criar novo changelog
  - Listar todos ou apenas pinados
  - Filtrar por categoria
  - Gerenciar categorias de changelog
  - Ver estatísticas
  - Exportar HTML/PDF

### Comandos de Tópico
- `/topicoid` - Mostra o ID do tópico atual
- `/settopico [ID]` - Configura o tópico permitido para o bot
- `/settopico off` - Desabilita restrição de tópico

### Comandos Administrativos
- `/categorias` - Lista e gerencia categorias de tarefas
- `/addcategoria [nome]` - Adiciona nova categoria de tarefa
- `/renomearcategoria [id] [novo_nome]` - Renomeia categoria de tarefa
- `/removercategoria [id]` - Remove categoria de tarefa e move tarefas para Geral
- `/deletetarefa [id]` - Remove qualquer tarefa (ADMIN_IDS)

### Comandos de Ajuda
- `/ajuda` - Mostra todos os comandos disponíveis
- `/cancelar` - Cancela operação em andamento

## 🎮 Como Usar

### Configurar Tópico (Opcional)

Para restringir o bot a funcionar apenas em um tópico específico:

1. Entre no tópico desejado no seu grupo Telegram
2. Digite `/topicoid` para ver o ID do tópico
3. Copie o ID mostrado (exemplo: `12345`)
4. Digite `/settopico 12345` para configurar
5. ✅ Agora o bot só responderá neste tópico!

Para desabilitar a restrição: `/settopico off`

### Criar uma Nova Tarefa

1. Digite `/nova`
2. Digite o título
3. Digite a descrição
4. Escolha a categoria (XFCE, Cinnamon, GNOME, Geral)
5. Escolha a prioridade (Alta, Média, Baixa)
6. Envie uma imagem (opcional, ou clique em Pular)
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
- **Gerenciar categorias** com `/categorias`

### Gerenciar Changelogs

Use `/changelog` para documentar mudanças do projeto:

- **Criar changelog** com categoria e descrição
- **Pinar changelogs** importantes para destaque
- **Filtrar** por categoria (Ashy Terminal, GNOME, XFCE, etc.)
- **Editar ou deletar** changelogs (apenas criador)
- **Ver estatísticas** de changelogs por categoria e autor
- **Exportar** changelogs em HTML ou PDF
- **Gerenciar categorias** pelo menu do changelog

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
├── handlers.py      # Compatibilidade antiga
├── keyboards.py     # Layouts dos botões inline
├── database.py      # Gerenciamento do SQLite
├── requirements.txt # Dependências Python
└── tarefas_bot.db  # Banco de dados (criado automaticamente)
```

## 🗄️ Banco de Dados

O bot usa SQLite com 6 tabelas:

- **categorias** - Armazena as categorias de tarefas (XFCE, Cinnamon, etc.)
- **tarefas** - Armazena todas as tarefas
- **comentarios** - Armazena comentários das tarefas
- **changelogs** - Armazena histórico de mudanças do projeto
- **categorias_changelog** - Categorias específicas para changelogs
- **configuracoes** - Configurações do bot (como ID do tópico permitido)

O banco é criado automaticamente na primeira execução.

## 🎨 Personalização

### Adicionar Novas Categorias

Pelo bot:
```
/addcategoria KDE
/categorias
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

### Botões coloridos e emojis customizados

A Bot API 9.4+ suporta `style` e `icon_custom_emoji_id` em botões. O bot envia esses campos via `api_kwargs`.

```env
TELEGRAM_BUTTON_STYLES=1
TELEGRAM_BUTTON_CUSTOM_EMOJI_IDS=success=ID,danger=ID,primary=ID
```

Os estilos disponíveis são `primary` (azul), `success` (verde) e `danger` (vermelho). Emojis customizados dependem das regras do Telegram para bots com suporte a custom emoji.

## 🔒 Segurança e Permissões

### Tarefas
- ✏️ Apenas o criador pode editar ou deletar
- 🛡️ Admins em `ADMIN_IDS` também podem editar/deletar
- 👥 Todos podem ver, comentar e mudar status (colaborativo)
- 🏷️ Se `ADMIN_IDS` estiver vazio, categorias ficam abertas para compatibilidade

### Changelogs
- ✏️ Apenas o criador pode editar ou deletar
- 🛡️ Admins em `ADMIN_IDS` também podem editar/deletar
- 📌 Todos podem pinar/despinar changelogs
- 👥 Todos podem visualizar

### Restrição de Tópico
- 🔒 Administrador pode restringir o bot a um tópico específico usando `/settopico`
- ⚠️ Quando configurado, o bot só responde no tópico definido
- 🔓 Use `/settopico off` para remover a restrição

## 🐛 Troubleshooting

### Bot não responde
- Verifique se o token está correto no arquivo `.env`
- Certifique-se que o bot está rodando (`python bot.py`)
- Verifique os logs no terminal
- **Se estiver em um grupo com tópicos:** Verifique se está no tópico correto com `/topicoid`

### Bot só responde em um tópico específico
- O bot foi configurado para funcionar apenas em um tópico
- Use `/topicoid` no tópico atual para ver o ID
- Use `/settopico off` para desabilitar a restrição (se tiver permissão)

### Erro de permissão no grupo
- Adicione o bot ao grupo
- Dê permissão de admin ao bot (para apagar mensagens se necessário)
- Em grupos com tópicos, certifique-se que o bot pode postar no tópico desejado

### Banco de dados corrompido
```bash
rm tarefas_bot.db
python bot.py  # Recria o banco
```

### Ver qual tópico está configurado
```bash
# O ID fica salvo no banco de dados
# Use o comando /topicoid dentro do tópico para ver o ID
# Use /settopico sem argumentos para ver as instruções
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

Código livre para uso em projetos open source.

---

Desenvolvido com ❤️ por @talesam

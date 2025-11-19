# 🚀 GUIA RÁPIDO DE USO

## Passo 1: Instalar dependências

```bash
pip install python-telegram-bot==20.7
```

## Passo 2: Criar o bot no Telegram

1. Abra o Telegram
2. Busque por `@BotFather`
3. Envie `/newbot`
4. Escolha um nome: `BigCommunity Tasks`
5. Escolha um username: `bigcommunity_tasks_bot` (ou outro disponível)
6. **COPIE O TOKEN** que o BotFather enviar

## Passo 3: Configurar o token

Edite o arquivo `bot.py` na linha onde está:

```python
TOKEN = "SEU_TOKEN_AQUI"
```

Substitua por seu token real:

```python
TOKEN = "7123456789:AAHdqTcvCH1vGEVBfXqQyFKd3yXUfY-abcd"
```

## Passo 4: Executar o bot

```bash
python3 bot.py
```

Você verá:
```
🤖 Bot iniciado! Aguardando mensagens...
```

## Passo 5: Testar no Telegram

1. Abra o Telegram
2. Busque pelo seu bot (pelo username que você escolheu)
3. Clique em START ou envie `/start`
4. Pronto! O bot está funcionando! 🎉

## Comandos para testar:

```
/start          - Ver menu de ajuda
/nova           - Criar sua primeira tarefa
/tarefas        - Ver todas as tarefas
/minhas         - Ver suas tarefas
/buscar teste   - Buscar tarefas
```

## Usar em um grupo:

1. Crie um grupo ou use um existente
2. Adicione o bot ao grupo (usando o @username dele)
3. Todos no grupo podem usar os comandos!

## Dica Pro:

Para parar o bot, pressione `Ctrl + C` no terminal.

---

## Estrutura de Arquivos

```
📁 seu_projeto/
  ├── bot.py              ⭐ Arquivo principal (configure o TOKEN aqui)
  ├── handlers.py         🎮 Lógica dos comandos
  ├── keyboards.py        ⌨️ Botões e menus
  ├── database.py         💾 Banco de dados
  ├── requirements.txt    📦 Dependências
  ├── README.md           📖 Documentação completa
  └── tarefas_bot.db     🗄️ Banco (criado automaticamente)
```

## Fluxo de Criação de Tarefa:

```
/nova
  ↓
📁 Escolhe categoria (XFCE, Cinnamon, GNOME, Geral)
  ↓
✍️ Digite o título
  ↓  
📝 Digite a descrição (ou /pular)
  ↓
🎯 Escolha prioridade (Alta, Média, Baixa)
  ↓
📸 Envie imagem (opcional, ou /pular)
  ↓
✅ Tarefa criada!
```

## Status da Tarefa:

⏳ **Pendente** → 🔄 **Em Andamento** → ✅ **Concluído**

Mude o status clicando nos botões ao visualizar a tarefa!

---

**Qualquer dúvida, consulte o README.md completo!**

# 🔒 Segurança

## Informações Sensíveis

Este projeto usa variáveis de ambiente para armazenar informações sensíveis como tokens de API.

### ⚠️ NUNCA faça commit de:

- ✗ Arquivo `.env` (contém o token do bot)
- ✗ Arquivo `tarefas_bot.db` (banco de dados com informações do projeto)
- ✗ Tokens ou credenciais em código-fonte
- ✗ Logs que possam conter informações sensíveis

### ✅ O que está protegido pelo `.gitignore`:

- `.env` e variações
- `*.db` e arquivos de banco de dados
- `__pycache__/` e arquivos compilados Python
- Logs e arquivos temporários
- Configurações de IDEs

### 🔐 Boas Práticas:

1. **Sempre use `.env.example`** como template
2. **Nunca compartilhe** seu arquivo `.env` 
3. **Gere um novo token** se acidentalmente expor o atual
4. **Revise** o `.gitignore` antes de fazer commit
5. **Use `.env` diferente** para desenvolvimento e produção

### 🚨 Se você expôs seu token acidentalmente:

1. Acesse [@BotFather](https://t.me/BotFather) no Telegram
2. Use `/mybots` → Selecione seu bot → API Token → Revoke Token
3. Gere um novo token
4. Atualize seu arquivo `.env` local
5. Se o token foi commitado no Git:
   - Revogue o token imediatamente
   - Faça um commit removendo o token
   - Considere limpar o histórico do Git se necessário

## 📝 Verificação antes de commits

Antes de fazer `git commit`, sempre verifique:

```bash
# Ver arquivos que serão commitados
git status

# Ver o conteúdo que será commitado
git diff --cached

# Verificar se .env não está sendo commitado
git status | grep .env
```

Se você vir o arquivo `.env` listado, **NÃO FAÇA COMMIT!**

## 🔍 Verificar se há informações sensíveis

```bash
# Procurar por possíveis tokens no código
grep -r "AAHY7sAyc31c6m0zCtV1fMEOcu20LxgJRiU" .
grep -r "TOKEN.*=" . --include="*.py"

# Ver o que está sendo rastreado pelo Git
git ls-files
```

---

**Lembre-se:** Segurança é responsabilidade de todos! 🛡️

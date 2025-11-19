# ✅ Checklist antes de fazer Push para o GitHub

## 🔍 Verificações de Segurança

Antes de fazer `git push`, verifique:

### 1. Arquivos Sensíveis Protegidos

```bash
# Verificar se .env NÃO aparece
git status | grep ".env"
# Resultado esperado: apenas .env.example ou nada

# Verificar se o banco de dados NÃO aparece
git status | grep ".db"
# Resultado esperado: nada

# Verificar se CLAUDE.md NÃO aparece
git status | grep "CLAUDE"
# Resultado esperado: nada
```

### 2. Procurar por Tokens no Código

```bash
# Procurar por padrões de token do Telegram
grep -r ":[A-Za-z0-9_-]\{35\}" . --exclude-dir=.git --include="*.py"
# Resultado esperado: apenas em bot.py usando os.getenv()

# Procurar por números de bot (primeiro parte do token)
grep -r "[0-9]\{10\}:" . --exclude-dir=.git --include="*.py"
# Resultado esperado: nada em hardcode
```

### 3. Revisar Arquivos que Serão Commitados

```bash
# Ver lista de arquivos
git status

# Ver conteúdo que será commitado
git diff --cached
```

## ✅ Arquivos que DEVEM estar listados:

- [x] `.gitignore`
- [x] `.env.example`
- [x] `README.md`
- [x] `SECURITY.md`
- [x] `GIT_STATUS.md`
- [x] `requirements.txt`
- [x] `setup.sh`
- [x] `bot.py`
- [x] `database.py`
- [x] `keyboards.py`
- [x] `handlers.py` (se existir)

## ❌ Arquivos que NÃO DEVEM estar listados:

- [ ] `.env` (⚠️ CRÍTICO - contém token)
- [ ] `tarefas_bot.db` (banco de dados local)
- [ ] `CLAUDE.md` (contexto do AI)
- [ ] `__pycache__/` (cache Python)
- [ ] `venv/` (ambiente virtual)
- [ ] `*.log` (arquivos de log)

## 🚀 Comandos Seguros para Primeiro Push

```bash
# 1. Inicializar repositório (se ainda não fez)
git init

# 2. Adicionar arquivos
git add .

# 3. VERIFICAR NOVAMENTE!
git status

# 4. Se tudo OK, fazer commit
git commit -m "Initial commit: Bot de gerenciamento de tarefas

- Sistema de tarefas com categorias e prioridades
- Sistema de changelog
- Comentários em tarefas
- Autenticação por tópico do Telegram
- Interface inline completa"

# 5. Criar repositório no GitHub (via web)

# 6. Adicionar remote
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git

# 7. Renomear branch para main
git branch -M main

# 8. Push
git push -u origin main
```

## 🆘 Se Você Acidentalmente Expôs o Token

### ⚠️ AÇÃO IMEDIATA:

1. **Revogar o token no @BotFather:**
   - Abra [@BotFather](https://t.me/BotFather)
   - `/mybots` → Seu bot → API Token → Revoke Token

2. **Gerar novo token:**
   - Ainda no BotFather → Generate New Token
   - Copiar o novo token

3. **Atualizar .env local:**
   ```bash
   nano .env
   # Colar o novo token
   ```

4. **Se já fez push com o token exposto:**
   ```bash
   # Remover do histórico (use com cuidado!)
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch bot.py' \
   --prune-empty --tag-name-filter cat -- --all
   
   # Fazer push forçado
   git push origin --force --all
   ```

## 📚 Recursos

- [Guia de Segurança](SECURITY.md)
- [Documentação](README.md)
- [Status do Git](GIT_STATUS.md)

---

**Lembre-se:** É melhor verificar 10 vezes do que expor dados sensíveis! 🔒

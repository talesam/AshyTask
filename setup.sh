#!/bin/bash

echo "🤖 Setup do Bot de Gerenciamento de Tarefas - BigCommunity"
echo "==========================================================="
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não está instalado!"
    echo "Por favor, instale Python 3.8 ou superior"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Criar ambiente virtual (opcional)
read -p "Deseja criar um ambiente virtual? (s/N): " criar_venv
if [[ $criar_venv =~ ^[Ss]$ ]]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Ambiente virtual criado e ativado"
    echo ""
fi

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt
echo "✅ Dependências instaladas"
echo ""

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Criando .env a partir do .env.example..."
    cp .env.example .env
    echo "✅ Arquivo .env criado"
    echo ""
    echo "⚠️  IMPORTANTE: Edite o arquivo .env e adicione seu token do Telegram!"
    echo "Para obter o token:"
    echo "  1. Acesse @BotFather no Telegram"
    echo "  2. Use /newbot para criar um novo bot"
    echo "  3. Copie o token fornecido"
    echo "  4. Edite o arquivo .env e cole o token"
    echo ""
    read -p "Deseja editar o .env agora? (s/N): " editar_env
    if [[ $editar_env =~ ^[Ss]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo "✅ Arquivo .env encontrado"
fi

echo ""
echo "🎉 Setup concluído!"
echo ""
echo "Para iniciar o bot:"
echo "  python bot.py"
echo ""
echo "Para ativar o ambiente virtual (se criado):"
echo "  source venv/bin/activate"
echo ""

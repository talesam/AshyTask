#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração única para converter tarefas concluídas em changelogs
Execute este script APENAS UMA VEZ após atualizar o bot para a versão 1.1.3
"""

from database import Database

def migrar_tarefas_concluidas():
    """Migra todas as tarefas concluídas para o changelog"""
    db = Database()

    # Buscar todas as tarefas concluídas
    tarefas = db.listar_tarefas(status='concluido')

    if not tarefas:
        print("✅ Nenhuma tarefa concluída encontrada para migrar.")
        return

    print(f"🔍 Encontradas {len(tarefas)} tarefas concluídas.")
    print("📝 Criando changelogs...\n")

    migradas = 0
    erros = 0

    for tarefa in tarefas:
        try:
            # Formatar descrição do changelog
            prioridade_emoji = {
                "alta": "🔴",
                "media": "🟡",
                "baixa": "🟢"
            }.get(tarefa.get('prioridade', 'media'), "⚪")

            changelog_descricao = f"✅ **{tarefa['titulo']}**\n\n"
            if tarefa.get('descricao'):
                changelog_descricao += f"📄 {tarefa['descricao']}\n\n"
            changelog_descricao += f"⚡ Prioridade: {prioridade_emoji} {tarefa.get('prioridade', 'media').capitalize()}"

            # Criar changelog
            categoria = tarefa.get('categoria') or "Geral"
            autor_id = tarefa.get('autor_id', 0)
            autor_nome = tarefa.get('autor_nome', 'Sistema')

            changelog_id = db.criar_changelog(
                categoria=categoria,
                descricao=changelog_descricao,
                autor_id=autor_id,
                autor_nome=autor_nome
            )

            print(f"✅ Tarefa #{tarefa['id']}: {tarefa['titulo'][:50]}... → Changelog #{changelog_id}")
            migradas += 1

        except Exception as e:
            print(f"❌ Erro ao migrar tarefa #{tarefa['id']}: {str(e)}")
            erros += 1

    print(f"\n{'='*60}")
    print(f"✅ Migração concluída!")
    print(f"📊 Changelogs criados: {migradas}")
    if erros > 0:
        print(f"⚠️  Erros: {erros}")
    print(f"{'='*60}")
    print("\n💡 Agora você pode visualizar os changelogs com o comando /changelog no bot!")

if __name__ == "__main__":
    print("="*60)
    print("🚀 Script de Migração - Tarefas Concluídas → Changelog")
    print("="*60)
    print("\n⚠️  ATENÇÃO: Execute este script apenas UMA VEZ!")
    print("    Tarefas concluídas serão convertidas em changelogs.\n")

    resposta = input("Deseja continuar? (s/n): ").strip().lower()

    if resposta in ['s', 'sim', 'y', 'yes']:
        print("\n🔄 Iniciando migração...\n")
        migrar_tarefas_concluidas()
    else:
        print("\n❌ Migração cancelada pelo usuário.")

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_name: str = "tarefas_bot.db"):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de categorias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        """)
        
        # Tabela de tarefas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                categoria_id INTEGER,
                autor_id INTEGER NOT NULL,
                autor_nome TEXT NOT NULL,
                atribuido_id INTEGER,
                atribuido_nome TEXT,
                status TEXT DEFAULT 'pendente',
                prioridade TEXT DEFAULT 'media',
                imagem_file_id TEXT,
                data_criacao TEXT NOT NULL,
                data_conclusao TEXT,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            )
        """)
        
        # Tabela de comentários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarefa_id INTEGER NOT NULL,
                autor_id INTEGER NOT NULL,
                autor_nome TEXT NOT NULL,
                comentario TEXT NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE
            )
        """)

        # Tabela de changelogs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS changelogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT NOT NULL,
                descricao TEXT NOT NULL,
                autor_id INTEGER NOT NULL,
                autor_nome TEXT NOT NULL,
                data_criacao TEXT NOT NULL,
                pinado INTEGER DEFAULT 0
            )
        """)

        # Tabela de categorias de changelog
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias_changelog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        """)

        # Tabela de configurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        """)

        # Inserir categorias padrão de tarefas
        categorias_padrao = ["XFCE", "Cinnamon", "GNOME", "Geral"]
        for cat in categorias_padrao:
            cursor.execute("INSERT OR IGNORE INTO categorias (nome) VALUES (?)", (cat,))

        # Inserir categorias padrão de changelog
        categorias_changelog_padrao = ["Ashy Terminal", "GNOME", "XFCE", "Cinnamon", "All", "Geral"]
        for cat in categorias_changelog_padrao:
            cursor.execute("INSERT OR IGNORE INTO categorias_changelog (nome) VALUES (?)", (cat,))

        conn.commit()
        conn.close()
    
    def adicionar_categoria(self, nome: str) -> bool:
        """Adiciona nova categoria"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def listar_categorias(self) -> List[Dict]:
        """Lista todas as categorias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM categorias ORDER BY nome")
        categorias = [{"id": row[0], "nome": row[1]} for row in cursor.fetchall()]
        conn.close()
        return categorias
    
    def criar_tarefa(self, titulo: str, descricao: str, categoria_id: int, 
                     autor_id: int, autor_nome: str, prioridade: str = "media",
                     imagem_file_id: Optional[str] = None) -> int:
        """Cria uma nova tarefa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO tarefas (titulo, descricao, categoria_id, autor_id, autor_nome,
                               prioridade, imagem_file_id, data_criacao, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendente')
        """, (titulo, descricao, categoria_id, autor_id, autor_nome, prioridade, 
              imagem_file_id, data_criacao))
        
        tarefa_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tarefa_id
    
    def listar_tarefas(self, categoria_id: Optional[int] = None, 
                       status: Optional[str] = None,
                       autor_id: Optional[int] = None) -> List[Dict]:
        """Lista tarefas com filtros opcionais"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT t.id, t.titulo, t.descricao, c.nome as categoria, t.autor_nome,
                   t.atribuido_nome, t.status, t.prioridade, t.data_criacao,
                   t.imagem_file_id
            FROM tarefas t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE 1=1
        """
        params = []
        
        if categoria_id:
            query += " AND t.categoria_id = ?"
            params.append(categoria_id)
        
        if status:
            query += " AND t.status = ?"
            params.append(status)
        
        if autor_id:
            query += " AND t.autor_id = ?"
            params.append(autor_id)
        
        query += " ORDER BY t.id DESC"
        
        cursor.execute(query, params)
        tarefas = []
        for row in cursor.fetchall():
            tarefas.append({
                "id": row[0],
                "titulo": row[1],
                "descricao": row[2],
                "categoria": row[3],
                "autor_nome": row[4],
                "atribuido_nome": row[5],
                "status": row[6],
                "prioridade": row[7],
                "data_criacao": row[8],
                "imagem_file_id": row[9]
            })
        
        conn.close()
        return tarefas
    
    def obter_tarefa(self, tarefa_id: int) -> Optional[Dict]:
        """Obtém uma tarefa específica"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.titulo, t.descricao, c.nome as categoria, t.autor_nome,
                   t.atribuido_nome, t.status, t.prioridade, t.data_criacao,
                   t.data_conclusao, t.imagem_file_id, t.autor_id
            FROM tarefas t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE t.id = ?
        """, (tarefa_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "titulo": row[1],
                "descricao": row[2],
                "categoria": row[3],
                "autor_nome": row[4],
                "atribuido_nome": row[5],
                "status": row[6],
                "prioridade": row[7],
                "data_criacao": row[8],
                "data_conclusao": row[9],
                "imagem_file_id": row[10],
                "autor_id": row[11]
            }
        return None
    
    def atualizar_status(self, tarefa_id: int, status: str) -> bool:
        """Atualiza o status de uma tarefa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        data_conclusao = None
        if status == "concluido":
            data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE tarefas 
            SET status = ?, data_conclusao = ?
            WHERE id = ?
        """, (status, data_conclusao, tarefa_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def atualizar_tarefa(self, tarefa_id: int, titulo: Optional[str] = None,
                        descricao: Optional[str] = None, 
                        prioridade: Optional[str] = None) -> bool:
        """Atualiza informações de uma tarefa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if titulo:
            updates.append("titulo = ?")
            params.append(titulo)
        if descricao:
            updates.append("descricao = ?")
            params.append(descricao)
        if prioridade:
            updates.append("prioridade = ?")
            params.append(prioridade)
        
        if not updates:
            return False
        
        params.append(tarefa_id)
        query = f"UPDATE tarefas SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def deletar_tarefa(self, tarefa_id: int) -> bool:
        """Deleta uma tarefa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def adicionar_comentario(self, tarefa_id: int, autor_id: int, 
                           autor_nome: str, comentario: str) -> bool:
        """Adiciona comentário a uma tarefa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO comentarios (tarefa_id, autor_id, autor_nome, comentario, data)
            VALUES (?, ?, ?, ?, ?)
        """, (tarefa_id, autor_id, autor_nome, comentario, data))
        
        conn.commit()
        conn.close()
        return True
    
    def listar_comentarios(self, tarefa_id: int) -> List[Dict]:
        """Lista comentários de uma tarefa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT autor_nome, comentario, data
            FROM comentarios
            WHERE tarefa_id = ?
            ORDER BY data ASC
        """, (tarefa_id,))
        
        comentarios = []
        for row in cursor.fetchall():
            comentarios.append({
                "autor_nome": row[0],
                "comentario": row[1],
                "data": row[2]
            })
        
        conn.close()
        return comentarios
    
    def buscar_tarefas(self, termo: str) -> List[Dict]:
        """Busca tarefas por termo no título ou descrição"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.titulo, t.descricao, c.nome as categoria, t.autor_nome,
                   t.status, t.prioridade
            FROM tarefas t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE t.titulo LIKE ? OR t.descricao LIKE ?
            ORDER BY t.id DESC
        """, (f"%{termo}%", f"%{termo}%"))
        
        tarefas = []
        for row in cursor.fetchall():
            tarefas.append({
                "id": row[0],
                "titulo": row[1],
                "descricao": row[2],
                "categoria": row[3],
                "autor_nome": row[4],
                "status": row[5],
                "prioridade": row[6]
            })

        conn.close()
        return tarefas

    def estatisticas(self) -> Dict:
        """Retorna estatísticas gerais das tarefas"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Total de tarefas
        cursor.execute("SELECT COUNT(*) FROM tarefas")
        total = cursor.fetchone()[0]

        # Tarefas por status
        cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'pendente'")
        pendentes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'em_andamento'")
        em_andamento = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'concluido'")
        resolvidas = cursor.fetchone()[0]

        conn.close()

        return {
            'total': total,
            'pendentes': pendentes,
            'em_andamento': em_andamento,
            'resolvidas': resolvidas
        }

    # ============ CONFIGURAÇÕES ============

    def obter_config(self, chave: str) -> Optional[str]:
        """Obtém uma configuração"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def salvar_config(self, chave: str, valor: str):
        """Salva ou atualiza uma configuração"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", (chave, valor))
        conn.commit()
        conn.close()

    # ============ CHANGELOGS ============

    def listar_categorias_changelog(self) -> List[str]:
        """Lista todas as categorias de changelog"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM categorias_changelog ORDER BY nome")
        categorias = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categorias

    def adicionar_categoria_changelog(self, nome: str) -> bool:
        """Adiciona nova categoria de changelog"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categorias_changelog (nome) VALUES (?)", (nome,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def criar_changelog(self, categoria: str, descricao: str, autor_id: int, autor_nome: str) -> int:
        """Cria um novo changelog"""
        conn = self.get_connection()
        cursor = conn.cursor()
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO changelogs (categoria, descricao, autor_id, autor_nome, data_criacao, pinado)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (categoria, descricao, autor_id, autor_nome, data_criacao))

        changelog_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return changelog_id

    def listar_changelogs(self, categoria: Optional[str] = None, pinado: Optional[bool] = None) -> List[Dict]:
        """Lista changelogs com filtros opcionais"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT id, categoria, descricao, autor_id, autor_nome, data_criacao, pinado FROM changelogs WHERE 1=1"
        params = []

        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)

        if pinado is not None:
            query += " AND pinado = ?"
            params.append(1 if pinado else 0)

        query += " ORDER BY pinado DESC, data_criacao DESC"

        cursor.execute(query, params)
        changelogs = []
        for row in cursor.fetchall():
            changelogs.append({
                'id': row[0],
                'categoria': row[1],
                'descricao': row[2],
                'autor_id': row[3],
                'autor_nome': row[4],
                'data_criacao': row[5],
                'pinado': row[6]
            })

        conn.close()
        return changelogs

    def obter_changelog(self, changelog_id: int) -> Optional[Dict]:
        """Obtém um changelog específico"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, categoria, descricao, autor_id, autor_nome, data_criacao, pinado
            FROM changelogs WHERE id = ?
        """, (changelog_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'categoria': row[1],
                'descricao': row[2],
                'autor_id': row[3],
                'autor_nome': row[4],
                'data_criacao': row[5],
                'pinado': row[6]
            }
        return None

    def alternar_pinagem_changelog(self, changelog_id: int) -> bool:
        """Alterna o estado de pinagem de um changelog"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Obter estado atual
        cursor.execute("SELECT pinado FROM changelogs WHERE id = ?", (changelog_id,))
        row = cursor.fetchone()

        if row is None:
            conn.close()
            return False

        novo_estado = 0 if row[0] == 1 else 1

        cursor.execute("UPDATE changelogs SET pinado = ? WHERE id = ?", (novo_estado, changelog_id))
        conn.commit()
        conn.close()
        return True

    def deletar_changelog(self, changelog_id: int) -> bool:
        """Deleta um changelog"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM changelogs WHERE id = ?", (changelog_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def atualizar_changelog(self, changelog_id: int, descricao: Optional[str] = None, categoria: Optional[str] = None) -> bool:
        """Atualiza um changelog"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if descricao is not None:
            updates.append("descricao = ?")
            params.append(descricao)

        if categoria is not None:
            updates.append("categoria = ?")
            params.append(categoria)

        if not updates:
            conn.close()
            return False

        params.append(changelog_id)
        query = f"UPDATE changelogs SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(query, params)
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    def estatisticas_changelog(self) -> Dict:
        """Retorna estatísticas dos changelogs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Total geral
        cursor.execute("SELECT COUNT(*) FROM changelogs")
        total = cursor.fetchone()[0]

        # Total pinados
        cursor.execute("SELECT COUNT(*) FROM changelogs WHERE pinado = 1")
        pinados = cursor.fetchone()[0]

        # Por categoria
        cursor.execute("""
            SELECT categoria, COUNT(*) as total
            FROM changelogs
            GROUP BY categoria
            ORDER BY total DESC
        """)
        por_categoria = {row[0]: row[1] for row in cursor.fetchall()}

        # Por autor
        cursor.execute("""
            SELECT autor_nome, COUNT(*) as total
            FROM changelogs
            GROUP BY autor_nome
            ORDER BY total DESC
        """)
        por_autor = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            'total': total,
            'pinados': pinados,
            'por_categoria': por_categoria,
            'por_autor': por_autor
        }

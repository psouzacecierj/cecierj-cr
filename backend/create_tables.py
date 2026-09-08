import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from supabase_client import supabase

# SQL para criar as tabelas
SQL_TABLES = """
-- Tabela: candidatos
CREATE TABLE IF NOT EXISTS candidatos (
    id SERIAL PRIMARY KEY,
    nome_completo TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    data_nascimento DATE,
    email TEXT,
    telefone TEXT,
    endereco TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: editais
CREATE TABLE IF NOT EXISTS editais (
    id SERIAL PRIMARY KEY,
    numero TEXT UNIQUE NOT NULL,
    ano INTEGER,
    semestre TEXT,
    data_publicacao DATE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: cursos
CREATE TABLE IF NOT EXISTS cursos (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    codigo TEXT UNIQUE NOT NULL,
    modalidade TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: disciplinas
CREATE TABLE IF NOT EXISTS disciplinas (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    codigo TEXT UNIQUE NOT NULL,
    curso_id INTEGER REFERENCES cursos(id),
    vagas INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: inscricoes
CREATE TABLE IF NOT EXISTS inscricoes (
    id SERIAL PRIMARY KEY,
    candidato_id INTEGER REFERENCES candidatos(id),
    edital_id INTEGER REFERENCES editais(id),
    disciplina_id INTEGER REFERENCES disciplinas(id),
    status TEXT DEFAULT 'pendente',
    opta_cotas BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
"""

try:
    print("🔨 Criando tabelas no Supabase...")
    result = supabase.rpc('exec_sql', {'sql': SQL_TABLES}).execute()
    print("✅ Tabelas criadas com sucesso!")
    
    # Listar tabelas criadas
    print("\n📋 Tabelas criadas:")
    response = supabase.table('information_schema.tables') \
        .select('table_name') \
        .eq('table_schema', 'public') \
        .execute()
    
    tables = [t['table_name'] for t in response.data if t['table_name'] not in ['test_connection']]
    for table in tables:
        print(f"   - {table}")
    
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
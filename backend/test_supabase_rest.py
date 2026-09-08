import os
import sys
from pathlib import Path

# Adicionar o caminho do projeto
sys.path.insert(0, str(Path(__file__).parent))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from supabase_client import supabase

print("🔍 Testando conexão com Supabase via REST...")
print(f"📊 URL: {os.getenv('SUPABASE_URL')}")

if supabase is None:
    print("❌ Cliente Supabase não inicializado. Verifique as credenciais.")
    sys.exit(1)

try:
    # Teste 1: Tentar listar tabelas existentes
    print("\n📋 Listando tabelas existentes...")
    response = supabase.table('information_schema.tables') \
        .select('table_name') \
        .eq('table_schema', 'public') \
        .limit(10) \
        .execute()
    
    if response.data:
        print("✅ Tabelas encontradas:")
        for table in response.data:
            print(f"   - {table['table_name']}")
    else:
        print("ℹ️ Nenhuma tabela encontrada (banco vazio)")
    
    # Teste 2: Criar uma tabela de teste
    print("\n📝 Criando tabela de teste...")
    
    # Primeiro, verificar se a tabela já existe
    response = supabase.table('information_schema.tables') \
        .select('table_name') \
        .eq('table_schema', 'public') \
        .eq('table_name', 'test_connection') \
        .execute()
    
    if not response.data:
        # Criar a tabela
        sql = """
        CREATE TABLE IF NOT EXISTS test_connection (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW(),
            message TEXT
        );
        """
        response = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ Tabela de teste criada com sucesso!")
    else:
        print("ℹ️ Tabela de teste já existe")
    
    # Teste 3: Inserir dados
    print("\n📝 Inserindo dados de teste...")
    data = {'message': 'Teste de conexão Supabase REST - Funcionando!'}
    response = supabase.table('test_connection').insert(data).execute()
    print("✅ Dados inseridos com sucesso!")
    
    # Teste 4: Buscar dados
    print("\n📝 Buscando dados...")
    response = supabase.table('test_connection').select('*').execute()
    print(f"📋 Dados salvos: {response.data}")
    
    print("\n🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
    print("✅ Conexão com Supabase via REST estabelecida com SUCESSO!")
    
except Exception as e:
    print(f"\n❌ Erro ao testar Supabase REST: {e}")
    print("\nVerifique:")
    print("1. Se SUPABASE_URL está correto")
    print("2. Se SUPABASE_KEY está correto")
    print("3. Se o projeto está ativo no Supabase")
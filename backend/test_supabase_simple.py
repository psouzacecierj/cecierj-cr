import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from supabase_client import supabase

print("🔍 Testando conexão com Supabase via REST...")
print(f"📊 URL: {os.getenv('SUPABASE_URL')}")

if supabase is None:
    print("❌ Cliente Supabase não inicializado.")
    sys.exit(1)

try:
    # Testar inserção na tabela candidatos
    print("\n📝 Inserindo candidato de teste...")
    data = {
        'nome_completo': 'Teste Supabase',
        'cpf': '12345678901',
        'email': 'teste@supabase.com',
        'telefone': '(11) 99999-9999'
    }
    response = supabase.table('candidatos').insert(data).execute()
    print("✅ Candidato inserido com sucesso!")
    print(f"📋 Dados: {response.data}")
    
    # Testar consulta
    print("\n📋 Buscando candidatos...")
    response = supabase.table('candidatos').select('*').execute()
    print(f"📋 Total de candidatos: {len(response.data)}")
    for item in response.data[:3]:
        print(f"   - {item['nome_completo']} ({item['cpf']})")
    
    print("\n🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
    print("✅ Conexão com Supabase via REST estabelecida com SUCESSO!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
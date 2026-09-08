import os
import django
from django.conf import settings

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

print("🔍 Testando conexão com Supabase...")
print(f"📊 Host: {settings.DATABASES['default']['HOST']}")
print(f"👤 User: {settings.DATABASES['default']['USER']}")
print(f"🗄️  Database: {settings.DATABASES['default']['NAME']}")

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print("\n✅ CONEXÃO COM SUPABASE ESTABELECIDA COM SUCESSO!")
        print(f"📦 Versão do PostgreSQL: {result[0][:50]}...")
        
        # Testar se o banco está funcionando
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"🗄️  Banco atual: {db_name[0]}")
        
        # Listar tabelas existentes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        if tables:
            print(f"\n📋 Tabelas existentes: {len(tables)}")
            for table in tables[:5]:  # Mostra as primeiras 5
                print(f"   - {table[0]}")
        else:
            print("\n📋 Nenhuma tabela encontrada (banco vazio)")
        
except Exception as e:
    print(f"\n❌ Erro ao conectar: {e}")
    print("\nVerifique:")
    print("1. Se a senha no .env está correta")
    print("2. Se o projeto no Supabase está ativo")
    print("3. Se o IPv4 add-on está habilitado (se necessário)")
from supabase import create_client
from django.conf import settings

# Inicializar o cliente Supabase
try:
    supabase = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )
    print("✅ Cliente Supabase inicializado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao inicializar cliente Supabase: {e}")
    supabase = None
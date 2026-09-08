from supabase_client import supabase
from typing import Dict, List, Optional, Any

class SupabaseSync:
    """Serviço para sincronizar dados com o Supabase"""
    
    @staticmethod
    def get_all(table_name: str) -> List[Dict]:
        """Busca todos os registros de uma tabela"""
        try:
            response = supabase.table(table_name).select('*').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Erro ao buscar dados de {table_name}: {e}")
            return []
    
    @staticmethod
    def get_by_id(table_name: str, id: int) -> Optional[Dict]:
        """Busca um registro por ID"""
        try:
            response = supabase.table(table_name).select('*').eq('id', id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao buscar registro {id} em {table_name}: {e}")
            return None
    
    @staticmethod
    def insert(table_name: str, data: Dict) -> Optional[Dict]:
        """Insere um novo registro"""
        try:
            response = supabase.table(table_name).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao inserir em {table_name}: {e}")
            return None
    
    @staticmethod
    def update(table_name: str, id: int, data: Dict) -> Optional[Dict]:
        """Atualiza um registro"""
        try:
            response = supabase.table(table_name).update(data).eq('id', id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao atualizar registro {id} em {table_name}: {e}")
            return None
    
    @staticmethod
    def delete(table_name: str, id: int) -> bool:
        """Remove um registro"""
        try:
            response = supabase.table(table_name).delete().eq('id', id).execute()
            return True
        except Exception as e:
            print(f"Erro ao deletar registro {id} de {table_name}: {e}")
            return False
    
    @staticmethod
    def filter(table_name: str, **filters) -> List[Dict]:
        """Busca registros com filtros"""
        try:
            query = supabase.table(table_name).select('*')
            for key, value in filters.items():
                query = query.eq(key, value)
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Erro ao filtrar em {table_name}: {e}")
            return []
from supabase_client import supabase
from typing import Dict, List, Optional, Any

class SupabaseService:
    """Serviço para interagir com o Supabase"""
    
    @staticmethod
    def get_table(table_name: str):
        """Retorna uma referência para uma tabela"""
        if supabase is None:
            raise Exception("Cliente Supabase não inicializado")
        return supabase.table(table_name)
    
    @staticmethod
    def insert(table_name: str, data: Dict):
        """Insere dados em uma tabela"""
        return supabase.table(table_name).insert(data).execute()
    
    @staticmethod
    def select(table_name: str, columns: str = '*', filters: Optional[Dict] = None):
        """Seleciona dados de uma tabela"""
        query = supabase.table(table_name).select(columns)
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        return query.execute()
    
    @staticmethod
    def update(table_name: str, data: Dict, filters: Dict):
        """Atualiza dados em uma tabela"""
        query = supabase.table(table_name).update(data)
        for key, value in filters.items():
            query = query.eq(key, value)
        return query.execute()
    
    @staticmethod
    def delete(table_name: str, filters: Dict):
        """Deleta dados de uma tabela"""
        query = supabase.table(table_name).delete()
        for key, value in filters.items():
            query = query.eq(key, value)
        return query.execute()
    
    @staticmethod
    def execute_sql(sql: str):
        """Executa SQL diretamente no Supabase"""
        return supabase.rpc('exec_sql', {'sql': sql}).execute()
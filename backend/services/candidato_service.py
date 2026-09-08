from services.supabase_sync import SupabaseSync
from typing import Dict, List, Optional

class CandidatoService:
    """Serviço para gerenciar candidatos no Supabase"""
    
    TABLE = 'candidatos'
    
    @classmethod
    def listar_todos(cls) -> List[Dict]:
        """Lista todos os candidatos"""
        return SupabaseSync.get_all(cls.TABLE)
    
    @classmethod
    def buscar_por_id(cls, id: int) -> Optional[Dict]:
        """Busca candidato por ID"""
        return SupabaseSync.get_by_id(cls.TABLE, id)
    
    @classmethod
    def buscar_por_cpf(cls, cpf: str) -> Optional[Dict]:
        """Busca candidato por CPF"""
        resultados = SupabaseSync.filter(cls.TABLE, cpf=cpf)
        return resultados[0] if resultados else None
    
    @classmethod
    def criar(cls, dados: Dict) -> Optional[Dict]:
        """Cria um novo candidato"""
        return SupabaseSync.insert(cls.TABLE, dados)
    
    @classmethod
    def atualizar(cls, id: int, dados: Dict) -> Optional[Dict]:
        """Atualiza um candidato"""
        return SupabaseSync.update(cls.TABLE, id, dados)
    
    @classmethod
    def deletar(cls, id: int) -> bool:
        """Deleta um candidato"""
        return SupabaseSync.delete(cls.TABLE, id)
    
    @classmethod
    def buscar_por_email(cls, email: str) -> List[Dict]:
        """Busca candidatos por email"""
        return SupabaseSync.filter(cls.TABLE, email=email)
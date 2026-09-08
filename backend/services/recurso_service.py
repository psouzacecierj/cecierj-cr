from services.supabase_sync import SupabaseSync
from typing import Dict, List, Optional

class RecursoService:
    """Serviço para gerenciar recursos"""
    
    TABLE = 'recursos'
    
    @classmethod
    def listar_por_inscricao(cls, inscricao_id: int) -> List[Dict]:
        """Lista recursos de uma inscrição"""
        return SupabaseSync.filter(cls.TABLE, inscricao_id=inscricao_id)
    
    @classmethod
    def criar(cls, dados: Dict) -> Optional[Dict]:
        """Cria um novo recurso"""
        return SupabaseSync.insert(cls.TABLE, dados)
    
    @classmethod
    def aprovar(cls, id: int, parecer: str) -> Optional[Dict]:
        """Aprova um recurso"""
        return SupabaseSync.update(cls.TABLE, id, {
            'status': 'deferido',
            'parecer': parecer
        })
    
    @classmethod
    def reprovar(cls, id: int, parecer: str) -> Optional[Dict]:
        """Reprova um recurso"""
        return SupabaseSync.update(cls.TABLE, id, {
            'status': 'indeferido',
            'parecer': parecer
        })
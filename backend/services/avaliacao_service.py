from services.supabase_sync import SupabaseSync
from typing import Dict, List, Optional

class AvaliacaoService:
    """Serviço para gerenciar avaliações no Supabase"""
    
    TABLE = 'avaliacoes'
    
    @classmethod
    def listar_por_inscricao(cls, inscricao_id: int) -> List[Dict]:
        """Lista avaliações de uma inscrição"""
        return SupabaseSync.filter(cls.TABLE, inscricao_id=inscricao_id)
    
    @classmethod
    def criar(cls, dados: Dict) -> Optional[Dict]:
        """Cria uma nova avaliação"""
        # Calcular nota final
        if 'nota_ac' in dados and 'nota_pp' in dados:
            peso_ac = 0.6
            peso_pp = 0.4
            dados['nota_final'] = (dados['nota_ac'] * peso_ac) + (dados['nota_pp'] * peso_pp)
        
        return SupabaseSync.insert(cls.TABLE, dados)
    
    @classmethod
    def atualizar(cls, id: int, dados: Dict) -> Optional[Dict]:
        """Atualiza uma avaliação"""
        if 'nota_ac' in dados and 'nota_pp' in dados:
            peso_ac = 0.6
            peso_pp = 0.4
            dados['nota_final'] = (dados['nota_ac'] * peso_ac) + (dados['nota_pp'] * peso_pp)
        
        return SupabaseSync.update(cls.TABLE, id, dados)
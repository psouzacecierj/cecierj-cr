from supabase_client import supabase
from typing import Dict, List, Optional

class AvaliacaoService:
    """Serviço para gerenciar avaliações"""
    
    TABLE = 'avaliacoes'
    
    @classmethod
    def listar_por_inscricao(cls, inscricao_id: int) -> Optional[Dict]:
        """Busca avaliação por inscrição"""
        try:
            response = supabase.table(cls.TABLE)\
                .select('*')\
                .eq('inscricao_id', inscricao_id)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    @classmethod
    def criar_ou_atualizar(cls, inscricao_id: int, nota_ac: float, nota_pp: float) -> Optional[Dict]:
        """Cria ou atualiza uma avaliação"""
        try:
            nota_final = (nota_ac * 0.6) + (nota_pp * 0.4)
            
            existente = cls.listar_por_inscricao(inscricao_id)
            
            dados = {
                'inscricao_id': inscricao_id,
                'nota_ac': nota_ac,
                'nota_pp': nota_pp,
                'nota_final': round(nota_final, 2)
            }
            
            if existente:
                response = supabase.table(cls.TABLE)\
                    .update(dados)\
                    .eq('id', existente['id'])\
                    .execute()
            else:
                response = supabase.table(cls.TABLE)\
                    .insert(dados)\
                    .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    @classmethod
    def listar_por_disciplina(cls, disciplina_id: int) -> List[Dict]:
        """Lista avaliações de uma disciplina"""
        try:
            # Buscar inscrições da disciplina
            response = supabase.table('inscricoes')\
                .select('*')\
                .eq('disciplina_id', disciplina_id)\
                .execute()
            
            if not response.data:
                return []
            
            resultado = []
            for inscricao in response.data:
                # Buscar candidato
                cand = supabase.table('candidatos')\
                    .select('nome_completo, cpf')\
                    .eq('id', inscricao['candidato_id'])\
                    .execute()
                
                # Buscar avaliação
                aval = supabase.table('avaliacoes')\
                    .select('*')\
                    .eq('inscricao_id', inscricao['id'])\
                    .execute()
                
                resultado.append({
                    'inscricao_id': inscricao['id'],
                    'candidato': cand.data[0] if cand.data else None,
                    'avaliacao': aval.data[0] if aval.data else None
                })
            
            return resultado
        except Exception as e:
            print(f"❌ Erro: {e}")
            return []
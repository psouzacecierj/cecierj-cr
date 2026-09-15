from supabase_client import supabase
from typing import Dict, List, Optional


class AvaliacaoService:
    """Serviço para gerenciar avaliações"""
    
    TABLE = 'avaliacoes'
    
    @classmethod
    def listar_por_inscricao(cls, inscricao_id: int) -> Optional[Dict]:
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
        try:
            response = supabase.table('inscricoes')\
                .select('*')\
                .eq('disciplina_id', disciplina_id)\
                .execute()
            
            if not response.data:
                return []
            
            resultado = []
            for inscricao in response.data:
                cand = supabase.table('candidatos')\
                    .select('nome_completo, cpf')\
                    .eq('id', inscricao['candidato_id'])\
                    .execute()
                
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
    
    @classmethod
    def classificar_disciplina(cls, disciplina_id: int) -> List[Dict]:
        """Classifica os candidatos de uma disciplina"""
        try:
            response = supabase.table('inscricoes')\
                .select('*')\
                .eq('disciplina_id', disciplina_id)\
                .execute()
            
            if not response.data:
                return []
            
            resultados = []
            for inscricao in response.data:
                aval = supabase.table('avaliacoes')\
                    .select('*')\
                    .eq('inscricao_id', inscricao['id'])\
                    .execute()
                
                if not aval.data:
                    continue
                
                avaliacao = aval.data[0]
                
                cand = supabase.table('candidatos')\
                    .select('nome_completo, cpf')\
                    .eq('id', inscricao['candidato_id'])\
                    .execute()
                
                if not cand.data:
                    continue
                
                candidato = cand.data[0]
                
                aprovado = avaliacao['nota_pp'] >= 24 and avaliacao['nota_final'] >= 60
                
                resultados.append({
                    'inscricao_id': inscricao['id'],
                    'avaliacao_id': avaliacao['id'],
                    'nome_completo': candidato['nome_completo'],
                    'cpf': candidato['cpf'],
                    'nota_ac': avaliacao['nota_ac'],
                    'nota_pp': avaliacao['nota_pp'],
                    'nota_final': avaliacao['nota_final'],
                    'status': 'APROVADO' if aprovado else 'NÃO APROVADO'
                })
            
            resultados.sort(key=lambda x: x['nota_final'], reverse=True)
            
            for i, resultado in enumerate(resultados, 1):
                resultado['classificacao'] = i
            
            return resultados
        except Exception as e:
            print(f"❌ Erro: {e}")
            return []
    
    @classmethod
    def salvar_classificacao(cls, disciplina_id: int) -> bool:
        """Salva a classificação no banco"""
        try:
            resultados = cls.classificar_disciplina(disciplina_id)
            
            for resultado in resultados:
                supabase.table('avaliacoes')\
                    .update({
                        'classificacao': resultado['classificacao'],
                        'parecer': resultado['status']
                    })\
                    .eq('id', resultado['avaliacao_id'])\
                    .execute()
            
            return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
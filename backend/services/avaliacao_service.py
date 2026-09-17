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
    @classmethod
    def processar_todas_disciplinas(cls) -> Dict:
        """Processa todas as disciplinas que têm avaliações"""
        try:
            # Buscar todas as disciplinas que têm avaliações
            response = supabase.table('avaliacoes')\
                .select('inscricao_id')\
                .execute()
            
            if not response.data:
                return {
                    'total_disciplinas': 0,
                    'processadas': 0,
                    'erros': 0,
                    'detalhes': []
                }
            
            # Buscar IDs únicos de disciplinas
            inscricoes_ids = [a['inscricao_id'] for a in response.data]
            
            response = supabase.table('inscricoes')\
                .select('disciplina_id')\
                .in_('id', inscricoes_ids)\
                .execute()
            
            if not response.data:
                return {
                    'total_disciplinas': 0,
                    'processadas': 0,
                    'erros': 0,
                    'detalhes': []
                }
            
            disciplinas_ids = list(set([i['disciplina_id'] for i in response.data]))
            
            # Processar cada disciplina
            detalhes = []
            processadas = 0
            erros = 0
            
            for disciplina_id in disciplinas_ids:
                try:
                    # Buscar nome da disciplina
                    disc = supabase.table('disciplinas')\
                        .select('nome')\
                        .eq('id', disciplina_id)\
                        .execute()
                    
                    nome_disciplina = disc.data[0]['nome'] if disc.data else f'ID {disciplina_id}'
                    
                    # Classificar
                    resultados = cls.classificar_disciplina(disciplina_id)
                    
                    if resultados:
                        # Salvar classificação
                        sucesso = cls.salvar_classificacao(disciplina_id)
                        
                        aprovados = sum(1 for r in resultados if r['status'] == 'APROVADO')
                        reprovados = len(resultados) - aprovados
                        
                        detalhes.append({
                            'disciplina_id': disciplina_id,
                            'nome': nome_disciplina,
                            'total': len(resultados),
                            'aprovados': aprovados,
                            'reprovados': reprovados,
                            'salvo': sucesso
                        })
                        processadas += 1
                    else:
                        detalhes.append({
                            'disciplina_id': disciplina_id,
                            'nome': nome_disciplina,
                            'total': 0,
                            'mensagem': 'Sem avaliações'
                        })
                except Exception as e:
                    erros += 1
                    detalhes.append({
                        'disciplina_id': disciplina_id,
                        'erro': str(e)
                    })
            
            return {
                'total_disciplinas': len(disciplinas_ids),
                'processadas': processadas,
                'erros': erros,
                'detalhes': detalhes
            }
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {
                'total_disciplinas': 0,
                'processadas': 0,
                'erros': 1,
                'detalhes': [{'erro': str(e)}]
            }
@classmethod
def classificar_por_grupo(cls, grupo_id: int, funcao: str) -> List[Dict]:
    """Classifica os candidatos de um grupo/função"""
    try:
        # Buscar todas as avaliações do grupo/função
        response = supabase.table('avaliacoes')\
            .select('*')\
            .eq('grupo_id', grupo_id)\
            .eq('funcao', funcao)\
            .execute()
        
        if not response.data:
            return []
        
        # Ordenar por nota final (decrescente)
        avaliacoes = sorted(response.data, key=lambda x: x['nota_final'] or 0, reverse=True)
        
        # Atualizar classificação no banco
        for i, aval in enumerate(avaliacoes, 1):
            supabase.table('avaliacoes')\
                .update({'classificacao': i})\
                .eq('id', aval['id'])\
                .execute()
            aval['classificacao'] = i
        
        return avaliacoes
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []        
from supabase_client import supabase
from typing import Dict, List


class ResultadoService:
    """Serviço para gerenciar resultados finais (por grupo/função)"""
    
    @classmethod
    def gerar_resultado_grupo(cls, grupo_id: int, funcao: str) -> Dict:
        """Gera o resultado de um grupo/função (com cadastro de reserva)"""
        try:
            grupo_resp = supabase.table('grupos')\
                .select('nome, curso_id, cursos(nome)')\
                .eq('id', grupo_id)\
                .execute()
            
            if not grupo_resp.data:
                return {'status': 'error', 'message': 'Grupo não encontrado'}
            
            grupo = grupo_resp.data[0]
            
            response = supabase.table('avaliacoes')\
                .select('*')\
                .eq('grupo_id', grupo_id)\
                .eq('funcao', funcao)\
                .order('nota_final', desc=True)\
                .execute()
            
            if not response.data:
                return {
                    'grupo_id': grupo_id,
                    'grupo': grupo['nome'],
                    'curso': grupo['cursos']['nome'] if grupo.get('cursos') else None,
                    'funcao': funcao,
                    'cadastro_reserva': {'cg': [], 'rv': []},
                    'reprovados': [],
                    'resumo': {
                        'total': 0,
                        'cadastro_reserva': 0,
                        'cg': 0,
                        'rv': 0,
                        'reprovados': 0
                    }
                }
            
            inscricao_ids = [a['inscricao_id'] for a in response.data]
            
            insc_resp = supabase.table('inscricoes')\
                .select('*')\
                .in_('id', inscricao_ids)\
                .execute()
            
            inscricoes_map = {i['id']: i for i in insc_resp.data}
            
            candidato_ids = [i['candidato_id'] for i in insc_resp.data]
            
            cand_resp = supabase.table('candidatos')\
                .select('id, nome_completo, cpf, email')\
                .in_('id', candidato_ids)\
                .execute()
            
            candidatos_map = {c['id']: c for c in cand_resp.data}
            
            aprovados = []
            reprovados = []
            
            for aval in response.data:
                inscricao = inscricoes_map.get(aval['inscricao_id'])
                if not inscricao:
                    continue
                
                candidato = candidatos_map.get(inscricao['candidato_id'])
                if not candidato:
                    continue
                
                aprovado = (
                    (aval['nota_pp'] or 0) >= 24 
                    and (aval['nota_final'] or 0) >= 60
                )
                
                resultado = {
                    'inscricao_id': inscricao['id'],
                    'avaliacao_id': aval['id'],
                    'nome_completo': candidato['nome_completo'],
                    'cpf': candidato['cpf'],
                    'email': candidato['email'],
                    'nota_ac': aval['nota_ac'],
                    'nota_pp': aval['nota_pp'],
                    'nota_final': aval['nota_final'],
                    'classificacao': aval['classificacao'],
                    'parecer': aval['parecer'],
                    'opta_cotas': inscricao.get('opta_cotas', False),
                    'status_cr': aval.get('status_cr', 'aguardando'),
                    'data_convocacao': aval.get('data_convocacao'),
                    'observacoes': aval.get('observacoes'),
                    'titulacao': aval.get('titulacao')
                }
                
                if aprovado:
                    aprovados.append(resultado)
                else:
                    reprovados.append(resultado)
            
            aprovados.sort(key=lambda x: x['classificacao'] or 999)
            reprovados.sort(key=lambda x: x['classificacao'] or 999)
            
            cg = [a for a in aprovados if not a['opta_cotas']]
            rv = [a for a in aprovados if a['opta_cotas']]
            
            for i, a in enumerate(cg, 1):
                a['posicao_cg'] = i
            for i, a in enumerate(rv, 1):
                a['posicao_rv'] = i
            
            return {
                'grupo_id': grupo_id,
                'grupo': grupo['nome'],
                'curso': grupo['cursos']['nome'] if grupo.get('cursos') else None,
                'funcao': funcao,
                'cadastro_reserva': {
                    'cg': cg,
                    'rv': rv
                },
                'reprovados': reprovados,
                'resumo': {
                    'total': len(aprovados) + len(reprovados),
                    'cadastro_reserva': len(aprovados),
                    'cg': len(cg),
                    'rv': len(rv),
                    'reprovados': len(reprovados)
                }
            }
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @classmethod
    def gerar_resultado_geral(cls) -> Dict:
        """Gera o resultado consolidado de todos os grupos"""
        try:
            response = supabase.table('avaliacoes')\
                .select('grupo_id, funcao')\
                .execute()
            
            if not response.data:
                return {
                    'total_grupos': 0,
                    'total_candidatos': 0,
                    'total_aprovados': 0,
                    'total_reprovados': 0,
                    'grupos': []
                }
            
            combinacoes = list(set(
                (a['grupo_id'], a['funcao']) 
                for a in response.data 
                if a['grupo_id'] and a['funcao']
            ))
            
            resultados = []
            total_aprovados = 0
            total_reprovados = 0
            total_candidatos = 0
            
            for grupo_id, funcao in combinacoes:
                resultado = cls.gerar_resultado_grupo(grupo_id, funcao)
                
                if resultado and 'grupo' in resultado:
                    resultados.append(resultado)
                    total_aprovados += resultado['resumo']['cadastro_reserva']
                    total_reprovados += resultado['resumo']['reprovados']
                    total_candidatos += resultado['resumo']['total']
            
            return {
                'total_grupos': len(resultados),
                'total_candidatos': total_candidatos,
                'total_aprovados': total_aprovados,
                'total_reprovados': total_reprovados,
                'grupos': resultados
            }
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @classmethod
    def recalcular_classificacao_grupo(cls, grupo_id: int, funcao: str) -> Dict:
        """Recalcula a classificação de um grupo/função"""
        try:
            # Buscar todas as avaliações do grupo/função
            response = supabase.table('avaliacoes')\
                .select('id, nota_final')\
                .eq('grupo_id', grupo_id)\
                .eq('funcao', funcao)\
                .execute()
            
            if not response.data:
                return {'status': 'error', 'message': 'Nenhuma avaliação encontrada'}
            
            # Ordenar por nota final (decrescente)
            avaliacoes = sorted(
                response.data, 
                key=lambda x: x['nota_final'] or 0, 
                reverse=True
            )
            
            # Atualizar classificação
            atualizados = 0
            for i, aval in enumerate(avaliacoes, 1):
                supabase.table('avaliacoes')\
                    .update({'classificacao': i})\
                    .eq('id', aval['id'])\
                    .execute()
                atualizados += 1
            
            return {
                'status': 'success',
                'message': f'Classificação recalculada para {atualizados} candidatos',
                'grupo_id': grupo_id,
                'funcao': funcao,
                'total': atualizados
            }
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {'status': 'error', 'message': str(e)}
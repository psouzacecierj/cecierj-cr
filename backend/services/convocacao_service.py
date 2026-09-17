from supabase_client import supabase
from typing import Dict, List, Optional
from datetime import date


class ConvocacaoService:
    """
    Serviço para gerenciar convocações do Cadastro de Reserva.
    
    Regra 3:1 (Edital 001/2026, item 5.1.1):
    - A cada 3 convocações de ampla concorrência (CG), 1 deve ser de cota (RV).
    - Se não houver candidato de cota, segue a ordem geral.
    - O contador é acumulativo dentro do grupo/função.
    
    Lógica do ciclo (4 convocações):
    - 1ª → CG (posição 1)
    - 2ª → CG (posição 2)
    - 3ª → CG (posição 3)
    - 4ª → RV (posição 0 - reseta)
    
    IMPORTANTE: Apenas candidatos APROVADOS entram no CR:
    - PP >= 24 E Nota Final >= 60
    """
    
    @classmethod
    def listar_cr_grupo(cls, grupo_id: int, funcao: str) -> Dict:
        """
        Lista o Cadastro de Reserva de um grupo/função, ordenado por classificação.
        Inclui APENAS candidatos APROVADOS (PP >= 24 e Nota Final >= 60).
        Usa JOIN para reduzir requisições ao Supabase.
        """
        try:
            # Buscar avaliações do grupo/função
            response = supabase.table('avaliacoes')\
                .select('*')\
                .eq('grupo_id', grupo_id)\
                .eq('funcao', funcao)\
                .order('nota_final', desc=True)\
                .execute()
            
            if not response.data:
                return {
                    'grupo_id': grupo_id,
                    'funcao': funcao,
                    'cg': [],
                    'rv': [],
                    'total': 0,
                    'total_cg': 0,
                    'total_rv': 0,
                    'total_reprovados': 0
                }
            
            # Buscar TODAS as inscrições de uma vez
            inscricao_ids = [a['inscricao_id'] for a in response.data]
            
            insc_response = supabase.table('inscricoes')\
                .select('*')\
                .in_('id', inscricao_ids)\
                .execute()
            
            inscricoes_map = {i['id']: i for i in insc_response.data}
            
            # Buscar TODOS os candidatos de uma vez
            candidato_ids = [i['candidato_id'] for i in insc_response.data]
            
            cand_response = supabase.table('candidatos')\
                .select('id, nome_completo, cpf, email')\
                .in_('id', candidato_ids)\
                .execute()
            
            candidatos_map = {c['id']: c for c in cand_response.data}
            
            # Montar resultado — APENAS APROVADOS
            cg = []
            rv = []
            reprovados = 0
            
            for aval in response.data:
                # ✅ FILTRO: Só incluir se APROVADO
                nota_pp = aval.get('nota_pp') or 0
                nota_final = aval.get('nota_final') or 0
                
                if nota_pp < 24 or nota_final < 60:
                    reprovados += 1
                    continue  # ❌ Reprovado → não entra no CR
                
                inscricao = inscricoes_map.get(aval['inscricao_id'])
                if not inscricao:
                    continue
                
                candidato = candidatos_map.get(inscricao['candidato_id'])
                if not candidato:
                    continue
                
                item = {
                    'avaliacao_id': aval['id'],
                    'inscricao_id': inscricao['id'],
                    'nome_completo': candidato['nome_completo'],
                    'cpf': candidato['cpf'],
                    'email': candidato['email'],
                    'nota_final': aval['nota_final'],
                    'classificacao': aval['classificacao'],
                    'titulacao': aval.get('titulacao'),
                    'status_cr': aval.get('status_cr', 'aguardando'),
                    'data_convocacao': aval.get('data_convocacao'),
                    'observacoes': aval.get('observacoes'),
                    'opta_cotas': inscricao.get('opta_cotas', False)
                }
                
                if inscricao.get('opta_cotas', False):
                    rv.append(item)
                else:
                    cg.append(item)
            
            cg.sort(key=lambda x: x['classificacao'] or 999)
            rv.sort(key=lambda x: x['classificacao'] or 999)
            
            return {
                'grupo_id': grupo_id,
                'funcao': funcao,
                'cg': cg,
                'rv': rv,
                'total': len(cg) + len(rv),
                'total_cg': len(cg),
                'total_rv': len(rv),
                'total_reprovados': reprovados
            }
        except Exception as e:
            print(f"❌ Erro em listar_cr_grupo: {e}")
            return {
                'grupo_id': grupo_id,
                'funcao': funcao,
                'cg': [],
                'rv': [],
                'total': 0,
                'total_cg': 0,
                'total_rv': 0,
                'total_reprovados': 0
            }
    
    @classmethod
    def calcular_proxima_convocacao(cls, grupo_id: int, funcao: str) -> Dict:
        """
        Calcula a próxima convocação com base na regra 3:1.
        
        Lógica:
        - Conta convocações feitas (CG + RV)
        - A cada 4 convocações, a 4ª é RV (posicao_no_ciclo == 3)
        - Se não houver candidato do tipo esperado, ajusta para o outro tipo
        """
        try:
            cr = cls.listar_cr_grupo(grupo_id, funcao)
            
            convocados_cg = [c for c in cr['cg'] if c['status_cr'] == 'convocado']
            convocados_rv = [c for c in cr['rv'] if c['status_cr'] == 'convocado']
            
            total_cg = len(convocados_cg)
            total_rv = len(convocados_rv)
            
            proximo_cg = next((c for c in cr['cg'] if c['status_cr'] == 'aguardando'), None)
            proximo_rv = next((c for c in cr['rv'] if c['status_cr'] == 'aguardando'), None)
            
            total_convocacoes = total_cg + total_rv
            posicao_no_ciclo = total_convocacoes % 4
            
            # Regra 3:1 → a cada 4 convocações, a 4ª é RV
            deveria_ser_rv = (posicao_no_ciclo == 3)
            
            # Ajustar se não houver candidato do tipo esperado
            if deveria_ser_rv:
                if proximo_rv:
                    proximo = proximo_rv
                    tipo = 'RV'
                    aviso = "⚠️ Próxima convocação deve ser de COTA (RV)"
                elif proximo_cg:
                    proximo = proximo_cg
                    tipo = 'CG'
                    aviso = "ℹ️ Não há candidatos de COTA. Convocando CG (próximo da fila)"
                else:
                    proximo = None
                    tipo = None
                    aviso = "Não há candidatos aguardando convocação"
            else:
                if proximo_cg:
                    proximo = proximo_cg
                    tipo = 'CG'
                    aviso = "Próxima convocação deve ser de AMPLA CONCORRÊNCIA (CG)"
                elif proximo_rv:
                    proximo = proximo_rv
                    tipo = 'RV'
                    aviso = "ℹ️ Não há candidatos de CG. Convocando RV (próximo da fila)"
                else:
                    proximo = None
                    tipo = None
                    aviso = "Não há candidatos aguardando convocação"
            
            return {
                'grupo_id': grupo_id,
                'funcao': funcao,
                'tipo_proxima': tipo,
                'proximo_candidato': proximo,
                'posicao_no_ciclo': posicao_no_ciclo,
                'total_cg_convocados': total_cg,
                'total_rv_convocados': total_rv,
                'total_convocacoes': total_convocacoes,
                'aviso': aviso
            }
        except Exception as e:
            print(f"❌ Erro em calcular_proxima_convocacao: {e}")
            return {
                'grupo_id': grupo_id,
                'funcao': funcao,
                'tipo_proxima': None,
                'proximo_candidato': None,
                'posicao_no_ciclo': 0,
                'total_cg_convocados': 0,
                'total_rv_convocados': 0,
                'total_convocacoes': 0,
                'aviso': 'Erro ao calcular. Tente novamente.'
            }
    
    @classmethod
    def convocar_candidato(cls, avaliacao_id: int, data_convocacao: str, observacoes: str = '') -> Optional[Dict]:
        """Convoca um candidato"""
        try:
            dados = {
                'status_cr': 'convocado',
                'data_convocacao': data_convocacao,
                'observacoes': observacoes
            }
            
            response = supabase.table('avaliacoes')\
                .update(dados)\
                .eq('id', avaliacao_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    @classmethod
    def registrar_recusa(cls, avaliacao_id: int, motivo: str = '') -> Optional[Dict]:
        """Registra recusa"""
        try:
            response = supabase.table('avaliacoes')\
                .update({
                    'status_cr': 'recusou',
                    'observacoes': motivo
                })\
                .eq('id', avaliacao_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    @classmethod
    def atualizar_status(cls, avaliacao_id: int, dados: Dict) -> Optional[Dict]:
        """Atualiza status"""
        try:
            response = supabase.table('avaliacoes')\
                .update(dados)\
                .eq('id', avaliacao_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    @classmethod
    def listar_kpis(cls, edital_id: Optional[int] = None) -> Dict:
        """
        KPIs do CR (otimizado).
        Considera apenas candidatos APROVADOS (no CR).
        """
        try:
            query = supabase.table('avaliacoes')\
                .select('status_cr, prazo_convocacao, nota_pp, nota_final')
            
            if edital_id:
                insc = supabase.table('inscricoes')\
                    .select('id')\
                    .eq('edital_id', edital_id)\
                    .execute()
                
                if insc.data:
                    ids = [i['id'] for i in insc.data]
                    query = query.in_('inscricao_id', ids)
            
            response = query.execute()
            
            if not response.data:
                return {
                    'total': 0,
                    'convocados': 0,
                    'aguardando': 0,
                    'expirados': 0,
                    'recusou': 0
                }
            
            # ✅ Filtrar apenas APROVADOS (que estão no CR)
            aprovados = [
                a for a in response.data
                if (a.get('nota_pp') or 0) >= 24 
                and (a.get('nota_final') or 0) >= 60
            ]
            
            total = len(aprovados)
            convocados = sum(1 for a in aprovados if a.get('status_cr') == 'convocado')
            aguardando = sum(1 for a in aprovados if a.get('status_cr') == 'aguardando')
            recusou = sum(1 for a in aprovados if a.get('status_cr') == 'recusou')
            
            hoje = date.today()
            expirados = sum(
                1 for a in aprovados
                if a.get('status_cr') == 'aguardando'
                and a.get('prazo_convocacao')
                and a['prazo_convocacao'] < str(hoje)
            )
            
            return {
                'total': total,
                'convocados': convocados,
                'aguardando': aguardando,
                'expirados': expirados,
                'recusou': recusou
            }
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {
                'total': 0,
                'convocados': 0,
                'aguardando': 0,
                'expirados': 0,
                'recusou': 0
            }
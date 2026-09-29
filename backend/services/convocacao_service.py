from supabase_client import supabase
from typing import Dict, List, Optional
from datetime import date, datetime


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

    # ═══════════════════════════════════════════════════════════
    # AUXILIAR PRIVADO
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _calcular_aviso_edital(edital: Dict) -> Dict:
        """
        Calcula o aviso de validade de um edital.
        
        Retorna dict com:
            nivel, cor, mensagem, dias_restantes, meses_restantes,
            prazo_convocacao (str|None), validade_pagamento_bolsa (str|None),
            id, numero, semestre
        """
        prazo = edital.get('prazo_convocacao')
        validade_bolsa = edital.get('validade_pagamento_bolsa')

        hoje = date.today()

        # ── Calcular dias/meses restantes ───────────────────────
        if prazo:
            try:
                prazo_date = datetime.strptime(str(prazo), '%Y-%m-%d').date()
                dias_restantes = (prazo_date - hoje).days
                meses_restantes = dias_restantes // 30
            except Exception:
                dias_restantes = None
                meses_restantes = None
        else:
            dias_restantes = None
            meses_restantes = None

        # ── Definir nível de alerta ─────────────────────────────
        if dias_restantes is None:
            nivel, cor = 'sem_prazo', 'cinza'
            mensagem = 'Sem prazo definido'
        elif dias_restantes < 0:
            nivel, cor = 'expirado', 'preto'
            mensagem = f'Edital expirado há {abs(dias_restantes)} dias'
        elif dias_restantes <= 30:
            nivel, cor = 'critico', 'vermelho'
            mensagem = f'⚠️ URGENTE: expira em {dias_restantes} dias'
        elif meses_restantes is not None and meses_restantes <= 3:
            nivel, cor = 'alerta', 'laranja'
            mensagem = f'⚠️ Atenção: expira em {meses_restantes} meses'
        elif meses_restantes is not None and meses_restantes <= 12:
            nivel, cor = 'atencao', 'amarelo'
            mensagem = f'Atenção: expira em {meses_restantes} meses'
        else:
            nivel, cor = 'ok', 'verde'
            mensagem = f'OK: expira em {meses_restantes} meses'

        return {
            'id': edital.get('id'),
            'numero': edital.get('numero'),
            'semestre': edital.get('semestre'),
            'prazo_convocacao': str(prazo) if prazo else None,
            'validade_pagamento_bolsa': str(validade_bolsa) if validade_bolsa else None,
            'dias_restantes': dias_restantes,
            'meses_restantes': meses_restantes,
            'nivel': nivel,
            'cor': cor,
            'mensagem': mensagem,
        }

    # ═══════════════════════════════════════════════════════════
    # CR — CADASTRO DE RESERVA
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def listar_cr_grupo(cls, grupo_id: int, funcao: str) -> Dict:
        """
        Lista o Cadastro de Reserva de um grupo/função, ordenado por classificação.
        Inclui APENAS candidatos APROVADOS (PP >= 24 e Nota Final >= 60).
        Usa JOIN para reduzir requisições ao Supabase.
        """
        try:
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
                    'cg': [], 'rv': [],
                    'total': 0, 'total_cg': 0, 'total_rv': 0,
                    'total_reprovados': 0
                }

            inscricao_ids = [a['inscricao_id'] for a in response.data]

            insc_response = supabase.table('inscricoes')\
                .select('*')\
                .in_('id', inscricao_ids)\
                .execute()

            inscricoes_map = {i['id']: i for i in insc_response.data}

            candidato_ids = [i['candidato_id'] for i in insc_response.data]

            cand_response = supabase.table('candidatos')\
                .select('id, nome_completo, cpf, email')\
                .in_('id', candidato_ids)\
                .execute()

            candidatos_map = {c['id']: c for c in cand_response.data}

            cg, rv, reprovados = [], [], 0

            for aval in response.data:
                nota_pp = aval.get('nota_pp') or 0
                nota_final = aval.get('nota_final') or 0

                if nota_pp < 24 or nota_final < 60:
                    reprovados += 1
                    continue

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
                'cg': cg, 'rv': rv,
                'total': len(cg) + len(rv),
                'total_cg': len(cg),
                'total_rv': len(rv),
                'total_reprovados': reprovados
            }
        except Exception as e:
            print(f"❌ Erro em listar_cr_grupo: {e}")
            return {
                'grupo_id': grupo_id, 'funcao': funcao,
                'cg': [], 'rv': [],
                'total': 0, 'total_cg': 0, 'total_rv': 0,
                'total_reprovados': 0
            }

    @classmethod
    def calcular_proxima_convocacao(cls, grupo_id: int, funcao: str) -> Dict:
        """Calcula a próxima convocação com base na regra 3:1."""
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

            deveria_ser_rv = (posicao_no_ciclo == 3)

            if deveria_ser_rv:
                if proximo_rv:
                    proximo, tipo = proximo_rv, 'RV'
                    aviso = "⚠️ Próxima convocação deve ser de COTA (RV)"
                elif proximo_cg:
                    proximo, tipo = proximo_cg, 'CG'
                    aviso = "ℹ️ Não há candidatos de COTA. Convocando CG (próximo da fila)"
                else:
                    proximo, tipo, aviso = None, None, "Não há candidatos aguardando convocação"
            else:
                if proximo_cg:
                    proximo, tipo = proximo_cg, 'CG'
                    aviso = "Próxima convocação deve ser de AMPLA CONCORRÊNCIA (CG)"
                elif proximo_rv:
                    proximo, tipo = proximo_rv, 'RV'
                    aviso = "ℹ️ Não há candidatos de CG. Convocando RV (próximo da fila)"
                else:
                    proximo, tipo, aviso = None, None, "Não há candidatos aguardando convocação"

            return {
                'grupo_id': grupo_id, 'funcao': funcao,
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
                'grupo_id': grupo_id, 'funcao': funcao,
                'tipo_proxima': None, 'proximo_candidato': None,
                'posicao_no_ciclo': 0,
                'total_cg_convocados': 0, 'total_rv_convocados': 0,
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
                .update({'status_cr': 'recusou', 'observacoes': motivo})\
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
        """KPIs do CR (apenas aprovados)."""
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
                return {'total': 0, 'convocados': 0, 'aguardando': 0, 'expirados': 0, 'recusou': 0}

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
            return {'total': 0, 'convocados': 0, 'aguardando': 0, 'expirados': 0, 'recusou': 0}

    # ═══════════════════════════════════════════════════════════
    # AVISOS DE VALIDADE
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def listar_avisos_validade(cls) -> Dict:
        """
        Lista todos os editais ativos com seus prazos de validade e avisos.
        
        Regra de alerta:
        - > 12 meses: 🟢 OK (verde)
        - 3 a 12 meses: 🟡 ATENÇÃO (amarelo)
        - 1 a 3 meses: 🟠 ALERTA (laranja)
        - 0 a 1 mês: 🔴 CRÍTICO (vermelho)
        - < 0 dias: ❌ EXPIRADO (preto)
        """
        try:
            response = supabase.table('editais')\
                .select('*')\
                .eq('ativo', True)\
                .execute()

            if not response.data:
                return {'total': 0, 'editais': []}

            editais = [cls._calcular_aviso_edital(e) for e in response.data]

            # Ordenar por dias restantes (mais crítico primeiro)
            editais.sort(
                key=lambda x: x['dias_restantes']
                if x['dias_restantes'] is not None
                else 99999
            )

            return {'total': len(editais), 'editais': editais}
        except Exception as e:
            print(f"❌ Erro em listar_avisos_validade: {e}")
            return {'total': 0, 'editais': []}

    @classmethod
    def atualizar_prazos_edital(cls, edital_id: int, dados: Dict) -> Dict:
        """
        Atualiza prazos (prazo_convocacao, validade_pagamento_bolsa) de um edital.
        
        Retorna dict padronizado:
            {
                'success': bool,
                'message': str,
                'status_code': int (opcional),
                'data': { 'edital': {...}, 'aviso': {...} }
            }
        """
        try:
            # ── 1. Verificar se edital existe ───────────────────
            edital_atual = supabase.table('editais')\
                .select('*')\
                .eq('id', edital_id)\
                .execute()

            if not edital_atual.data:
                return {
                    'success': False,
                    'message': f'Edital {edital_id} não encontrado.',
                    'status_code': 404
                }

            # ── 2. Montar payload com validação de datas ────────
            payload = {}

            for campo in ('prazo_convocacao', 'validade_pagamento_bolsa'):
                if campo in dados:
                    valor = dados[campo]
                    if valor:  # aceita None/'' para limpar
                        try:
                            datetime.strptime(str(valor), '%Y-%m-%d')
                        except ValueError:
                            return {
                                'success': False,
                                'message': f"Formato inválido em '{campo}'. Use YYYY-MM-DD.",
                                'status_code': 400
                            }
                    payload[campo] = valor

            if not payload:
                return {
                    'success': False,
                    'message': 'Nenhum campo válido para atualizar.',
                    'status_code': 400
                }

            # ── 3. Executar update no Supabase ──────────────────
            resultado = supabase.table('editais')\
                .update(payload)\
                .eq('id', edital_id)\
                .execute()

            if not resultado.data:
                return {
                    'success': False,
                    'message': 'Falha ao atualizar o edital no banco.',
                    'status_code': 500
                }

            # ── 4. Recalcular aviso com dados atualizados ───────
            edital_atualizado = resultado.data[0]
            aviso = cls._calcular_aviso_edital(edital_atualizado)

            return {
                'success': True,
                'message': 'Prazos atualizados com sucesso.',
                'data': {
                    'edital': edital_atualizado,
                    'aviso': aviso
                }
            }
        except Exception as e:
            print(f"❌ Erro em atualizar_prazos_edital: {e}")
            return {
                'success': False,
                'message': f'Erro interno: {str(e)}',
                'status_code': 500
            }
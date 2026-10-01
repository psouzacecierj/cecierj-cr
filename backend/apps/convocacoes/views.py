from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from services.convocacao_service import ConvocacaoService
from services.grupo_service import GrupoService


# ═══════════════════════════════════════════════════════════════
# CR — Cadastro de Reserva
# ═══════════════════════════════════════════════════════════════

@api_view(['GET'])
def listar_cr_grupo(request, grupo_id):
    """Lista o CR de um grupo/função"""
    funcao = request.GET.get('funcao', 'Coordenador de Disciplina')
    try:
        cr = ConvocacaoService.listar_cr_grupo(grupo_id, funcao)
        return Response({'status': 'success', 'data': cr})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)


@api_view(['GET'])
def proxima_convocacao(request, grupo_id):
    """Retorna a próxima convocação sugerida (com regra 3:1)"""
    funcao = request.GET.get('funcao', 'Coordenador de Disciplina')
    try:
        resultado = ConvocacaoService.calcular_proxima_convocacao(grupo_id, funcao)
        return Response({'status': 'success', 'data': resultado})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)


@api_view(['POST'])
def convocar(request, avaliacao_id):
    """Convoca um candidato"""
    try:
        data_convocacao = request.data.get('data_convocacao', '')
        observacoes = request.data.get('observacoes', '')
        resultado = ConvocacaoService.convocar_candidato(
            avaliacao_id, data_convocacao, observacoes
        )
        if resultado:
            return Response({'status': 'success', 'data': resultado})
        return Response({'status': 'error', 'message': 'Erro ao convocar'}, status=400)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)


@api_view(['POST'])
def registrar_recusa(request, avaliacao_id):
    """Registra recusa de um candidato"""
    try:
        motivo = request.data.get('motivo', '')
        resultado = ConvocacaoService.registrar_recusa(avaliacao_id, motivo)
        if resultado:
            return Response({'status': 'success', 'data': resultado})
        return Response({'status': 'error', 'message': 'Erro ao registrar recusa'}, status=400)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)


@api_view(['PATCH'])
def atualizar_status(request, avaliacao_id):
    """Atualiza status e dados de convocação"""
    try:
        resultado = ConvocacaoService.atualizar_status(avaliacao_id, request.data)
        if resultado:
            return Response({'status': 'success', 'data': resultado})
        return Response({'status': 'error', 'message': 'Erro ao atualizar'}, status=400)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)


@api_view(['GET'])
def kpis(request):
    """KPIs do CR"""
    edital_id = request.GET.get('edital_id')
    try:
        resultado = ConvocacaoService.listar_kpis(int(edital_id) if edital_id else None)
        return Response({'status': 'success', 'data': resultado})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)


# ═══════════════════════════════════════════════════════════════
# Avisos de Validade dos Editais
# ═══════════════════════════════════════════════════════════════

@api_view(['GET'])
def avisos_validade(request):
    """
    Lista avisos de validade dos editais.
    
    Retorna todos os editais ativos com:
    - Prazo de convocação
    - Validade da bolsa
    - Dias/meses restantes
    - Nível de alerta (ok, atencao, alerta, critico, expirado)
    - Cor sugerida (verde, amarelo, laranja, vermelho, preto)
    - Mensagem descritiva
    """
    try:
        resultado = ConvocacaoService.listar_avisos_validade()
        return Response({
            'status': 'success',
            'data': resultado
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'PUT'])
def atualizar_prazos_edital(request, edital_id):
    """
    Atualiza os prazos de um edital.
    
    Body esperado (JSON):
    {
        "prazo_convocacao": "2026-03-31",          # opcional
        "validade_pagamento_bolsa": "2026-12-31"   # opcional
    }
    
    Retorna o edital atualizado com avisos recalculados.
    """
    try:
        dados = request.data or {}

        if not dados:
            return Response(
                {"status": "error", "message": "Nenhum dado enviado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = ConvocacaoService.atualizar_prazos_edital(edital_id, dados)

        if not resultado.get('success'):
            return Response(
                {
                    "status": "error",
                    "message": resultado.get('message', 'Erro ao atualizar prazos.')
                },
                status=resultado.get('status_code', status.HTTP_400_BAD_REQUEST)
            )

        return Response({
            "status": "success",
            "message": resultado.get('message', 'Prazos atualizados com sucesso.'),
            "data": resultado.get('data', {})
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"status": "error", "message": f"Erro interno: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
# ═══════════════════════════════════════════════════════════════
# Grupos
# ═══════════════════════════════════════════════════════════════

@api_view(['GET'])
def listar_grupos(request):
    """
    Lista grupos, opcionalmente filtrando por edital_id e/ou curso_id.
    
    Query params:
        ?edital_id=1
        ?curso_id=1
    """
    try:
        edital_id = request.GET.get('edital_id')
        curso_id = request.GET.get('curso_id')

        grupos = GrupoService.listar_grupos(
            edital_id=int(edital_id) if edital_id else None,
            curso_id=int(curso_id) if curso_id else None,
        )

        return Response({
            'status': 'success',
            'data': grupos,
            'total': len(grupos)
        })
    except Exception as e:
        return Response(
            {'status': 'error', 'message': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
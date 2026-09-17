from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from services.convocacao_service import ConvocacaoService


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
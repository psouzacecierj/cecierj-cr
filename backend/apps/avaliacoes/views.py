from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from services.avaliacao_service import AvaliacaoService
from services.resultado_service import ResultadoService


# ============================================================
# AVALIAÇÕES
# ============================================================

@api_view(['POST'])
def lancar_avaliacao(request):
    """Lançar notas AC e PP para uma inscrição"""
    try:
        inscricao_id = request.data.get('inscricao_id')
        nota_ac = float(request.data.get('nota_ac', 0))
        nota_pp = float(request.data.get('nota_pp', 0))
        
        if not inscricao_id:
            return Response({
                'status': 'error',
                'message': 'inscricao_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        avaliacao = AvaliacaoService.criar_ou_atualizar(
            inscricao_id, nota_ac, nota_pp
        )
        
        if avaliacao:
            return Response({'status': 'success', 'data': avaliacao})
        
        return Response({
            'status': 'error',
            'message': 'Erro ao lançar avaliação'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def listar_avaliacoes_disciplina(request, disciplina_id):
    """Lista avaliações de uma disciplina"""
    try:
        avaliacoes = AvaliacaoService.listar_por_disciplina(disciplina_id)
        return Response({
            'status': 'success',
            'data': avaliacoes,
            'total': len(avaliacoes)
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def classificar_disciplina(request, disciplina_id):
    """Classifica os candidatos de uma disciplina"""
    try:
        resultados = AvaliacaoService.classificar_disciplina(disciplina_id)
        return Response({
            'status': 'success',
            'data': resultados,
            'total': len(resultados)
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def salvar_classificacao(request, disciplina_id):
    """Salva a classificação no banco"""
    try:
        sucesso = AvaliacaoService.salvar_classificacao(disciplina_id)
        if sucesso:
            return Response({
                'status': 'success',
                'message': 'Classificação salva com sucesso'
            })
        return Response({
            'status': 'error',
            'message': 'Erro ao salvar classificação'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def processar_todas_disciplinas(request):
    """Processa todas as disciplinas que têm avaliações"""
    try:
        resultado = AvaliacaoService.processar_todas_disciplinas()
        return Response({'status': 'success', 'data': resultado})
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# RESULTADOS
# ============================================================

@api_view(['GET'])
def resultado_grupo(request, grupo_id):
    """Gera o resultado de um grupo/função"""
    funcao = request.GET.get('funcao', 'Coordenador de Disciplina')
    try:
        resultado = ResultadoService.gerar_resultado_grupo(grupo_id, funcao)
        return Response({'status': 'success', 'data': resultado})
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def resultado_geral(request):
    """Gera o resultado consolidado de todos os grupos"""
    try:
        resultado = ResultadoService.gerar_resultado_geral()
        return Response({'status': 'success', 'data': resultado})
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def recalcular_classificacao(request, grupo_id):
    """Recalcula a classificação de um grupo/função"""
    funcao = request.data.get('funcao', 'Coordenador de Disciplina')
    try:
        resultado = ResultadoService.recalcular_classificacao_grupo(grupo_id, funcao)
        return Response({'status': 'success', 'data': resultado})
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
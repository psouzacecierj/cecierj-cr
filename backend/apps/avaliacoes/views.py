from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from services.avaliacao_service import AvaliacaoService

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
            return Response({
                'status': 'success',
                'data': avaliacao
            })
        
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
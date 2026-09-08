from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from services.supabase_sync import SupabaseSync

@api_view(['GET'])
def listar_avaliacoes(request):
    """Lista todas as avaliações"""
    try:
        avaliacoes = SupabaseSync.get_all('avaliacoes')
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

@api_view(['POST'])
def criar_avaliacao(request):
    """Cria uma nova avaliação"""
    try:
        dados = request.data
        
        # Calcular nota final se tiver AC e PP
        if 'nota_ac' in dados and 'nota_pp' in dados:
            peso_ac = 0.6
            peso_pp = 0.4
            dados['nota_final'] = (dados['nota_ac'] * peso_ac) + (dados['nota_pp'] * peso_pp)
        
        avaliacao = SupabaseSync.insert('avaliacoes', dados)
        
        if avaliacao:
            return Response({
                'status': 'success',
                'data': avaliacao
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'message': 'Erro ao criar avaliação'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
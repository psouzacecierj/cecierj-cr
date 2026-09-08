from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from services.candidato_service import CandidatoService

@api_view(['GET'])
def listar_candidatos(request):
    """Lista todos os candidatos"""
    try:
        candidatos = CandidatoService.listar_todos()
        return Response({
            'status': 'success',
            'data': candidatos,
            'total': len(candidatos)
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def buscar_candidato(request, id):
    """Busca candidato por ID"""
    try:
        candidato = CandidatoService.buscar_por_id(id)
        if candidato:
            return Response({
                'status': 'success',
                'data': candidato
            })
        return Response({
            'status': 'error',
            'message': 'Candidato não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def criar_candidato(request):
    """Cria um novo candidato"""
    try:
        dados = request.data
        
        # Verificar se CPF já existe
        existente = CandidatoService.buscar_por_cpf(dados.get('cpf'))
        if existente:
            return Response({
                'status': 'error',
                'message': 'CPF já cadastrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        candidato = CandidatoService.criar(dados)
        if candidato:
            return Response({
                'status': 'success',
                'data': candidato
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'message': 'Erro ao criar candidato'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def atualizar_candidato(request, id):
    """Atualiza um candidato"""
    try:
        dados = request.data
        candidato = CandidatoService.atualizar(id, dados)
        if candidato:
            return Response({
                'status': 'success',
                'data': candidato
            })
        return Response({
            'status': 'error',
            'message': 'Candidato não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deletar_candidato(request, id):
    """Deleta um candidato"""
    try:
        if CandidatoService.deletar(id):
            return Response({
                'status': 'success',
                'message': 'Candidato deletado com sucesso'
            })
        return Response({
            'status': 'error',
            'message': 'Candidato não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
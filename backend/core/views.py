from django.http import JsonResponse, FileResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os

def home(request):
    """Página inicial - Serve o frontend"""
    try:
        return render(request, 'index.html')
    except:
        # Se o arquivo não existir, retorna JSON
        return JsonResponse({
            'status': 'online',
            'message': 'API do Sistema de Automação do Processo Seletivo CEDERJ',
            'version': '1.0.0',
            'endpoints': {
                'admin': '/admin/',
                'candidatos': {
                    'listar': '/api/candidatos/',
                    'buscar': '/api/candidatos/<id>/',
                    'criar': '/api/candidatos/criar/',
                    'atualizar': '/api/candidatos/<id>/atualizar/',
                    'deletar': '/api/candidatos/<id>/deletar/',
                }
            },
            'docs': 'Acesse /admin/ para o painel administrativo'
        })
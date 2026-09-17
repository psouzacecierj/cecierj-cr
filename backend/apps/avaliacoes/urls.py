from django.urls import path
from . import views

urlpatterns = [
    # Avaliações
    path('lancar/', views.lancar_avaliacao, name='lancar_avaliacao'),
    path('disciplina/<int:disciplina_id>/', views.listar_avaliacoes_disciplina, name='listar_avaliacoes_disciplina'),
    path('classificar/<int:disciplina_id>/', views.classificar_disciplina, name='classificar_disciplina'),
    path('salvar-classificacao/<int:disciplina_id>/', views.salvar_classificacao, name='salvar_classificacao'),
    path('processar-tudo/', views.processar_todas_disciplinas, name='processar_todas_disciplinas'),
    
    # Resultados (por grupo)
    path('resultado/grupo/<int:grupo_id>/', views.resultado_grupo, name='resultado_grupo'),
    path('resultado/geral/', views.resultado_geral, name='resultado_geral'),
    path('recalcular-classificacao/<int:grupo_id>/', views.recalcular_classificacao, name='recalcular_classificacao'),
]
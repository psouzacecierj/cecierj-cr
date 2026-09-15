from django.urls import path
from . import views

urlpatterns = [
    path('lancar/', views.lancar_avaliacao, name='lancar_avaliacao'),
    path('disciplina/<int:disciplina_id>/', views.listar_avaliacoes_disciplina, name='listar_avaliacoes_disciplina'),
    path('classificar/<int:disciplina_id>/', views.classificar_disciplina, name='classificar_disciplina'),
    path('salvar-classificacao/<int:disciplina_id>/', views.salvar_classificacao, name='salvar_classificacao'),
]
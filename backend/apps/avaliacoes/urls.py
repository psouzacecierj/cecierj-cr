from django.urls import path
from . import views

urlpatterns = [
    path('lancar/', views.lancar_avaliacao, name='lancar_avaliacao'),
    path('disciplina/<int:disciplina_id>/', views.listar_avaliacoes_disciplina, name='listar_avaliacoes_disciplina'),
]
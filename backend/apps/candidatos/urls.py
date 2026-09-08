from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_candidatos, name='listar_candidatos'),
    path('<int:id>/', views.buscar_candidato, name='buscar_candidato'),
    path('criar/', views.criar_candidato, name='criar_candidato'),
    path('<int:id>/atualizar/', views.atualizar_candidato, name='atualizar_candidato'),
    path('<int:id>/deletar/', views.deletar_candidato, name='deletar_candidato'),
]
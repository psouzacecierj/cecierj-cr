from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_avaliacoes, name='listar_avaliacoes'),
    path('criar/', views.criar_avaliacao, name='criar_avaliacao'),
]
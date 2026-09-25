from django.urls import path
from . import views

urlpatterns = [
    path('cr/grupo/<int:grupo_id>/', views.listar_cr_grupo, name='listar_cr_grupo'),
    path('cr/grupo/<int:grupo_id>/proxima/', views.proxima_convocacao, name='proxima_convocacao'),
    path('cr/convocar/<int:avaliacao_id>/', views.convocar, name='convocar'),
    path('cr/recusar/<int:avaliacao_id>/', views.registrar_recusa, name='registrar_recusa'),
    path('cr/atualizar/<int:avaliacao_id>/', views.atualizar_status, name='atualizar_status'),
    path('cr/kpis/', views.kpis, name='kpis'),
    path('cr/avisos-validade/', views.avisos_validade, name='avisos_validade'),  
]
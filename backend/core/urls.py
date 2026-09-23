from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('convocacoes/', views.convocacoes, name='convocacoes'),  # ← NOVO
    path('admin/', admin.site.urls),
    path('api/candidatos/', include('apps.candidatos.urls')),
    path('api/avaliacoes/', include('apps.avaliacoes.urls')),
    path('api/convocacoes/', include('apps.convocacoes.urls')),
]
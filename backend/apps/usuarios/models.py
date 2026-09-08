from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    """Perfil estendido do usuário"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    curso = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.cargo or 'Sem cargo'}"
    
    class Meta:
        db_table = 'perfil_usuarios'
        managed = False
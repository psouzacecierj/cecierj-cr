from django.db import models
from django.contrib.auth.models import User

class Candidato(models.Model):
    """Modelo para candidatos (sincronizado com Supabase)"""
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    endereco = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.nome_completo
    
    class Meta:
        db_table = 'candidatos'
        managed = False  # Não criar no SQLite, usar o Supabase
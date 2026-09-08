from django.db import models

class Recurso(models.Model):
    """Modelo para recursos"""
    inscricao_id = models.IntegerField()
    tipo = models.CharField(max_length=50)
    descricao = models.TextField()
    status = models.CharField(max_length=20, default='pendente')
    parecer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recursos'
        managed = False
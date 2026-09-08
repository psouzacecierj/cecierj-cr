from django.db import models

class Convocacao(models.Model):
    """Modelo para convocações"""
    inscricao_id = models.IntegerField()
    data_limite_resposta = models.DateTimeField()
    status = models.CharField(max_length=20, default='pendente')
    email_enviado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'convocacoes'
        managed = False
from django.db import models

class Importacao(models.Model):
    """Histórico de importações"""
    arquivo = models.CharField(max_length=255)
    data_importacao = models.DateTimeField(auto_now_add=True)
    registros_importados = models.IntegerField()
    status = models.CharField(max_length=50)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'importacoes'
        managed = False
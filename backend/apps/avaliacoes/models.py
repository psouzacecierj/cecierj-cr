from django.db import models

class Avaliacao(models.Model):
    """Modelo para avaliações"""
    inscricao_id = models.IntegerField()
    nota_ac = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nota_pp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nota_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    classificacao = models.IntegerField(null=True, blank=True)
    parecer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'avaliacoes'
        managed = False
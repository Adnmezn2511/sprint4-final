from django.db import models

class GraphHistory(models.Model):
    user = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    graph_json = models.JSONField(blank=True, null=True)
    parameters = models.JSONField(blank=True, null=True)
    result_folder = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Graph généré le {self.created_at:%d/%m/%Y}"

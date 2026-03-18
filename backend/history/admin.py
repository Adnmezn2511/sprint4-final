from django.contrib import admin
from .models import GraphHistory

class GraphHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'result_folder', 'created_at')  # Ajoute l'ID dans l'interface admin

admin.site.register(GraphHistory, GraphHistoryAdmin)

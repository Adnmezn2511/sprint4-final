from rest_framework import serializers
from .models import GraphHistory

class GraphHistorySerializer(serializers.ModelSerializer):
    # Format ISO 8601 pour une meilleure compatibilité JavaScript
    created_at = serializers.DateTimeField(format="iso-8601")
    
    class Meta:
        model = GraphHistory
        fields = ['id', 'user', 'graph_json','title', 'created_at', 'parameters']

from rest_framework import serializers
from rest_framework.templatetags.rest_framework import items

from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']





from rest_framework import serializers

from .models import Item, Question


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "title", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class GameQuestionSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="text")

    class Meta:
        model = Question
        fields = ["id", "question_text", "correct_answer"]

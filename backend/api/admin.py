from api.models import Category, Question
from django.contrib import admin


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "category", "pegi_rating", "created_at"]
    list_filter = ["category", "pegi_rating"]
    search_fields = ["text", "translation_text"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]

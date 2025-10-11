from django.db import models


class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name
    
class Question(models.Model):
    text = models.CharField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    correct_answer = models.CharField(max_length=500)
    translation_text = models.TextField(blank=True, null=True)
    pegi_rating = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]
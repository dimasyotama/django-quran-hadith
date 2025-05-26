# hadith_app/models.py
from django.db import models

class HadithBook(models.Model):
    api_id = models.CharField(max_length=50, unique=True) # e.g., "bukhari"
    name = models.CharField(max_length=100) # e.g., Sahih Bukhari
    available_hadiths = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Hadith(models.Model):
    book = models.ForeignKey(HadithBook, related_name='hadiths', on_delete=models.CASCADE)
    number = models.IntegerField()
    arab = models.TextField()
    id_translation = models.TextField() # Indonesian translation

    def __str__(self):
        return f"{self.book.name} - {self.number}"

    class Meta:
        unique_together = ('book', 'number')
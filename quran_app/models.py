from django.db import models

class Surah(models.Model):
    number = models.IntegerField(unique=True)
    name_simple = models.CharField(max_length=100) # e.g., Al-Fatihah
    name_arabic = models.CharField(max_length=100)
    revelation_place = models.CharField(max_length=20) # Mecca or Medina
    verses_count = models.IntegerField()

    def __str__(self):
        return f"{self.number}. {self.name_simple}"

class Ayah(models.Model):
    surah = models.ForeignKey(Surah, related_name='ayahs', on_delete=models.CASCADE)
    number_in_surah = models.IntegerField()
    text_uthmani = models.TextField()
    translation_id = models.TextField() # Indonesian translation

    def __str__(self):
        return f"Surah {self.surah.number}, Ayah {self.number_in_surah}"

    class Meta:
        unique_together = ('surah', 'number_in_surah')
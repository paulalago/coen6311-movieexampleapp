# moviemanager/movies/models/genre.py
from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'GENRES'
        ordering = ['name']
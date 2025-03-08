# moviemanager/movies/models/director.py
from django.db import models

class Director(models.Model):
    name = models.CharField(max_length=100)
    year_of_birth = models.IntegerField()
    place_of_birth = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'DIRECTORS'
        ordering = ['name']
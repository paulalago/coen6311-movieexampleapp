from django.db import models
from django.urls import reverse
from .director import Director
from .genre import Genre


# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=100)
    year = models.IntegerField()
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True)
    director = models.ForeignKey(Director, on_delete=models.CASCADE, null=True)
    plot = models.TextField()
    poster = models.URLField()
    imdb_rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('movie-detail', args=[str(self.id)])

    #write code to name the database table
    class Meta:
        db_table = 'MOVIES'
        ordering = ['title']

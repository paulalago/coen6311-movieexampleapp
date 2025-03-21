# Generated by Django 5.1.3 on 2024-12-17 23:04

from django.db import migrations


def add_default_genres(apps, schema_editor):
    Genre = apps.get_model('movies', 'Genre')
    default_genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'Western', 'Animation', 'Documentary']
    Genre.objects.bulk_create([Genre(name=genre) for genre in default_genres])

class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default_genres),
    ]

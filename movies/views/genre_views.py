from django.views import generic
from movies.models.genre import Genre

class GenreListView(generic.ListView):
    model = Genre
    paginate_by = 10
    template_name = 'genres/genre_list.html'


from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import Http404
from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response

from movies.models.movie import Movie
from movies.serializers.movie_serializer import MovieSerializer



class MovieListCreateView(views.APIView):
    """
        List all movies, or create a new one.
    """
    def get(self, request, format=None):
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovieDetailUpdateDeleteView(views.APIView):
    """
        Retrieve, update or delete a movie instance.
    """
    def get_object(self, pk):
        try:
            return Movie.objects.get(pk=pk)
        except Movie.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_UPDATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        movie = self.get_object(pk)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MovieCreateView(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class MovieListView(generic.ListView):
    model = Movie
    paginate_by = 10

class MovieDetailView(generic.DetailView):
    model = Movie

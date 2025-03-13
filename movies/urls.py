from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='chat'),
    path('new_session', views.new_session, name='new_session'),
    path('list', views.MovieListView.as_view(), name='movielist'),
    path('movie/<int:pk>/', views.MovieDetailView.as_view(), name='movie-detail-1'),
    path('api/create/', views.MovieCreateView.as_view(), name='movie-create'),
    path('api/movies/', views.MovieListCreateView.as_view(), name='movie-list-create'),
    path('api/movies/<int:pk>/', views.MovieDetailUpdateDeleteView.as_view(), name='movie-detail'),
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
]

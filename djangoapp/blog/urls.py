from django.urls import path

from blog import views

urlpatterns = [
    path("posts/", views.PostListView.as_view(), name="blogpost-list"),
    path("posts/<int:pk>", views.PostDetailView.as_view(), name="blogpost-detail"),
]

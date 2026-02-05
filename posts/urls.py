from django.urls import path
from .views import (
    PostListView,
    PostCreateView,
    PostDetailView,
    vote_post,
    user_post_votes
)

app_name = 'posts'

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:post_id>/vote/', vote_post, name='vote-post'),
    path('votes/', user_post_votes, name='user-post-votes'),
]

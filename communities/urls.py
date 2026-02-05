from django.urls import path
from .views import (
    CommunityListCreateView,
    CommunityDetailView,
    UserCommunitiesView,
    join_community,
    leave_community
)

app_name = 'communities'

urlpatterns = [
    path('', CommunityListCreateView.as_view(), name='community-list'),
    path('<str:id>/', CommunityDetailView.as_view(), name='community-detail'),
    path('user/snippets/', UserCommunitiesView.as_view(), name='user-communities'),
    path('<str:community_id>/join/', join_community, name='community-join'),
    path('<str:community_id>/leave/', leave_community, name='community-leave'),
]

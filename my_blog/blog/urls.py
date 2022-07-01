from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('', views.home, name='homepage'),
    path('<slug:post>/', views.post_info, name='post_info'),
    path('<int:post_id>/share/', views.share, name='share'),
    path('login', views.login, name='login'),
    path('tag/<slug:tag_slug>/', views.home, name='post_list_by_tag'),
    path('logout', views.logout, name='logout'),
]

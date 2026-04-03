# In myproject/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # User/Auth Paths
    path('', views.home_view, name='home'),      
    path('index/', views.index, name='index'),  
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('history/', views.history_view, name='history'), 
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'), 
    path('category/<str:category_name>/', views.news_by_category, name='news_by_category'),
]
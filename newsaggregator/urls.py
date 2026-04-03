from django.contrib import admin
from django.urls import path
from myproject import views
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myproject.urls')),
    # User/Auth Paths
    path('', views.home_view, name='home'),      # home.html (Landing page)
    path('index/', views.index, name='index'),   # index.html (Main news page)
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('history/', views.history_view, name='history'), 
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    # News Paths
     path('bookmark/toggle/<int:pk>/', views.bookmark_toggle, name='bookmark_toggle'),

    # Path to display the list of bookmarked articles
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    # ✅ Use the standard 'pk' (primary key) for the detail view
    path('news/<int:pk>/', views.news_detail, name='news_detail'), 
    path('category/<str:category_name>/', views.news_by_category, name='news_by_category'),
    # ✅ This URL is for category filteringth('new/<str:category>/', views.news_by_category, name='news_by_category')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
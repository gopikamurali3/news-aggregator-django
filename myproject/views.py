from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q # Import Q for complex lookups
from .models import News 
from django.utils import timezone
from django.urls import reverse
import datetime
from django.http import JsonResponse  
from django.contrib.auth.decorators import login_required
from .models import News, ReadHistory 
from django.http import JsonResponse
from .models import News, Bookmark 
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
# --- AUTHENTICATION VIEWS ---

# REMOVED: get_user_country_code is no longer needed

@login_required
@require_POST # Ensure only POST requests are allowed
def bookmark_toggle(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    article = get_object_or_404(News, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, article=article)

    if not created:
        # Already bookmarked → remove it
        bookmark.delete()
        bookmarked = False
        message = f"Bookmark removed from '{article.title[:30]}...'"
    else:
        # Newly bookmarked
        bookmarked = True
        message = f"Article bookmarked: '{article.title[:30]}...'"

    return JsonResponse({'bookmarked': bookmarked, 'message': message})

@login_required
def bookmarks_view(request):
    """
    Displays the list of articles the logged-in user has bookmarked.
    """
    # Fetch all Bookmark entries for the current user, ordered by most recent bookmark time.
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('article').order_by('-bookmarked_at')
    
    context = {
        'bookmarks_list': bookmarks,
    }
    
    # You must have a bookmarks.html template for this to work.
    return render(request, 'bookmarks.html', context)

@login_required
def history_view(request):
    """
    Shows the logged-in user's reading history.
    """
    # Use the @login_required decorator instead of this manual check if possible,
    # but the manual check is fine if you're not using decorators elsewhere.
    if not request.user.is_authenticated:
        return redirect('login')

    # 1. Fetch user’s reading history, newest first, and store in 'history'
    history = ReadHistory.objects.filter(user=request.user).select_related('article').order_by('-read_at')
    
    # 2. Correctly use the 'history' variable to populate the 'history_list' context key
    context = {
        'history_list': history, # <-- FIXED: Passing 'history' to the key 'history_list'
    }
    
    return render(request, 'history.html', context)
def home_view(request):
    """
    Renders the home.html landing page.
    If the user is already logged in, redirect them to the index page.
    """
    if request.user.is_authenticated:
        # If the user is logged in, skip the home page and go to the news feed
        return redirect('index') 
        
    # If the user is NOT logged in, show the home.html landing page
    return render(request, 'home.html')

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index") 
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})

def signup_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            error = "Passwords do not match"
        elif User.objects.filter(username=username).exists():
            error = "Username already taken"
        else:
            User.objects.create_user(username=username, password=password)
            return redirect("login") 

    return render(request, "signup.html", {"error": error})

def logout_view(request):
    logout(request)
    return redirect("home") 

# --- NEWS VIEWS ---

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q # Import Q for complex lookups
from .models import News 

# --- AUTHENTICATION VIEWS ---

# REMOVED: get_user_country_code is no longer needed

def home_view(request):
    """
    Renders the home.html landing page.
    If the user is already logged in, redirect them to the index page.
    """
    if request.user.is_authenticated:
        # If the user is logged in, skip the home page and go to the news feed
        return redirect('index') 
        
    # If the user is NOT logged in, show the home.html landing page
    return render(request, 'home.html')

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index") 
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})

def signup_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            error = "Passwords do not match"
        elif User.objects.filter(username=username).exists():
            error = "Username already taken"
        else:
            User.objects.create_user(username=username, password=password)
            return redirect("login") 

    return render(request, "signup.html", {"error": error})

def logout_view(request):
    logout(request)
    return redirect("home") 

# --- NEWS VIEWS ---

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q # Import Q for complex lookups
from .models import News 

# --- AUTHENTICATION VIEWS ---

def home_view(request):
    """
    Renders the home.html landing page.
    If the user is already logged in, redirect them to the index page.
    """
    if request.user.is_authenticated:
        return redirect('index') 
    return render(request, 'home.html')

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index") 
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})

def signup_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            error = "Passwords do not match"
        elif User.objects.filter(username=username).exists():
            error = "Username already taken"
        else:
            User.objects.create_user(username=username, password=password)
            return redirect("login") 

    return render(request, "signup.html", {"error": error})

def logout_view(request):
    logout(request)
    return redirect("home") 

# --- NEWS VIEWS ---


# In myproject/views.py

# In myproject/views.py

# In myproject/views.py

# In myproject/views.py
# views.py
from django.shortcuts import render
from .models import News, Bookmark

def category_view(request, category_name):
    news_items = News.objects.filter(category=category_name)

    if request.user.is_authenticated:
        bookmarked_pks = Bookmark.objects.filter(user=request.user).values_list('article_id', flat=True)
    else:
        bookmarked_pks = []

    return render(request, 'category.html', {
        'news_items': news_items,
        'bookmarked_pks': bookmarked_pks,
        'category_name': category_name
    })



def index(request):
    # 1. Fetch latest news from the general category for the slideshow
    latest_news = News.objects.all().order_by('-published_at')[:5]

    # 2. Fetch specific categories for the main feed
    india_news = News.objects.filter(category__iexact='india-general').order_by('-published_at')[:10]
    global_business_news = News.objects.filter(category__iexact='global-business').order_by('-published_at')[:10]
    
    # Combine the main news feed items (used in your template as 'news_items')
    news_items = list(india_news) + list(global_business_news)

    return render(request, "index.html", {
        "latest_news": latest_news,
        "news_items": news_items,   
        # Note: Your template structure only uses 'latest_news' and 'news_items'
    })

# In myproject/views.py (within news_by_category function)

# In myproject/views.py (The final structure for news_by_category)

def news_by_category(request, category_name):
    url_category = category_name.strip().lower()
    
    # 1. Map simple URL slug to the complex database category name
    # Based on your shell output: ['science', 'bbc', 'cnn', 'global-business']
    category_map = {
        'business': 'global-business',
        'science': 'science', 
        # Add the remaining categories based on your database contents or your API_SOURCES
        'politics': 'bbc',      # Mapping your 'Politics' button to 'bbc' data
        'entertainment': 'cnn', # Mapping 'Entertainment' button to 'cnn' data (example)
        'sports': 'cnn',        # Mapping 'Sports' to 'cnn' (example)
        'fashion': 'cnn',       # Mapping 'Fashion' to 'cnn' (example)
    }
    news_items = News.objects.filter(category=category_name).order_by('-published_at')[:20]

    bookmarked_pks = []
    if request.user.is_authenticated:
        # 1. Get the PKs of articles currently displayed that the user has bookmarked
        bookmarked_pks = Bookmark.objects.filter(
            user=request.user, 
            article__in=news_items
        ).values_list('article__pk', flat=True)
    
    context = {
        'news_items': news_items,
        'category_name': category_name.title(),
        'bookmarked_pks': list(bookmarked_pks), # <-- THIS MUST BE PRESENT
    }
    
    # Use the mapped value, or fall back to the URL name if no map exists
    db_category_name = category_map.get(url_category, url_category)
    
    # 2. Filter using the name guaranteed to exist in the database
    news_items = News.objects.filter(category__iexact=db_category_name).order_by('-published_at')
    
    # 3. CRITICAL: Define the context dictionary
    context = {
        'news_items': news_items,
        # Format the category name for the page heading (e.g., 'global-business' -> 'Global Business')
        'category_name': url_category.title(),
    }
    
    # 4. Render the correct template
    return render(request, 'news_by_category.html', context)
def news_detail(request, pk):
    article = get_object_or_404(News, pk=pk)
    
    # History logging (Keep this correct)
    if request.user.is_authenticated:
        ReadHistory.objects.update_or_create(
            user=request.user, 
            article=article,
            defaults={'read_at': timezone.now()}
        )
    
    # --- DYNAMIC BACK BUTTON LOGIC ---
    # 1. Default back URL is the current article's category list
    back_url = reverse('news_by_category', args=[article.category])
    back_text = f"← Back to {article.category} News"
    
    # 2. Check the referrer (where the user came from)
    referrer = request.META.get('HTTP_REFERER')
    
    # 3. If the user came from the history page, override the back link
    if referrer and reverse('history') in referrer:
        back_url = reverse('history')
        back_text = "← Back to History"
        
    # 4. If the user came from the main index, override the back link
    elif referrer and reverse('index') in referrer:
        back_url = reverse('index')
        back_text = "← Back to Home"
        
    # --- END DYNAMIC BACK BUTTON LOGIC ---

    context = {
        'article': article,
        'back_url': back_url,   # Pass the dynamic URL
        'back_text': back_text, # Pass the dynamic Text
    }
    
    return render(request, "news_detail.html", context)
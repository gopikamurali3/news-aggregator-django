# In myproject/management/commands/fetch_news.py

from django.core.management.base import BaseCommand
import requests
from django.conf import settings
from myproject.models import News
from datetime import datetime
import os
import uuid
import re 

class Command(BaseCommand):
    help = "Fetch news using a dedicated News API (e.g., NewsAPI) and store content/images locally."

    # --- CONSTANTS ---
    API_SOURCES = {
        # Using country codes for specific sections
        "INDIA_GENERAL": {"endpoint": "top-headlines", "country": "in", "category": "general"},
        "GLOBAL_BUSINESS": {"endpoint": "top-headlines", "country": "us", "category": "business"},
        "GLOBAL_SCIENCE": {"endpoint": "top-headlines", "country": "gb", "category": "science"},
        
        # Using the 'everything' endpoint for specific topics (less structure than 'top-headlines')
        # We will use these for the 'bbc' and 'cnn' categories that were present in your database
        "BBC_NEWS": {"endpoint": "everything", "sources": "bbc-news", "language": "en"},
        "CNN_NEWS": {"endpoint": "everything", "sources": "cnn", "language": "en"},
    }
    
    # Base URL for NewsAPI
    NEWS_API_URL = "https://newsapi.org/v2/"

    # --- ADD ARGUMENTS ---
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-old-data',
            action='store_true',
            help='Clear all existing news items before fetching new ones.',
        )

    # --- HELPER FUNCTION: IMAGE DOWNLOAD ---
    def download_and_save_image(self, image_url):
        if not image_url:
            return None
        
        # Strip potential query parameters
        clean_url = image_url.split('?')[0] 
        
        try:
            # Use a User-Agent header to mimic a browser, helping avoid some blocks
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            image_response = requests.get(clean_url, stream=True, timeout=10, headers=headers) 
            image_response.raise_for_status()
            
            # Extract extension safely
            extension = os.path.splitext(clean_url)[-1].lower()
            if extension not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                extension = '.jpg' # Default to jpg if extension is weird or missing
                
            filename = f"img_{uuid.uuid4()}{extension}"
            # Django uses os.path.join for path handling
            relative_path = os.path.join('news_images', filename)
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'news_images'), exist_ok=True)
            
            with open(full_path, 'wb') as f:
                f.write(image_response.content)
                
            # Return the URL path for Django to use in the template
            # .replace('\\', '/') ensures correct path separators on all OS
            return os.path.join(settings.MEDIA_URL, relative_path).replace('\\', '/')
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to download image from: {clean_url}. Error: {e}"))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Generic error processing image: {e}"))
            return None
            
    # --- CRITICALLY MOVED API FETCHER FUNCTION INSIDE THE CLASS ---
    def fetch_news_from_api(self, source_name, params, existing_titles, new_news_items):
        self.stdout.write(self.style.NOTICE(f"--- Starting API fetch for {source_name} ---"))
        
        # Build URL and parameters
        url = self.NEWS_API_URL + params.pop('endpoint', 'top-headlines')
        
        api_params = {
            'apiKey': settings.NEWS_API_KEY,
            'pageSize': 20, 
            **params
        }

        try:
            response = requests.get(url, params=api_params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Use the source_name for the category field (e.g., 'india-general' -> 'india-general')
            category_name = source_name.lower().replace('_', '-') 
            source_type = 'API' 
            
            for article in data.get('articles', []):
                title = article.get('title')
                link = article.get('url')
                external_image_url = article.get('urlToImage') 
                description = article.get('description', '')
                content = article.get('content') 
                published_at_str = article.get('publishedAt')
                
                if not title or title in existing_titles or title == "[Removed]":
                    continue
                
                # Date Parsing (NewsAPI uses ISO format)
                try:
                    published_at = datetime.strptime(published_at_str[:19], '%Y-%m-%dT%H:%M:%S')
                except (ValueError, TypeError):
                    published_at = datetime.now()
                
                # 1. Attempt to download image locally
                local_image_path = self.download_and_save_image(external_image_url)
                
                # 2. IMAGE FALLBACK LOGIC: If download fails, use the external URL
                final_image_url = local_image_path if local_image_path else external_image_url
                
                # Clean HTML from description and content
                cleaned_description = re.sub('<[^>]*>', '', description)
                cleaned_content = re.sub('<[^>]*>', '', content or cleaned_description)
                
                new_news_items.append(
                    News(
                        title=title,
                        description=cleaned_description[:300], 
                        content=cleaned_content,
                        category=category_name,
                        link=link,
                        image_url=final_image_url, 
                        published_at=published_at,
                        source_type=source_type 
                    )
                )
                existing_titles.add(title)
                self.stdout.write(f"Prepared to add ({category_name}): {title}")
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ API fetch error for {source_name}: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ General error processing API data for {source_name}: {e}"))
            
    # --- MAIN HANDLE METHOD ---
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting news aggregation via API..."))
        
        # Clear old data if the option was passed
        if options.get('clear_old_data'):
            self.stdout.write(self.style.WARNING("Clearing old news data..."))
            News.objects.all().delete()
        
        existing_titles = set(News.objects.values_list('title', flat=True))
        new_news_items = []
        
        # 1. Iterate through API Sources
        for source_name, params in self.API_SOURCES.items():
            # Pass a copy of params to avoid modifying the original dictionary in the loop
            self.fetch_news_from_api(source_name, params.copy(), existing_titles, new_news_items)

        # 2. Bulk-save the new items for performance
        count = len(new_news_items)
        # Note: bulk_create works best without a primary key conflict check, 
        # but the title check above prevents most duplicates.
        News.objects.bulk_create(new_news_items) 
        
        self.stdout.write(self.style.SUCCESS(f"✅ Successfully added {count} new news items."))
        self.stdout.write(self.style.SUCCESS("News aggregation complete."))
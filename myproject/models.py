from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse  
class News(models.Model):
    SOURCE_CHOICES = [
        ('INDIA', 'India News'),
        ('GLOBAL', 'Global News'),
    ]

    # --- Main Fields ---
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100)
    link = models.URLField(null=True, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # --- Source Type (India / Global) ---
    source_type = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default='GLOBAL'
    )
    def get_absolute_url(self):
        # This returns the URL for the news detail page
        return reverse('news_detail', args=[str(self.pk)])
    def __str__(self):
        return self.title

    @property
    def readmore(self):
        """Returns external link for 'Read original article'"""
        return self.link

class ReadHistory(models.Model):
    # Links the history entry to a specific authenticated user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Links the history entry to the article that was read
    article = models.ForeignKey(News, on_delete=models.CASCADE)
    
    # Records the exact time the article was read (for ordering/recency)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a user from having two history entries for the exact same article 
        # (though read_at will make them unique, this is often good practice)
        unique_together = ('user', 'article')
        verbose_name_plural = " History" 
        ordering = ['-read_at'] # Default order is newest first

    def __str__(self):
        return f"{self.user.username} read {self.article.title[:20]}..."
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey('News', on_delete=models.CASCADE)
    bookmarked_at = models.DateTimeField(auto_now_add=True) # Sets time on creation

    class Meta:
        # Prevents a user from bookmarking the same article twice
        unique_together = ('user', 'article')
        verbose_name_plural = "Bookmarks"
        ordering = ['-bookmarked_at']

    def __str__(self):
        return f"{self.user.username} bookmarked {self.article.title[:20]}"

from django.db import models
import uuid

class DocumentationItem(models.Model):
    CATEGORY_CHOICES = (
        ('quick_start', 'Quick Start'),
        ('video_tutorial', 'Video Tutorial'),
        ('module_guide', 'Module Guide'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='quick_start')
    
    url = models.URLField(blank=True, null=True, help_text="External link to documentation or video")
    thumbnail_url = models.URLField(blank=True, null=True, help_text="Thumbnail image URL for video")
    video_file = models.FileField(upload_to='documentation_videos/', blank=True, null=True, help_text="Upload local video file")
    
    order = models.IntegerField(default=0, help_text="Order in which it appears in the side panel")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'order', '-created_at']

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"

class Notification(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    link_url = models.CharField(max_length=500, blank=True, null=True, help_text="Frontend route to navigate to")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.user.email} - {self.title}"

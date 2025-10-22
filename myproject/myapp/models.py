from django.db import models

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('music', 'Arts and Music'),
        ('industrial', 'Industrial Engineering'),
        ('health', 'Health & Wellness'),
        ('education', 'Education & Training'),
        ('travel', 'Travel & Tourism'),
        ('sports', 'Sports & Travel'),
    ]
    
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='music')  # ✅ ADD THIS
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def __str__(self):
        return self.title
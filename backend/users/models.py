from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    ROLE_CHOICES = [
        ('contributor', 'Contributor'),
        ('validator', 'Validator'),
        ('admin', 'Admin'),
        ('researcher', 'Researcher'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='contributor')
    wallet_address = models.CharField(max_length=42, blank=True, null=True, unique=True)
    wallet_signature = models.TextField(blank=True, null=True)
    wallet_verified = models.BooleanField(default=False)
    balance_usdc = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    firebase_uid = models.CharField(max_length=128, blank=True, null=True, unique=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    total_contributions = models.IntegerField(default=0)
    total_validations = models.IntegerField(default=0)
    total_earnings_usdc = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    streak_days = models.IntegerField(default=0)
    last_contribution_date = models.DateField(blank=True, null=True)
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    is_email_verified = models.BooleanField(default=False)
    magic_link_token = models.CharField(max_length=255, blank=True, null=True)
    magic_link_expires = models.DateTimeField(blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default='en')
    consent_given = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet_address']),
            models.Index(fields=['firebase_uid']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def update_streak(self):
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        if self.last_contribution_date:
            days_diff = (today - self.last_contribution_date).days
            
            if days_diff == 0:
                return
            elif days_diff == 1:
                self.streak_days += 1
            else:
                self.streak_days = 1
        else:
            self.streak_days = 1
        
        self.last_contribution_date = today
        self.save(update_fields=['streak_days', 'last_contribution_date'])
    
    def add_points(self, points):
        self.points += points
        self.level = (self.points // 100) + 1
        self.save(update_fields=['points', 'level'])
    
    def get_initials(self):
        if self.nickname:
            parts = self.nickname.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[1][0]}".upper()
            return self.nickname[:2].upper()
        elif self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()


class Badge(models.Model):
    BADGE_TYPES = [
        ('first_contribution', 'First Contribution'),
        ('streak_7', '7 Day Streak'),
        ('streak_30', '30 Day Streak'),
        ('contributor_100', '100 Contributions'),
        ('validator_100', '100 Validations'),
        ('earnings_10', '$10 Earned'),
        ('earnings_100', '$100 Earned'),
        ('quality_expert', 'Quality Expert'),
        ('early_adopter', 'Early Adopter'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    badge_type = models.CharField(max_length=30, choices=BADGE_TYPES, unique=True)
    description = models.TextField()
    icon_url = models.URLField(blank=True, null=True)
    points_reward = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'badges'
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

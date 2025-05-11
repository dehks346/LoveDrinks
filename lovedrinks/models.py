from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.db.models.functions import Coalesce
from django.db.models import FloatField
from django.db.models.functions import Cast
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import os


class drinks(models.Model):
    drink_id = models.AutoField(primary_key=True)
    drink_name = models.CharField(max_length=255)
    drink_type = models.CharField(max_length=255)
    drink_image = models.ImageField(upload_to='drinks/')
    drink_abv = models.DecimalField(max_digits=5, decimal_places=2)
    drink_producer = models.CharField(max_length=255)
    drink_tasting_notes = models.TextField()
    drink_rating = models.DecimalField(max_digits=3, decimal_places=2)


    class Meta:
        verbose_name = 'Drink'
        verbose_name_plural = 'Drinks'

    def __str__(self):
        return self.drink_name

    def update_average_rating(self):
        """Calculate and update the average rating for this drink, taking into account user averages"""
        from django.db.models import Avg, FloatField
        from django.db.models.functions import Cast

        # First get all unique users who rated this drink
        users = DrinkLog.objects.filter(drink_id=self).values('user_id').distinct()
        
        # Calculate average for each user
        user_averages = []
        for user in users:
            user_avg = DrinkLog.objects.filter(
                drink_id=self,
                user_id=user['user_id']
            ).aggregate(
                avg=Avg(Cast('rating', FloatField()))
            )['avg']
            if user_avg is not None:
                user_averages.append(user_avg)
        
        # Calculate final average
        if user_averages:
            self.drink_rating = sum(user_averages) / len(user_averages)
        else:
            self.drink_rating = 0
        
        self.save()

class DrinkLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    drink_id = models.ForeignKey(drinks, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    logged_at = models.DateTimeField(auto_now_add=True)

    @property
    def drink_name(self):
        return self.drink_id.drink_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.drink_id.update_average_rating()

    def delete(self, *args, **kwargs):
        drink = self.drink_id
        super().delete(*args, **kwargs)
        drink.update_average_rating()

    class Meta:
        verbose_name = 'Drink Log'
        verbose_name_plural = 'Drink Logs'



class follows(models.Model):
    following_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'


class user_stats(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    top_drink_1 = models.ForeignKey(drinks, on_delete=models.CASCADE, related_name='top_drink_1', null=True, blank=True)
    top_drink_2 = models.ForeignKey(drinks, on_delete=models.CASCADE, related_name='top_drink_2', null=True, blank=True)
    top_drink_3 = models.ForeignKey(drinks, on_delete=models.CASCADE, related_name='top_drink_3', null=True, blank=True)
    top_drink_4 = models.ForeignKey(drinks, on_delete=models.CASCADE, related_name='top_drink_4', null=True, blank=True)
    top_drink_5 = models.ForeignKey(drinks, on_delete=models.CASCADE, related_name='top_drink_5', null=True, blank=True)

    class Meta:
        verbose_name = 'User Stat'
        verbose_name_plural = 'User Stats'



class drink_trending(models.Model):
    drink_id = models.ForeignKey(drinks, on_delete=models.CASCADE)
    trending_score = models.IntegerField()
    trending_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Drink Trending'
        verbose_name_plural = 'Drink Trending'


def validate_file_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB limit
        raise ValidationError("The maximum file size that can be uploaded is 5MB")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_file_size
        ]
    )
    instagram_username = models.CharField(max_length=255, null=True, blank=True)
    twitter_username = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    @classmethod
    def get_or_create_profile(cls, user):
        profile, created = cls.objects.get_or_create(user=user)
        return profile



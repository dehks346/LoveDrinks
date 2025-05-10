from django.db import models
from django.contrib.auth.models import User


class drinks(models.Model):
    drink_id = models.AutoField(primary_key=True)
    drink_name = models.CharField(max_length=255)
    drink_type = models.CharField(max_length=255)
    drink_image = models.ImageField(upload_to='drinks/')
    drink_abv = models.DecimalField(max_digits=5, decimal_places=2)
    drink_producer = models.CharField(max_length=255)
    drink_tasting_notes = models.TextField()


    class Meta:
        verbose_name = 'Drink'
        verbose_name_plural = 'Drinks'

    def __str__(self):
        return self.drink_name

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
    total_logged = models.IntegerField()
    top_5_drinks = models.TextField()

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



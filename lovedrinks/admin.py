from django.contrib import admin
from .models import drinks, DrinkLog, follows, user_stats, drink_trending
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture')
    search_fields = ('user__username',)

@admin.register(drinks)
class DrinksAdmin(admin.ModelAdmin):
    list_display = ('drink_id', 'drink_name', 'drink_type', 'drink_producer', 'drink_abv', 'drink_rating')
    search_fields = ('drink_name', 'drink_type', 'drink_producer')
    list_filter = ('drink_type', 'drink_producer')

@admin.register(DrinkLog)
class DrinkLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'user_id', 'drink_id', 'rating', 'logged_at')
    list_filter = ('rating', 'logged_at')
    search_fields = ('user_id__username', 'drink_id__drink_name')

@admin.register(follows)
class FollowsAdmin(admin.ModelAdmin):
    list_display = ('following_id', 'followed_id', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('following_id__username', 'followed_id__username')

@admin.register(user_stats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'top_drink_1', 'top_drink_2', 'top_drink_3', 'top_drink_4', 'top_drink_5')
    search_fields = ('user_id__username',)


@admin.register(drink_trending)
class DrinkTrendingAdmin(admin.ModelAdmin):
    list_display = ('drink_id', 'trending_score', 'trending_date')
    list_filter = ('trending_date',)
    search_fields = ('drink_id__drink_name',)

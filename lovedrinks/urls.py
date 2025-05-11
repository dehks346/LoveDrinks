from django.urls import path, include
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('search/', views.searchpage, name='search'),
    path('profile/', views.profile, name='profile'),
    path('diary/<str:username>/', views.diary, name='diary'),
    path('log/<str:username>/<int:log_id>/', views.log, name='log'),
    path('search_drinks/', views.search_drinks, name='search_drinks'),
    path('search_users/', views.search_users, name='search_users'),
    path('profile/<str:username>/', views.other_profile, name='other_profile'),
    path('profilesettings/', views.profilesettings.as_view(), name='profilesettings'),
    path('following/<str:username>/', views.following, name='following'),
    path('followers/<str:username>/', views.followers, name='followers'),
    path('drink/<str:drink_name>/', views.drinkpage, name='drinkpage'),
    path('password/', views.CustomPasswordChangeView.as_view(), name='password'),
    path('top_drinks/', views.top_drinks, name='top_drinks'),
    path('drinks_tried/', views.drinks_tried, name='drinks_tried'),
    path('drink_reviews/<str:drink_name>/', views.drink_reviews, name='drink_reviews'),
]
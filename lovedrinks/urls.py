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
    path('profilesettings/', views.profilesettings, name='profilesettings'),
    path('following/', views.following, name='following'),
    path('followers/', views.followers, name='followers'),
    path('drink/<int:drink_id>/', views.drinkpage, name='drinkpage'),
]
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DrinkLogForm, SearchForm, CustomUserChangeForm, TopDrinkForm
from django.http import JsonResponse
from .models import drinks, DrinkLog, User, follows, user_stats, UserProfile
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Avg
import os




# Create your views here.
@login_required
def home(request):
    if request.method == 'POST':
        form = DrinkLogForm(request.POST)
        if form.is_valid():
            drink_log = form.save(commit=False)
            drink_log.user_id = request.user
            drink_log.save()
            return redirect('/home')
    else:
        form = DrinkLogForm()


    following_logs = DrinkLog.objects.filter(user_id__in=follows.objects.filter(following_id=request.user).values_list('followed_id', flat=True)).order_by('-logged_at')
    return render(request, 'lovedrinks/home.html', {
        'form': form, 
        'drink_logs': DrinkLog.objects.filter(user_id=request.user).order_by('-logged_at'),
        'following': following_logs
    })

@login_required
def searchpage(request):
    form = SearchForm(request.GET or None)
    search_type = request.GET.get('search_type', 'drinks')
    query = request.GET.get('query', '')
    
    context = {
        'form': form,
        'search_type': search_type,
        'query': query,
    }
    return render(request, 'lovedrinks/searchpage.html', context)

@login_required
def diary(request, username):
    user = User.objects.get(username=username)
    return render(request, 'lovedrinks/diary.html', {'user': user})

@login_required
def log(request, username, log_id):
    user = User.objects.get(username=username)
    log = DrinkLog.objects.get(log_id=log_id)
    
    if request.method == 'POST' and log.user_id == request.user:
        # Check which form was submitted
        if 'deleteLog' in request.POST:
            # Delete the log
            log.delete()
            return redirect('diary', username=username)
        else:
            # Edit the log
            rating = request.POST.get('rating')
            review = request.POST.get('review')
            
            log.rating = rating
            log.review = review
            log.save()
            
            return redirect('log', username=username, log_id=log_id)
    
    return render(request, 'lovedrinks/log.html', {'log': log})

@login_required
def profile(request):
    user = request.user
    #get the user stats for the user
    user_stats_obj = user_stats.objects.filter(user_id=user.id).first()
    
    # Get top drinks from the user_stats object
    top_drink_1 = user_stats_obj.top_drink_1 if user_stats_obj else None
    top_drink_2 = user_stats_obj.top_drink_2 if user_stats_obj else None
    top_drink_3 = user_stats_obj.top_drink_3 if user_stats_obj else None
    top_drink_4 = user_stats_obj.top_drink_4 if user_stats_obj else None
    top_drink_5 = user_stats_obj.top_drink_5 if user_stats_obj else None

    return render(request, 'lovedrinks/profile.html', {
        'user': request.user, 
        'user_stats': user_stats_obj, 
        'top_drink_1': top_drink_1, 
        'top_drink_2': top_drink_2, 
        'top_drink_3': top_drink_3, 
        'top_drink_4': top_drink_4, 
        'top_drink_5': top_drink_5
    })

@login_required
def drinks_tried(request):
    total_drinks_tried = DrinkLog.objects.filter(user_id=request.user).values_list('drink_id', flat=True).distinct().count()
    total_drinks_possible = drinks.objects.count()
    total_drinks_logged = DrinkLog.objects.filter(user_id=request.user).count()
    
    # Calculate percentage
    percentage = (total_drinks_tried / total_drinks_possible * 100) if total_drinks_possible > 0 else 0
    
    return render(request, 'lovedrinks/drinks_tried.html', {
        'total_drinks_tried': total_drinks_tried,
        'total_drinks_possible': total_drinks_possible,
        'total_drinks_logged': total_drinks_logged,
        'percentage': percentage,
    })

@login_required
def other_profile(request, username):
    user = User.objects.get(username=username)
    user_stats_obj = user_stats.objects.filter(user_id=user.id).first()

    top_drink_1 = user_stats_obj.top_drink_1 if user_stats_obj else None
    top_drink_2 = user_stats_obj.top_drink_2 if user_stats_obj else None
    top_drink_3 = user_stats_obj.top_drink_3 if user_stats_obj else None
    top_drink_4 = user_stats_obj.top_drink_4 if user_stats_obj else None
    top_drink_5 = user_stats_obj.top_drink_5 if user_stats_obj else None

    
    if request.user != user:
        action = request.GET.get('action')
        if action == 'follow' and not follows.objects.filter(following_id=request.user, followed_id=user).exists():
            follows.objects.create(
                following_id=request.user,
                followed_id=user
            )
        elif action == 'unfollow' and follows.objects.filter(following_id=request.user, followed_id=user).exists():
            follows.objects.filter(following_id=request.user, followed_id=user).delete()
    
    is_following = follows.objects.filter(following_id=request.user, followed_id=user).exists()
    
    return render(request, 'lovedrinks/otherprofile.html', {
        'user': user,
        'follows': is_following,
        'user_stats': user_stats_obj,
        'top_drink_1': top_drink_1,
        'top_drink_2': top_drink_2,
        'top_drink_3': top_drink_3,
        'top_drink_4': top_drink_4,
        'top_drink_5': top_drink_5
    })



class profilesettings(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'lovedrinks/profilesettings.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # Get the user profile
        profile = UserProfile.get_or_create_profile(self.request.user)
        
        # Handle profile picture
        if form.cleaned_data.get('clear_picture'):
            # Remove the profile picture if clear_picture is checked
            if profile.profile_picture:
                # Delete the old file from storage
                if os.path.isfile(profile.profile_picture.path):
                    os.remove(profile.profile_picture.path)
                profile.profile_picture = None
        elif form.cleaned_data.get('profile_picture'):
            # If there's an existing picture, delete it before saving the new one
            if profile.profile_picture:
                if os.path.isfile(profile.profile_picture.path):
                    os.remove(profile.profile_picture.path)
            profile.profile_picture = form.cleaned_data['profile_picture']
        
        profile.save()
        return super().form_valid(form)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'lovedrinks/password.html'
    success_url = reverse_lazy('profile')

@login_required
def top_drinks(request):
    # Get or create user_stats instance for the current user
    user_stats_obj, created = user_stats.objects.get_or_create(user_id=request.user)
    
    if request.method == 'POST':
        form = TopDrinkForm(request.POST, instance=user_stats_obj)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = TopDrinkForm(instance=user_stats_obj)
    
    return render(request, 'lovedrinks/topdrinks.html', {'form': form})

@login_required
def following(request, username):
    user = User.objects.get(username=username)
    return render(request, 'lovedrinks/following.html', {'user': user})

@login_required
def followers(request, username):
    user = User.objects.get(username=username)
    return render(request, 'lovedrinks/followers.html', {'user': user})



@login_required
def drinkpage(request, drink_name):
    drink = drinks.objects.get(drink_name=drink_name)
    user = request.user
    total_logged = DrinkLog.objects.filter(drink_id=drink).count()
    personal_total_logged = DrinkLog.objects.filter(drink_id=drink, user_id=request.user).count()
    personal_average_rating = DrinkLog.objects.filter(drink_id=drink, user_id=request.user).aggregate(Avg('rating'))['rating__avg']
    return render(request, 'lovedrinks/drinkpage.html', {'drink': drink, 'user': user, 'total_logged': total_logged, 'personal_total_logged': personal_total_logged, 'personal_average_rating': personal_average_rating})

@login_required
def drink_reviews(request, drink_name):
    drink = drinks.objects.get(drink_name=drink_name)
    reviews = DrinkLog.objects.filter(drink_id=drink)
    return render(request, 'lovedrinks/drink_reviews.html', {'reviews': reviews, 'drink': drink})

@login_required
def search_drinks(request):
    drink = request.GET.get('drinks', '')
    payload = []
    if drink:
        drink_objs = drinks.objects.filter(drink_name__icontains=drink).order_by('drink_name')

        for drink_obj in drink_objs:
            payload.append(drink_obj.drink_name)

    return JsonResponse({'status': 200, 'data': payload})

@login_required
def search_users(request):
    user = request.GET.get('user', '')
    payload = []
    if user:
        user_objs = User.objects.filter(username__icontains=user).order_by('username')

        for user_obj in user_objs:
            payload.append(user_obj.username)

    return JsonResponse({'status': 200, 'data': payload})

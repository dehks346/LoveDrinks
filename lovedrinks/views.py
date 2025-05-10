from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DrinkLogForm, SearchForm
from django.http import JsonResponse
from .models import drinks, DrinkLog, User, follows



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
    return render(request, 'lovedrinks/log.html', {'log': log})

@login_required
def profile(request):
    user = request.user
    return render(request, 'lovedrinks/profile.html', {'user': request.user})

@login_required
def other_profile(request, username):
    user = User.objects.get(username=username)
    
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
        'follows': is_following
    })


@login_required
def profilesettings(request):
    user = request.user
    return render(request, 'lovedrinks/profilesettings.html', {'user': user})

@login_required
def following(request):
    following_list = follows.objects.filter(following_id=request.user).values_list('followed_id', flat=True)
    following_users = User.objects.filter(id__in=following_list)
    return render(request, 'lovedrinks/following.html', {'following_users': following_users})

@login_required
def followers(request):
    followers_list = follows.objects.filter(followed_id=request.user).values_list('following_id', flat=True)
    followers_users = User.objects.filter(id__in=followers_list)
    return render(request, 'lovedrinks/followers.html', {'followers_users': followers_users})



@login_required
def drinkpage(request, drink_id):
    drink = drinks.objects.get(drink_id=drink_id)
    return render(request, 'lovedrinks/drinkpage.html', {'drink': drink})

def search_drinks(request):
    query = request.GET.get('query', '')
    
    if query:
        drink_results = drinks.objects.filter(drink_name__icontains=query).order_by('drink_name')[:10]
        data = [{'id': drink.drink_id, 'name': drink.drink_name} for drink in drink_results]
    else:
        data = []
    
    return JsonResponse(data, safe=False)

def search_users(request):
    query = request.GET.get('query', '')
    
    if query:
        user_results = User.objects.filter(username__icontains=query).order_by('username')[:10]
        data = [{'id': user.id, 'name': user.username} for user in user_results]
    else:
        data = []
    
    return JsonResponse(data, safe=False)

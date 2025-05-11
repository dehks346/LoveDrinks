from django import forms
from .models import drinks, DrinkLog, User, user_stats, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
import os

class DrinkLogForm(forms.ModelForm):
    drink_name = forms.CharField(
        label='Drink',
        help_text='Type the name of the drink you want to log'
    )

    class Meta:
        model = DrinkLog
        fields = ['drink_name', 'rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'review': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your thoughts about this drink...'}),
        }

    def clean_drink_name(self):
        name = self.cleaned_data['drink_name']
        try:
            drink = drinks.objects.get(drink_name__iexact=name)
        except drinks.DoesNotExist:
            raise forms.ValidationError(f"Drink with name '{name}' does not exist.")
        return drink

    def save(self, commit=True):
        # drink_name field now returns a drinks object (from clean_drink_name)
        self.instance.drink_id = self.cleaned_data['drink_name']
        return super().save(commit)

class SearchForm(forms.Form):
    SEARCH_TYPES = [
        ('drinks', 'Drinks'),
        ('users', 'Users'),
    ]
    
    search_type = forms.ChoiceField(
        choices=SEARCH_TYPES,
        initial='drinks',
        widget=forms.RadioSelect(attrs={'class': 'search-type-selector'})
    )
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...',
            'autocomplete': 'off'
        })
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }

class CustomUserChangeForm(UserChangeForm):
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png,image/gif'
        }),
        help_text='Maximum file size: 5MB. Allowed formats: JPG, JPEG, PNG, GIF'
    )
    clear_picture = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Check this to remove your current profile picture'
    )
    instagram_username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Enter your Instagram username'
    )
    twitter_username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Enter your Twitter username'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture', 'clear_picture', 'instagram_username', 'twitter_username')

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            if picture.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("Image file too large ( > 5MB )")
            if not picture.content_type in ['image/jpeg', 'image/png', 'image/gif']:
                raise ValidationError("Unsupported file type. Please upload a JPG, PNG, or GIF file.")
        return picture

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Get or create the user profile
            profile = UserProfile.get_or_create_profile(user)
            
            # Handle profile picture
            if self.cleaned_data.get('clear_picture'):
                # Remove the profile picture if clear_picture is checked
                if profile.profile_picture:
                    # Delete the old file from storage
                    if os.path.isfile(profile.profile_picture.path):
                        os.remove(profile.profile_picture.path)
                    profile.profile_picture = None
            elif self.cleaned_data.get('profile_picture'):
                # If there's an existing picture, delete it before saving the new one
                if profile.profile_picture:
                    if os.path.isfile(profile.profile_picture.path):
                        os.remove(profile.profile_picture.path)
                profile.profile_picture = self.cleaned_data['profile_picture']
            
            profile.save()
        return user

class TopDrinkForm(forms.ModelForm):
    class Meta:
        model = user_stats
        fields = ['top_drink_1', 'top_drink_2', 'top_drink_3', 'top_drink_4', 'top_drink_5']

    def clean_top_drink_1(self):
        return self.cleaned_data['top_drink_1']
    
    def clean_top_drink_2(self):
        return self.cleaned_data['top_drink_2']

    def clean_top_drink_3(self):
        return self.cleaned_data['top_drink_3']

    def clean_top_drink_4(self):
        return self.cleaned_data['top_drink_4']

    def clean_top_drink_5(self):
        return self.cleaned_data['top_drink_5']
    
    def update_user_stats(self):
        self.instance.user_id = self.user_id
        return super().save()
    



from django import forms
from .models import drinks, DrinkLog, User

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



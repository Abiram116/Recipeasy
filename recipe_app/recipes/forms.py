from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Recipe, RecipeSchedule, Tag

class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,  # Set this to True to enforce selecting at least one tag
        label="Tags"
    )

    class Meta:
        model = Recipe
        fields = ['name', 'description', 'image', 'rating', 'is_inspiring', 'ingredients', 'tags']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter recipe name'}),
            'description': forms.Textarea(attrs={'class': 'form-control recipe-textarea', 'rows': 5, 'placeholder': 'Describe your recipe'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}, choices=[(i, str(i)) for i in range(1, 6)]),
            'is_inspiring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control recipe-textarea', 'rows': 5, 'placeholder': 'List your ingredients'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})  # Checkbox for tags
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally, you can filter available tags based on some criteria, e.g., the current user
        # self.fields['tags'].queryset = Tag.objects.filter(user=user)

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if not tags:
            raise ValidationError('At least one tag is required.')  # Custom error message if no tags are selected
        return tags

class RecipeScheduleForm(forms.ModelForm):
    class Meta:
        model = RecipeSchedule
        fields = ['recipe', 'datetime']
        labels = {
            'recipe': 'Select Recipe',
            'datetime': 'Schedule Date and Time'
        }
        help_texts = {
            'datetime': 'Select the date and time for this recipe'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['recipe'].queryset = Recipe.objects.filter(user=user)
        self.fields['datetime'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })

    def clean_datetime(self):
        scheduled_time = self.cleaned_data['datetime']
        if scheduled_time < timezone.now():
            raise ValidationError("Scheduled time cannot be in the past.")
        return scheduled_time

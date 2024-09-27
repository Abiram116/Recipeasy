from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='recipes/')
    date = models.DateField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_inspiring = models.BooleanField(default=True)
    ingredients = models.TextField()

    def get_absolute_url(self):
        return reverse('recipe_detail', args=[str(self.id)])
    
    def get_ingredients_list(self):
        return [ing.strip() for ing in self.ingredients.split('\n')]
    
    def clean(self):
        if self.rating < 0 or self.rating > 5:  # Assuming a scale of 0-5
            raise ValidationError('Rating must be between 0 and 5.')

    def __str__(self):
        return self.name


class UserRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_inspiring = models.BooleanField(default=False)

    class Meta:
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"


class Update(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class RecipeSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    datetime = models.DateTimeField()  

    def __str__(self):
        return f"{self.recipe.name} scheduled for {self.datetime.strftime('%Y-%m-%d %H:%M')}"
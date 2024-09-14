from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.shortcuts import render
from recipes.forms import RecipeForm
from .models import Recipe, UserRecipe

def home(request):
    # Remove the filter to get all recipes
    inspiring_recipes = Recipe.objects.all()
    
    for recipe in inspiring_recipes:
        recipe.ingredients_list = recipe.get_ingredients_list()
    
    context = {
        'inspiring_recipes': inspiring_recipes,
        'user': request.user,
    }
    return render(request, 'home.html', context)

@login_required
def profile(request):
    user_recipes = UserRecipe.objects.filter(user=request.user)
    recipes = [user_recipe.recipe for user_recipe in user_recipes]

    context = {
        'user': request.user,
        'recipes': recipes,
    }
    return render(request, 'profile.html', context)

@login_required
def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.save()
            UserRecipe.objects.create(recipe=recipe, user=request.user)
            return redirect('home')
    else:
        form = RecipeForm()
    return render(request, 'create_recipe.html', {'form': form})

@login_required
def add_to_my_recipes(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    UserRecipe.objects.get_or_create(recipe=recipe, user=request.user)
    return redirect('home')

@login_required
def my_recipes(request):
    user_recipes = UserRecipe.objects.filter(user=request.user)
    recipes = [user_recipe.recipe for user_recipe in user_recipes]
    return render(request, 'my_recipes.html', {'recipes': recipes})

@login_required
def clear_my_recipes(request):
    UserRecipe.objects.filter(user=request.user).delete()
    return redirect('my_recipes')

@login_required
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    ingredients = [ingredient.strip() for ingredient in recipe.ingredients.replace('\n', ',').split(',') if ingredient.strip()]
from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe

def home(request):
    inspiring_recipes = Recipe.objects.all()[:6]
    for recipe in inspiring_recipes:
        recipe.ingredients_list = recipe.ingredients.split(',')
    context = {
        'inspiring_recipes': inspiring_recipes,
    }
    return render(request, 'home.html', context)


def add_to_my_recipes(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    my_recipes = request.session.get('my_recipes', [])
    
    if recipe_id not in my_recipes:
        my_recipes.append(recipe_id)
        # save it back to the session
    request.session['my_recipes'] = my_recipes
    return redirect('home')


def my_recipes(request):
    # get the recipe IDs stored in the session
    recipe_ids = request.session.get('my_recipes', [])
    
    # Retrieve the actual Recipe objects from the database
    recipes = Recipe.objects.filter(id__in=recipe_ids)
    
    return render(request, 'my_recipes.html', {'recipes': recipes})

def clear_my_recipes(request):
    if 'my_recipes' in request.session:
        del request.session['my_recipes']
    return redirect('my_recipes')

def recipe_detail(request, pk):
    # Retrieve the recipe by primary key (pk)
    recipe = get_object_or_404(Recipe, pk=pk)
    ingredients = [ingredient.strip() for ingredient in recipe.ingredients.split(',')]
    return render(request, 'recipe_detail.html', {'recipe': recipe, 'ingredients': ingredients})

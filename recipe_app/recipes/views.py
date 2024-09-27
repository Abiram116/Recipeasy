from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.shortcuts import render
from recipes.forms import RecipeForm, RecipeScheduleForm
from .models import Recipe, UserRecipe, RecipeSchedule
from django.http import JsonResponse
import datetime
import json
from django.views.decorators.csrf import csrf_exempt


def home(request):
    inspiring_recipes = Recipe.objects.filter(is_inspiring=True)
    for recipe in inspiring_recipes:
        recipe.ingredients_list = [ingredient.strip() for ingredient in recipe.ingredients.replace('\n', ',').split(',') if ingredient.strip()]
    
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

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    ingredients = [ingredient.strip() for ingredient in recipe.ingredients.replace('\n', ',').split(',') if ingredient.strip()]
    return render(request, 'recipe_detail.html', {'recipe': recipe, 'ingredients': ingredients})


def add_to_my_recipes_session(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    my_recipes = request.session.get('my_recipes', [])
    
    if recipe_id not in my_recipes:
        my_recipes.append(recipe_id)
    request.session['my_recipes'] = my_recipes
    return redirect('home')

def my_recipes_session(request):
    recipe_ids = request.session.get('my_recipes', [])
    recipes = Recipe.objects.filter(id__in=recipe_ids)
    return render(request, 'my_recipes.html', {'recipes': recipes})

def clear_my_recipes_session(request):
    if 'my_recipes' in request.session:
        del request.session['my_recipes']
    return redirect('my_recipes')

@login_required
def calendar_view(request):
    return render(request, 'calendar.html')

@login_required
def schedule_data(request):
    schedules = RecipeSchedule.objects.filter(user=request.user)
    events = []
    for schedule in schedules:
        events.append({
            'title': schedule.recipe.name,
            'start': schedule.datetime.strftime('%Y-%m-%T%H:%M:%S'),
        })
    return JsonResponse(events, safe=False)

@login_required
def schedule_recipe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipe_id = data.get('recipe_id')
        datetime = data.get('datetime')

        # Assuming you have Recipe and RecipeSchedule models
        recipe = Recipe.objects.get(id=recipe_id)
        user = request.user  # Assuming the user is logged in

        # Create a new schedule for this recipe
        RecipeSchedule.objects.create(
            recipe=recipe,
            user=user,
            date=datetime  # Store the date as a string or convert to a DateTime object if needed
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'fail'}, status=400)

@login_required
@csrf_exempt  # This is necessary for handling AJAX POST requests
def update_schedule(request, event_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_datetime = datetime.fromisoformat(data['newDatetime'].replace('Z', ''))
        
        try:
            schedule = RecipeSchedule.objects.get(id=event_id)
            schedule.datetime = new_datetime
            schedule.save()
            return JsonResponse({'success': True})
        except RecipeSchedule.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found'}, status=404)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@login_required
def calendar_view(request):
    # Fetch the current user's recipes
    user_recipes = UserRecipe.objects.filter(user=request.user).select_related('recipe')

    # Create a list to hold recipe details
    recipes = [{
        'name': user_recipe.recipe.name,
        'description': user_recipe.recipe.description,
        'image': user_recipe.recipe.image.url if user_recipe.recipe.image else None,
        'datetime': user_recipe.recipe.schedule.datetime if hasattr(user_recipe.recipe, 'schedule') else None,
        # Add any other fields you want to include
    } for user_recipe in user_recipes]
    # Pass the recipes to the template
    context = {
        'my_recipes': recipes,
    }
    return render(request, 'calendar.html', context)
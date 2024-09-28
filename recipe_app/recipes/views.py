from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Recipe, UserRecipe, RecipeSchedule
from .forms import RecipeForm
import json
from datetime import datetime
from django.utils import timezone

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
    user_recipe, created = UserRecipe.objects.get_or_create(recipe=recipe, user=request.user)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if created:
            return JsonResponse({'status': 'success', 'message': 'Recipe added to My Recipes'})
        else:
            return JsonResponse({'status': 'info', 'message': 'Recipe already in My Recipes'})
    else:
        if created:
            messages.success(request, 'Recipe added to My Recipes')
        else:
            messages.info(request, 'Recipe already in My Recipes')
        return redirect('home')
    
@login_required
def my_recipes(request):
    user_recipes = UserRecipe.objects.filter(user=request.user)
    recipes = [user_recipe.recipe for user_recipe in user_recipes]
    return render(request, 'my_recipes.html', {'recipes': recipes})

@login_required
def remove_from_my_recipes(request, recipe_id):
    if request.method == 'POST':
        user_recipe = get_object_or_404(UserRecipe, user=request.user, recipe_id=recipe_id)
        user_recipe.delete()
        messages.success(request, 'Recipe removed successfully.')
    return redirect('my_recipes')

@login_required
def clear_my_recipes(request):
    if request.method == 'POST':
        UserRecipe.objects.filter(user=request.user).delete()
        messages.success(request, 'All recipes cleared successfully.')
    return redirect('my_recipes')

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    ingredients = [ingredient.strip() for ingredient in recipe.ingredients.replace('\n', ',').split(',') if ingredient.strip()]
    return render(request, 'recipe_detail.html', {'recipe': recipe, 'ingredients': ingredients})

# Calendar views
@login_required
def calendar_view(request):
    user_recipes = UserRecipe.objects.filter(user=request.user).select_related('recipe')
    recipes = [{
        'id': user_recipe.recipe.id,
        'name': user_recipe.recipe.name,
    } for user_recipe in user_recipes]

    context = {
        'my_recipes': recipes,
    }
    return render(request, 'calendar.html', context)

@login_required
def get_recipe_schedule(request):
    scheduled_recipes = RecipeSchedule.objects.filter(user=request.user).select_related('recipe')
    events = [{
        'id': str(schedule.id),
        'title': schedule.recipe.name,
        'start': schedule.datetime.date().isoformat(),
        'allDay': True,
        'extendedProps': {
            'recipeId': schedule.recipe.id
        }
    } for schedule in scheduled_recipes]

    return JsonResponse(events, safe=False)

@login_required
@csrf_exempt
@require_POST
def save_recipe_schedule(request):
    data = json.loads(request.body)
    recipe_id = data['recipeId']
    start_time_str = data['startTime']
    event_id = data.get('eventId')

    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Parse the date string directly, without timezone awareness
    start_date = datetime.strptime(start_time_str, '%Y-%m-%d').date()

    # Create a timezone-aware datetime for the start of the day
    start_time = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))

    if event_id:
        schedule, created = RecipeSchedule.objects.update_or_create(
            id=event_id,
            user=request.user,
            defaults={'recipe': recipe, 'datetime': start_time}
        )
    else:
        schedule = RecipeSchedule.objects.create(
            user=request.user,
            recipe=recipe,
            datetime=start_time
        )

    return JsonResponse({
        'id': str(schedule.id),
        'startTime': schedule.datetime.date().isoformat(),
    })

@login_required
@csrf_exempt
@require_POST
def remove_recipe_schedule(request):
    data = json.loads(request.body)
    event_id = data['eventId']

    try:
        schedule = RecipeSchedule.objects.get(id=event_id, user=request.user)
        schedule.delete()
        return JsonResponse({'success': True})
    except RecipeSchedule.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Event not found'}, status=404)
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Recipe-related URLs
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('add_to_my_recipes/<int:recipe_id>/', views.add_to_my_recipes, name='add_to_my_recipes'),
    path('create/', views.create_recipe, name='create_recipe'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('remove_from_my_recipes/<int:recipe_id>/', views.remove_from_my_recipes, name='remove_from_my_recipes'),
    path('clear_my_recipes/', views.clear_my_recipes, name='clear_my_recipes'),

    # Authentication-related URLs
    path('accounts/', include('allauth.urls')),  # Use Django Allauth's URLs

    # Profile URL
    path('profile/', views.profile, name='profile'),

    # Calendar-related URLs
    path('calendar/', views.calendar_view, name='calendar'),
    path('get_recipe_schedule/', views.get_recipe_schedule, name='get_recipe_schedule'),
    path('save_recipe_schedule/', views.save_recipe_schedule, name='save_recipe_schedule'),
    path('remove_recipe_schedule/', views.remove_recipe_schedule, name='remove_recipe_schedule'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

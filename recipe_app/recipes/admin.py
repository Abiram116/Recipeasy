from django.contrib import admin
from .models import Recipe, Update, Tag

admin.site.register(Recipe)
admin.site.register(Update)
admin.site.register(Tag)

from django.contrib import admin
from rango.models import Category, Page, UserProfile


# Add in this class to customize the Admin Interface
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


# Register your models here.
admin.site.register(Category)
admin.site.register(Page)
admin.site.register(UserProfile)

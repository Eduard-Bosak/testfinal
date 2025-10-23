from django.contrib import admin
from import_export import resources
from .models import Person


class PersonResource(resources.ModelResource):
    class Meta:
        model = Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_on_main', 'name', 'skills', 'skill_level','desk')
    list_editable = ('skills', 'skill_level', 'is_on_main', 'desk')
    search_fields = ('id', 'name', 'sex', 'skills', 'skill_level', 'description', )
    list_filter = ('name', 'skills','desk')
    list_display_links = ('id', 'name',)

    resources_classes = [PersonResource]
























# Register your models here.

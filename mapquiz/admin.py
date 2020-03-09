from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from nested_inline.admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from .models import *


class ResourceTemplate:
    fields = ['name', 'code']
    readonly_fields = ['code']

    def code(self, obj):
        return obj.uri.code


class LocationInline(ResourceTemplate, NestedTabularInline):
    model = Location
    extra = 3
    fk_name = 'quiz'
    fields = ResourceTemplate.fields + ['hint', 'found_text', 'lat', 'lng']

    # https://stackoverflow.com/a/18738715
    formfield_overrides = {
        TextField: {'widget': Textarea(
            attrs={'rows': 5,
                   'cols': 25, }
        )}
    }


class QuizInline(ResourceTemplate, NestedStackedInline):
    model = Quiz
    inlines = [LocationInline]
    extra = 1
    fk_name = 'hunt'
    fields = ResourceTemplate.fields + ['stage']


@admin.register(Hunt)
class HuntAdmin(ResourceTemplate, NestedModelAdmin):
    inlines = [QuizInline]


@admin.register(Quiz)
class QuizAdmin(ResourceTemplate, NestedModelAdmin):
    inlines = [LocationInline]

    fields = ResourceTemplate.fields + ['stage']


@admin.register(Location)
class LocationAdmin(ResourceTemplate, admin.ModelAdmin):
    fields = ResourceTemplate.fields + ['hint', 'found_text', 'lat', 'lng']


admin.site.register(Team)

from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from nested_inline.admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from .models import *


class ResourceTemplate:
    fields = ['name', 'code']
    readonly_fields = ['code']
    list_display = ['name', 'code']

    def code(self, obj: Resource):
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
    fields = ResourceTemplate.fields + ['stages']
    readonly_fields = ResourceTemplate.readonly_fields + ['stages']
    list_display = ResourceTemplate.list_display + ['stages']


@admin.register(Quiz)
class QuizAdmin(ResourceTemplate, NestedModelAdmin):
    inlines = [LocationInline]
    fields = ResourceTemplate.fields + ['stage']
    list_display = ResourceTemplate.list_display + ['name', 'code']


@admin.register(Location)
class LocationAdmin(ResourceTemplate, admin.ModelAdmin):
    fields = ResourceTemplate.fields + ['hint', 'found_text', 'lat', 'lng']
    list_display = ResourceTemplate.list_display + ['short_hint']

    def short_hint(self, loc: Location, max_length: int = 25) -> str:
        """ Short extract of a hint """
        hint = loc.hint
        if len(hint) > max_length:
            return hint[: max_length - 3] + "..."

        return hint[: max_length]


@admin.register(Team)
class TeamAdmin(ResourceTemplate, admin.ModelAdmin):
    fields = ResourceTemplate.fields + ['logo', 'hunt', 'last_location']
    list_display = ResourceTemplate.list_display + ['hunt', 'last_location']

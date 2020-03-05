from django.shortcuts import get_object_or_404
from django.views import generic

from .models import *


class LocationView(generic.DetailView):
    model = Location

    def get_object(self, queryset=None):
        """ Overwrite to find object by code"""
        code = self.kwargs.get('code')
        if queryset is None:
            queryset = self.model.objects

        return get_object_or_404(queryset, uri__code=code)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = context['object']
        solved_stage = location.quiz.stage
        hunt = location.quiz.hunt
        try:
            next_quiz = hunt.quiz_set.get(stage=solved_stage + 1)
        except Quiz.DoesNotExist:
            context['final_stage'] = True
            return context
        else:
            context['final_stage'] = False

        hints = []
        next_locations = next_quiz.location_set.all()
        for location in next_locations:
            hints.append(location.hint)

        context['hints'] = hints
        return context

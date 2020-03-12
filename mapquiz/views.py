from django.shortcuts import get_object_or_404
from django.views import generic

from .models import *


class ResourceDetailView(generic.DetailView):
    def get_object(self, queryset=None):
        """ Overwrite to find the resource by code """
        code = self.kwargs.get('code')
        if queryset is None:
            queryset = self.model.objects

        return get_object_or_404(queryset, code=code)


class LocationView(ResourceDetailView):
    model = Location

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = context['object']

        # Try to get next quiz
        solved_stage = location.quiz.stage
        hunt = location.quiz.hunt
        try:
            next_quiz = hunt.quiz_set.get(stage=solved_stage + 1)
        except Quiz.DoesNotExist:
            # Render page as final page without new hints
            context['final_stage'] = True
            return context

        # Collect all the hints for the next quiz
        hints = []
        next_locations = next_quiz.location_set.all()
        for location in next_locations:
            hints.append(location.hint)

        context['hints'] = hints
        return context

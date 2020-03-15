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
        # Check team access
        team_id = context['view'].request.session.get('team_id', None)
        if not team_id:
            return context

        context['team'] = Team.objects.get(code=team_id)
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

    def render_to_response(self, context, **response_kwargs):
        """ Render denied.html if the user does not have a team """
        if 'team' not in context:
            response_kwargs.setdefault('content_type', self.content_type)
            return self.response_class(
                request=self.request,
                template=['mapquiz/denied.html'],
                context=context,
                using=self.template_engine,
                **response_kwargs
            )
        return super().render_to_response(context, **response_kwargs)


class TeamView(ResourceDetailView):
    model = Team

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = context['object']
        context['team'] = team  # For the team navbar, object == team for the team view

        request = context['view'].request
        session = request.session

        team_cookie = session.get('team_id', None)
        if team_cookie is None:
            # # https://docs.djangoproject.com/en/3.0/topics/http/sessions/#setting-test-cookies
            # if request.method == 'GET':
            #     session.set_test_cookie()
            #     context['test_cookie'] = True  # HTML has to set next request to POST
            #     return context
            # # Try to set cookie with Team code
            # if not session.test_cookie_worked():
            #     context['test_cookie_failed'] = True  # HTML asks user to enable cookies
            #
            # session.delete_test_cookie()
            #
            session['team_id'] = team.code
            context['joining'] = True

        return context

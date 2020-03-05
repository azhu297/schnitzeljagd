from django.urls import path

from . import views

app_name = 'mapquiz'
# urlpatterns = [
#     path('explanation/', views.Explanation.as_view(), name='explanation'),
#     path('register/<int:uri>/', views.Hunt.as_view(), name='hunt'),
#     path('quiz/<int:uri>/', views.Quiz.as_view(), name='quiz'),
#     path('location/<int:uri>/', views.Location.as_view(), name='location'),
# ]

urlpatterns = [
    path('location/<slug:code>', views.LocationView.as_view(), name='location'),

]

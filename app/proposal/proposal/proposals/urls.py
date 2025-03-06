from django.urls import path
from .views import create_proposal

urlpatterns = [
    path('create/', create_proposal, name='draft_proposals'),
]
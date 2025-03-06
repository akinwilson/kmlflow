from django.urls import path
from .views import *

urlpatterns = [
    path('', landing_page, name='live_proposals'),
    path('proposals/', proposal_page, name='draft_proposals'),
]

from django.urls import path
from .views import *

urlpatterns = [
    path('', landing_page, name='landing_page'),
    # path('proposals/', proposal_page, name='proposal_page'),
]

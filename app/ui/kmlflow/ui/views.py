from django.shortcuts import render
from django.http import HttpResponse
'''
landing page with iframes displaying each service
'''
def landing_page(request):
    ascii_art = """
     _              _  __ _               
    | | ___ __ ___ | |/ _| | _____      __
    | |/ / '_ ` _ \| | |_| |/ _ \ \ /\ / /
    |   <| | | | | | |  _| | (_) \ V  V / 
    |_|\_\_| |_| |_|_|_| |_|\___/ \_/\_/  

    """ 
    return render(request, "ui/landing.html", {"ascii_art": ascii_art})




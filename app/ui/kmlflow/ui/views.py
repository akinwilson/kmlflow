from django.shortcuts import render
from django.http import HttpResponse

def landing_page(request):
    ascii_art = """
     _              _  __ _               
    | | ___ __ ___ | |/ _| | _____      __
    | |/ / '_ ` _ \| | |_| |/ _ \ \ /\ / /
    |   <| | | | | | |  _| | (_) \ V  V / 
    |_|\_\_| |_| |_|_|_| |_|\___/ \_/\_/  

    """ 
    return render(request, "ui/landing.html", {"ascii_art": ascii_art})

def service_ui(request, service_name): 
    service_urls = { "mlflow": "/mlflow", 
                    "katib": "/katib",
                    "minio": "/minio",
                    "grafana": "/grafana",
                    "argocd": "/argocd"}
    return render(request, "ui/services.html", {"service_name": service_name, "service_url": service_urls.get(service_name, "/")})






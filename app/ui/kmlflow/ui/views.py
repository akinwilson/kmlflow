from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from kubernetes import client, config
'''
landing page with iframes displaying each service
'''

def get_endpoints():
    config.load_incluster_config()
    namespace = "models" 
    v1 = client.CoreV1Api()
    endpoints = v1.list_namespaced_pod(namespace)
    endpoint_names = [x.split("-")[1] for x in [pod.metadata.name for pod in endpoints.items]]
    print(f"{endpoint_names=}")
    return {'endpoints': endpoint_names}

def landing_page(request):
    ascii_art = """
     _              _  __ _               
    | | ___ __ ___ | |/ _| | _____      __
    | |/ / '_ ` _ \| | |_| |/ _ \ \ /\ / /
    |   <| | | | | | |  _| | (_) \ V  V / 
    |_|\_\_| |_| |_|_|_| |_|\___/ \_/\_/  

    """ 
    get_endpoints()
    return render(request, "ui/landing.html", {"ascii_art": ascii_art, **get_endpoints()})


def proposal_page(request):
    return render(request, "proposal/landing.html")


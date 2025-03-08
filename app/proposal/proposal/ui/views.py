from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from proposals.models import Proposals, Category, Tags
import json 
'''
landing page of Proposals; research, deployment and development tasks to be executed on the network
'''

def get_proposal(request):
    return {'proposals': proposals}


def landing_page(request):
    proposals = Proposals.objects.all().order_by('-created_at')
    tags = Category.objects.all()
    sub_tags = Tags.objects.all()
    sub_tags_dict = {tag.id: list(sub_tags.filter(category=tag).order_by('name').values('id', 'name')) for tag in tags}
    return render(request, "ui/landing.html", {
        'proposals': proposals,
        'page_title': 'Proposals',
        'tags': tags,
        'sub_tags': json.dumps(sub_tags_dict)  
    })


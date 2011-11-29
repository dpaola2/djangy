import os
from django.http import HttpResponse

def index(request):
    return HttpResponse('testapp.main second edition')

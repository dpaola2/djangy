import os
from django.http import HttpResponse
from main.models import *

def index(request):
    return HttpResponse('testapp.main second edition')

def add_foo(request):
    f = Foo(name="bar")
    f.save()
    return HttpResponse("bar")

def count_rows(request):
    return HttpResponse(Foo.objects.all.count())

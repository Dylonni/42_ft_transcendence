from django.http import HttpResponse
from django.template.loader import render_to_string

def login(request):
    html = render_to_string('login.html', request=request)
    return HttpResponse(html)

def register(request):
    html = render_to_string('register.html', request=request)
    return HttpResponse(html)
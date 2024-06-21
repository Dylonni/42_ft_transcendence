from django.http import HttpResponse
from django.template.loader import render_to_string

def login(request):
    html = render_to_string('accounts/login.html', request=request)
    return HttpResponse(html)

def register(request):
    html = render_to_string('accounts/register.html', request=request)
    return HttpResponse(html)
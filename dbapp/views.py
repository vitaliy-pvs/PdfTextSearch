from django.http import JsonResponse
from django.shortcuts import render
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dbserver.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
from dbapp.models import Drawing


def main_page(request):
    return render(request, 'main_page.html')


def text_search(request):
    i = 0
    queryset = Drawing.objects.all()
    response = []
    text = request.GET.get('text', None)
    for obj in queryset:
        if obj.text.find(text) != -1:
            response.append(obj.name)
            i += 1
    return JsonResponse(response, safe=False)

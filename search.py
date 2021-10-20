import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dbserver.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
from dbapp.models import Drawing

i = 0
queryset = Drawing.objects.all()
for obj in queryset:
    if obj.text.find('Опора INTEGRATO') != -1:
        print(obj.name + ': ' + obj.path)
        i += 1

print('Найдено ' + str(i) + ' чертежей.')

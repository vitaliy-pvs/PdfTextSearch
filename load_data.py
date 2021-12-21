from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import os.path
import ntpath

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dbserver.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from dbapp.models import Drawing


def convert_pdf_to_txt(path_1):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path_1, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

print('создание списка файлов чертежей')

FileList = []
def GetFileList(folder):
    for d, dirs, files in os.walk(folder):
        for f in files:
            FileList.append(d + "/" + f)


GetFileList("\\\\fileserver.souz.tld\\mediaw\\Детали\\КБ\\Цех №1")
GetFileList("\\\\fileserver.souz.tld\\mediaw\\Детали\\КБ\\Цех №2")

print('очистка базы')

Drawing.objects.all().delete()

print('копирование текста чертежей в базу')

list = []
for path in FileList:
    name = ntpath.basename(path)
    name, extension = os.path.splitext(name)
    if extension == ".PDF" or extension == ".pdf":
        if name in list:
            continue
        elif name[0] == '~':
            continue
        else:
            list.append(name)
            text = ''

            try:
                text = convert_pdf_to_txt(path)
            except Exception:

                print('Ошибка при извлечении текста из: ' + path)

            drawing = Drawing(path=path, name=name, text=text)
            drawing.save()


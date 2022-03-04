from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import os.path
import ntpath
import xlsxwriter
import re

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dbserver.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from dbapp.models import Drawing

"""
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


print('Создание списка имен файлов чертежей ...')

FileList = []


def GetFileList(folder):
    for d, dirs, files in os.walk(folder):
        for f in files:
            FileList.append(d + "/" + f)


GetFileList("\\\\fileserver.souz.tld\\mediaw\\Детали\\КБ\\Цех №1")
GetFileList("\\\\fileserver.souz.tld\\mediaw\\Детали\\КБ\\Цех №2")
# GetFileList("C:\\Users\\user\\Desktop\\база чертежей")
"""
print('Очистка таблицы Drawing ...')

Drawing.objects.all().delete()
"""
print('Запись в таблицу Drawing полей path, name, text ...')

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


print('Запись в таблицу Drawing значений поля true_name и true_text ...')

MO_PK = r'[MМ][OО][ ][РP][KК]'
MB_TT = r'[MМ][BВ][ ][ТT][ТT]'
MB_PM = r'[MМ][BВ][ ][РP][MМ]'
MB_EH = r'[MМ][BВ][ ][EЕ][НH]'

drawing_set_for_regexp = Drawing.objects.all()
for drw in drawing_set_for_regexp:
    if re.fullmatch(MO_PK, drw.name[:5]):
        drw.true_name = 'MO PK' + drw.name[5:]
    elif re.fullmatch(MB_TT, drw.name[:5]):
        drw.true_name = 'MB TT' + drw.name[5:]
    elif re.fullmatch(MB_PM, drw.name[:5]):
        drw.true_name = 'MB PM' + drw.name[5:]
    elif re.fullmatch(MB_EH, drw.name[:5]):
        drw.true_name = 'MB EH' + drw.name[5:]
    else:
        drw.true_name = drw.name

    strings_list = drw.text.split('\n')
    for string in strings_list:
        if len(string) > 7:
            if re.fullmatch(MO_PK, string[:5]):
                new_string = 'MO PK' + string[5:]
                for i, s in enumerate(strings_list):
                    if s == string:
                        strings_list[i] = new_string
            elif re.fullmatch(MB_TT, string[:5]):
                new_string = 'MB TT' + string[5:]
                for i, s in enumerate(strings_list):
                    if s == string:
                        strings_list[i] = new_string
            elif re.fullmatch(MB_PM, string[:5]):
                new_string = 'MB PM' + string[5:]
                for i, s in enumerate(strings_list):
                    if s == string:
                        strings_list[i] = new_string
            elif re.fullmatch(MB_EH, string[:5]):
                new_string = 'MB EH' + string[5:]
                for i, s in enumerate(strings_list):
                    if s == string:
                        strings_list[i] = new_string
    drw.true_text = '\n'.join(str(s) for s in strings_list)
    drw.save()


print('Запись в таблицу Drawing значений поля article ...')

drawing_set_for_art = Drawing.objects.all()
for draw in drawing_set_for_art:
    substrings_with_max_len = ''
    substrings_list = draw.true_text.split('\n')
    for substring in substrings_list:
        if substring == draw.true_name[:len(substring)]:
            if len(substring) > len(substrings_with_max_len):
                substrings_with_max_len = substring
    if substrings_with_max_len == '':
        for substring in substrings_list:
            if substring[-6:] == 'Листов':
                if substring[-7:-6] == ' ':
                    substring = substring[:-7]
                else:
                    substring = substring[:-6]
                if substring == draw.true_name[:len(substring)]:
                    if len(substring) > len(substrings_with_max_len):
                        substrings_with_max_len = substring
                substrings_with_max_len = substring

    draw.article = substrings_with_max_len
    draw.save()


print('Очистка полей applicability, incoming, structure ...')
all_draw_set = Drawing.objects.all()
for the_draw in all_draw_set:
    the_draw.applicability = ''
    the_draw.incoming = ''
    the_draw.structure = ''
    the_draw.save()


print('Уаление дублей и артикулов длиной меньше 4-х символов ...')
set_to_del = Drawing.objects.all()
article_list = []
for current_draw in set_to_del:
    if len(current_draw.article) < 4:
        current_draw.delete()
    else:
        if current_draw.article in article_list:
            current_draw.delete()
        else:
            article_list.append(current_draw.article)


print('Создание pref_end_dict ...')
pref_end_dict = {}
article_list = Drawing.objects.values_list('article', flat=True)
for current_article in article_list:
    for article in article_list:
        split_result = article.split(current_article)
        if len(split_result) == 2 and (split_result[0] != '' or split_result[1] != ''):
            if current_article not in pref_end_dict.keys():
                pref_end_dict[current_article] = {
                    'pref_end_set': set(),
                    'pref_set': set(),
                    'end_set': set()
                }
            if split_result[0] != '' and split_result[1] != '':
                pref_end_dict[current_article]['pref_end_set'].add("\n".join(split_result))
            elif split_result[0] != '':
                pref_end_dict[current_article]['pref_set'].add(split_result[0])
            elif split_result[1] != '':
                pref_end_dict[current_article]['end_set'].add(split_result[1])


print('Запись в таблицу Drawing значений поля applicability ...')
drawing_set_for_applicability = Drawing.objects.all()
for dr in drawing_set_for_applicability:
    for dr_2 in drawing_set_for_applicability:
        if re.search(pattern=r'[ \n]' + dr.article + r'[ \n]', string=dr_2.true_text):
            indices_object = re.finditer(pattern=r'[ \n]' + dr.article + r'[ \n]', string=dr_2.true_text)
            indices = [index.start() for index in indices_object]
            for i in indices:
                is_used_flag = False
                if dr.article in pref_end_dict.keys():

                    if len(pref_end_dict[dr.article]['pref_end_set']) > 0:
                        for pref_end_elem in pref_end_dict[dr.article]['pref_end_set']:
                            pref_end_elem_split = pref_end_elem.split("\n")
                            if i + 1 - len(pref_end_elem_split[0]) >= 0 and i + 1 + len(pref_end_elem_split[1]) <= len(dr_2.true_text):
                                prefix = dr_2.true_text[i + 1 - len(pref_end_elem_split[0]):i + 1]
                                ending = dr_2.true_text[i + 1:i + 1 + len(pref_end_elem_split[1])]
                                if prefix == pref_end_elem_split[0] and ending == pref_end_elem_split[1]:
                                    for drw_obj in Drawing.objects.filter(article=prefix + dr.article + ending):
                                        if drw_obj.applicability == '':
                                            drw_obj.applicability = dr_2.article
                                        elif dr_2.article not in drw_obj.applicability.split('\n'):
                                            drw_obj.applicability = drw_obj.applicability + "\n" + dr_2.article
                                        drw_obj.save()
                                        drawing_set_for_applicability = Drawing.objects.all()
                                        is_used_flag = True

                    if len(pref_end_dict[dr.article]['pref_set']) > 0:
                        for pref_elem in pref_end_dict[dr.article]['pref_set']:
                            if i + 1 - len(pref_elem) >= 0:
                                pref = dr_2.true_text[i + 1 - len(pref_elem):i + 1]
                                if pref == pref_elem:
                                    for pref_drw_obj in Drawing.objects.filter(article=pref + dr.article):
                                        if pref_drw_obj.applicability == '':
                                            pref_drw_obj.applicability = dr_2.article
                                        elif dr_2.article not in pref_drw_obj.applicability.split('\n'):
                                            pref_drw_obj.applicability = pref_drw_obj.applicability + "\n" + dr_2.article
                                        pref_drw_obj.save()
                                        drawing_set_for_applicability = Drawing.objects.all()
                                        is_used_flag = True

                    if len(pref_end_dict[dr.article]['end_set']) > 0:
                        for ending_elem in pref_end_dict[dr.article]['end_set']:
                            if i + 1 + len(ending_elem) <= len(dr_2.true_text):
                                ending = dr_2.true_text[i + 1:i + 1 + len(ending_elem)]
                                if ending == ending_elem:
                                    for end_drw_obj in Drawing.objects.filter(article=dr.article + ending_elem):
                                        if end_drw_obj.applicability == '':
                                            end_drw_obj.applicability = dr_2.article
                                        elif dr_2.article not in end_drw_obj.applicability.split('\n'):
                                            end_drw_obj.applicability = end_drw_obj.applicability + "\n" + dr_2.article
                                        end_drw_obj.save()
                                        drawing_set_for_applicability = Drawing.objects.all()
                                        is_used_flag = True

                if not is_used_flag:
                    if dr.applicability == '':
                        dr.applicability = dr_2.article
                    elif dr_2.article not in dr.applicability.split('\n'):
                        dr.applicability = dr.applicability + "\n" + dr_2.article
                    dr.save()
                    drawing_set_for_applicability = Drawing.objects.all()


print("Запись в таблицу Drawing значений поля incoming ...")
drawing_set_for_incoming = Drawing.objects.all()
for dra in drawing_set_for_incoming:
    for dra_2 in drawing_set_for_incoming:
        if dra.article in dra_2.applicability.split('\n'):
            if dra_2.article != '':
                if dra.incoming == '':
                    dra.incoming = dra_2.article
                elif dra_2.article not in dra.incoming.split('\n'):
                    dra.incoming = dra.incoming + "\n" + dra_2.article

    dra.save()


print("Запись в таблицу Drawing значений поля structure ...")
drawing_set_for_structure = Drawing.objects.all()

incoming_dict = {}
for d_2 in drawing_set_for_structure:
    incoming_dict[d_2.article] = d_2.incoming

structure_dict = {}

for incoming_key in incoming_dict.keys():

    checked = set()
    for_check = set()

    for_check.update(incoming_dict[incoming_key].split('\n'))

    incoming_dict_keys = []
    for key in incoming_dict:
        incoming_dict_keys.append(key)

    while len(for_check) > 0:
        first_elem_for_check = for_check.pop()
        if first_elem_for_check in incoming_dict_keys:
            for_check.update(incoming_dict[first_elem_for_check].split('\n'))
            incoming_dict_keys.remove(first_elem_for_check)
        checked.add(first_elem_for_check)

    structure_dict[incoming_key] = '\n'.join(str(s) for s in checked)

for d_3 in drawing_set_for_structure:
    d_3.structure = structure_dict[d_3.article]
    d_3.save()


print('Запись результатов в drawings.xlsx ...')
all_draw_set = Drawing.objects.all()
book = xlsxwriter.Workbook("drawings.xlsx")
sheet = book.add_worksheet('Лист1')
header = book.add_format({'bold': True, 'fg_color': '#D7E4BC', 'border': 1})
center = book.add_format({'align': 'center'})
sheet.write(0, 0, "name", header)
sheet.write(0, 1, "article", header)
sheet.write(0, 2, "applicability", header)
sheet.write(0, 3, "incoming", header)
sheet.write(0, 4, "structure", header)
j = 1
for the_draw in all_draw_set:
    sheet.write(j, 0, the_draw.name)
    sheet.write(j, 1, the_draw.article)
    sheet.write(j, 2, the_draw.applicability)
    sheet.write(j, 3, the_draw.incoming)
    sheet.write(j, 4, the_draw.structure)
    j += 1
book.close()
"""
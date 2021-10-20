from django.contrib import admin
from django.urls import path

from dbapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page, name='main_page'),
    path('search/', views.text_search, name='text_search'),

]

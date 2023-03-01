from django.urls import path
from . import views
 
urlpatterns = [
    path('', views.nikkei_225, name='nikkeki_225'),
]
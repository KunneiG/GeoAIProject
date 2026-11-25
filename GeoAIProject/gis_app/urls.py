from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/get-data/', views.get_data, name='get_data'),
    path('api/ask-ai/', views.ask_ai, name='ask_ai'),
]
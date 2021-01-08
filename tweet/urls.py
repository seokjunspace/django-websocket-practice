from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.test_list, name='test'),
    path('<str:room_name>/', views.room, name='room'),
]
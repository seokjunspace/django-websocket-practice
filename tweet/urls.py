from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.test_list, name='test'),
    # path('show/', views.tweetView.as_view()),
    # path('page/', views.tweet_function_view),
    path('<str:room_name>/', views.room, name='room'),
]
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('motivation-reel', views.create_reel, name='create_motivation'),
    path('onePic-reel/', views.create_onePic, name='create_onePic'),
    path('create-split-video/', views.create_split_video, name='create_split_video'),
    path('create-oneVid-video/', views.create_oneVid, name='create-oneVid'),
    path('create-oneCustomVid/', views.create_oneVidCustom, name='create-oneCustomVid'),
    path('clipAnything/', views.clipAnything, name='clipAnythingLINK'),
    path('', views.homePage, name='home'),
    path('register/', views.register, name='register'),  # Registration view
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('my_videos/', views.my_videos, name='my_videos'),
    path('clip_anything/', views.clipAnything, name='clip_anything'),
]
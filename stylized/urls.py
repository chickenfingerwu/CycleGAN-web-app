from django.urls import path

from . import views

urlpatterns = [
    path('', views.style_transfer_image, name='style_transfer_image'),
]

from django.urls import path, include

from .views import Homeresposta, Upload_success, Homepageupload

urlpatterns = [
    path("", Homepageupload.as_view(),name='homepage'),
    path('upload/', Homepageupload.as_view(), name='upload'),
    path('resposta/', Homeresposta.as_view(), name='resposta'),
    path('upload_success/', Upload_success.as_view(), name='upload_success'),
]
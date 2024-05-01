from django.urls import path, include
from . import views
from .views import Homepageupload, Homeresposta

urlpatterns = [
    path("", Homepageupload.as_view(), name='homepage'),
    path("uploaded/<int:id>/", Homeresposta.as_view(), name='uploaded_text'),

]

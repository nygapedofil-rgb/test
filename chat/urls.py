from django.urls import path
from . import views



urlpatterns = [
    path('api/login/',views.api_login,),
    path('api/set_public_key/',views.api_set_public_key),
    path('api/get_public_key/',views.api_get_public_key),
]


from django.urls import path
from locations.views import newLocation

app_name = 'locations'
urlpatterns = [
    path('addlocation/', newLocation, name='newLocation'),
]

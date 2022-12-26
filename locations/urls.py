
from django.urls import path
from locations.views import newLocation, index

app_name = 'locations'
urlpatterns = [
    path('addlocation/', newLocation, name='newLocation'),
    path('', index, name='index')
]

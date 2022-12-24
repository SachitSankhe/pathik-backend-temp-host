from django.shortcuts import render
from django.contrib import messages
from users.models import User
from rest_framework.decorators import api_view
from users.models import User
from .models import Location
from rest_framework.response import Response
from .serializers import LocationSerializer
# from rest_framework.response import Response
# from .forms import locationForm
# Create your views here.

# remove GET request


@api_view(['GET', 'POST'])
def newLocation(request):
    if request.method == "POST":
        try:
            adminusername = request.POST.get('locationAdmin')
            admin = User.objects.get(username=adminusername)
            data = {
                'name': request.POST.get('locationName'),
                'address': request.POST.get('locationAddress'),
                'description': request.POST.get('locationDescription'),
                'images': request.FILES.get('locationImg'),
                'admin': admin.pk,
                'status': request.POST.get('locationStatus')
            }
            print(data)

        except Exception as e:
            return Response({
                'detail': "first" + str(e)
            }, status=400)

        location = LocationSerializer(data=data)

        if location.is_valid():
            data['admin'] = admin
            print(data)
            newlocation = Location(name=data['name'], address=data['address'],
                                   description=data['description'], admin=data['admin'], images=data['images'], status=data['status'])
            newlocation.save()
            return Response({
                'detail': 'Location added succesfully'
            }, status=200)
        else:
            return Response({
                'detail': location.errors
            }, status=400)

    else:
        return render(request, 'locationform.html')

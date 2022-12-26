from django.shortcuts import render
from django.contrib import messages
from users.models import User
from rest_framework.decorators import api_view
from users.models import User
from .models import Location
from rest_framework.response import Response
from .serializers import LocationSerializer
import json
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.

# remove GET request


@api_view(['POST'])
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
                'detail': "Either field name is wrong or locationAdmin is not registered -> Specific error is :" + str(e)
            }, status=400)

        location = LocationSerializer(data=data)

        if location.is_valid():
            data['admin'] = admin
            print(data)
            try:
                newlocation = Location(name=data['name'], address=data['address'],
                                       description=data['description'], admin=data['admin'], images=data['images'], status=data['status'])
                newlocation.save()
                return Response({
                    'detail': 'Location added successfully'
                }, status=200)
            except Exception as e:
                return Response({
                    'detail': "Error while saving the location in the database -> Specific error is : " + str(e)
                }, status=500)
        else:
            return Response({
                'detail': location.errors
            }, status=400)

    else:
        return render(request, 'locationform.html')


@api_view(['GET'])
def index(request):
    try:
        locations = Location.objects.all().values()
        print(locations)
        return Response({
            # 'locations': json.dumps(list(locations), cls=DjangoJSONEncoder)
            'locations': locations
        }, status=200)
    except Exception as e:
        return Response({
            'detail': str(e)
        }, status=500)

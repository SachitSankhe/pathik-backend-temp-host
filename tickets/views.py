from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view
from users.models import User
from locations.models import Location
from .serializers import TicketSerializer
from .models import Ticket
from users.decorators import login_required
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest
import json

# Create your views here.
from instamojo_wrapper import Instamojo

# remove GET request


@login_required
@api_view(['GET', 'POST'])
def bookTicket(request):
    if request.method == "POST":
        try:
            user = User.objects.get(username=request.POST.get('user'))
            location = Location.objects.get(name=request.POST.get('location'))
            data = ({
                'user': user.pk,
                'location': location.pk,
                'date': request.POST.get('date'),
                'quantity': request.POST.get('quantity'),
                'amount': request.POST.get('amount'),
            })
        except Exception as e:
            return Response({
                'detail': str(e)
            }, status=400)

        ticket = TicketSerializer(data=data)
        if ticket.is_valid():
            # Getting all the items from the frontend after validation
            data = ({
                'user': user,
                'location': location,
                'date': data['date'],
                'quantity': data['quantity'],
                'amount': data['amount'],
            })
            print(data['amount'], " ", data['user'])

            try:
                # Creating Instamojo Client and Order id
                client = Instamojo(api_key=settings.API_KEY, auth_token=settings.AUTH_TOKEN,
                                   endpoint='https://test.instamojo.com/api/1.1/')
                print(HttpRequest.get_full_path)
                redirect_url = str(
                    "https://" + str(HttpRequest.get_host(request)) + "/api/payment/paymentstatus/")

                # redirect_url = str(
                #     HttpRequest.get_full_path + "/api/payment/paymentstatus/")

                payment_response = client.payment_request_create(
                    amount=data['amount'],
                    purpose='Buying a ticket',
                    buyer_name=data['user'].username,
                    email=data['user'].email,
                    send_email=True,
                    redirect_url=redirect_url,
                    allow_repeated_payments=False,
                )
                print(payment_response)
                order_id = payment_response['payment_request']['id']
                tempTicket = Ticket.objects.get_or_create(user=data['user'], location=data['location'],
                                                          date=data['date'], quantity=data['quantity'], amount=data['amount'], payment_id=order_id)
            except Exception as e:
                return Response({
                    'detail': str(e)
                }, status=500)

            return Response({
                'detail': "Successfully payment link generated.",
                'link': payment_response['payment_request']['longurl'],
            }, status=200)
            # return render(request, 'form.html', {'payment_url': payment_response['payment_request']['longurl'], 'button': "hide-button", 'field': "disable-field"})

        return Response({
            'detail': ticket.errors
        }, status=400)
    else:
        pass


@login_required
@api_view(['GET', 'POST'])
def book_Ticket(request, locationID):
    if request.method == "POST":
        try:
            user = User.objects.get(username=request.POST.get('user'))
            location = Location.objects.get(name=request.POST.get('location'))
            data = ({
                'user': user.pk,
                'location': location.pk,
                'date': request.POST.get('date'),
                'quantity': request.POST.get('quantity'),
                'amount': request.POST.get('amount'),
            })
        except Exception as e:
            return Response({
                'detail': str(e)
            }, status=400)

        ticket = TicketSerializer(data=data)
        if ticket.is_valid():
            # Getting all the items from the frontend after validation
            data = ({
                'user': user,
                'location': location,
                'date': data['date'],
                'quantity': data['quantity'],
                'amount': data['amount'],
            })
            print(data['amount'], " ", data['user'])

            try:
                # Creating Instamojo Client and Order id
                client = Instamojo(api_key=settings.API_KEY, auth_token=settings.AUTH_TOKEN,
                                   endpoint='https://test.instamojo.com/api/1.1/')

                redirect_url = str(
                    "https://" + str(HttpRequest.get_host(request)) + "/api/payment/paymentstatus/")

                payment_response = client.payment_request_create(
                    amount=data['amount'],
                    purpose='Buying a ticket',
                    buyer_name=data['user'].username,
                    email=data['user'].email,
                    send_email=True,
                    redirect_url=redirect_url,
                    allow_repeated_payments=False,
                )
                print(payment_response)
                order_id = payment_response['payment_request']['id']
                tempTicket = Ticket.objects.get_or_create(user=data['user'], location=data['location'],
                                                          date=data['date'], quantity=data['quantity'], amount=data['amount'], payment_id=order_id)
            except Exception as e:
                return Response({
                    'detail': str(e)
                }, status=500)

            return render(request, 'form.html', {'payment_url': payment_response['payment_request']['longurl'], 'button': "hide-button", 'field': "disable-field"})

        return Response({
            'detail': ticket.errors
        }, status=400)
    else:
        if locationID is None:
            return render(request, 'form.html', {'button': "", 'field': ""})
        else:
            location = Location.objects.get(pk=locationID)
            print(location)
            return render(request, 'form.html', {"locationName": str(location.name), 'button': "", 'field': ""})



@api_view(['GET'])
@login_required
def index(request):
    print(request.headers)
    print(request.user)
    tickets = Ticket.objects.filter(user=request.user).values()[:]
    print(list(tickets))
    return Response({
        'detail': json.dumps(list(tickets), cls=DjangoJSONEncoder)
    }, status=200)

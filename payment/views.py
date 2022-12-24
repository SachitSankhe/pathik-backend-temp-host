from django.shortcuts import render
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import Payment
from django.http import HttpResponse
from tickets.models import Ticket
from instamojo_wrapper import Instamojo
from django.conf import settings
import cloudinary
import cloudinary.uploader
import cloudinary.api
from .serializers import PaymentSerializer
# from users.utils import send_qrcode

from django.core.mail import send_mail
from django.template.loader import render_to_string
# Create your views here.

# app_name = "payment"

# Completing the payment request,saving a Payment instance and sending a email with QR code


@api_view(['GET'])
def completePayment(request):
    try:
        ticket = Ticket.objects.get(
            payment_id=request.GET.get('payment_request_id'))
        data = {
            'payment_request_id': request.GET.get('payment_request_id'),
            'payment_status': request.GET.get('payment_status'),
            'payment_id': request.GET.get('payment_id'),
            'ticket': ticket.pk,
        }
    except Exception as e:
        return Response({
            'detail': 'Problem with ticket querying -> '+str(e)
        }, status=400)

    payment_object = PaymentSerializer(data=data)

    if payment_object.is_valid():
       # Creating a client to verify payment request.
        data['ticket'] = Ticket.objects.get(pk=data['ticket'])
        try:
            client = Instamojo(api_key=settings.API_KEY,
                               auth_token=settings.AUTH_TOKEN,
                               endpoint='https://test.instamojo.com/api/1.1/')
            response = client.payment_request_payment_status(
                data['payment_request_id'], data['payment_id'])
            print(response)
        except Exception as e:
            return Response({
                'detail': "Payment problem ->" + str(e)
            }, status=500)

        # Checking if payment has been successfully completed
        if (data['payment_status'] == 'Credit' and response['payment_request']['status'] == 'Completed'):
            try:
                data['ticket'].paid = True
                data['ticket'].save()
                payment = Payment(payment_request_id=data['payment_request_id'],
                                  payment_id=data['payment_id'], ticket=data['ticket'], response=response)
                payment.save()
            except Exception as e:
                return Response({
                    'detail': str(e)
                }, status=500)

            user = data['ticket'].user

            config = cloudinary.config(secure=True)

            # Creating a payment response for QRcode
            payment_response = {
                'ID': str(payment.ID),
                # 'user_id': user.id,
                # 'ticket_id': ticket.id,
                # 'quantity': ticket.quantity,
                # 'order_id': payment_request_id,
                # 'payment_id': payment_id,
            }

            # Using a API for QR code generation
            link = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + \
                str(payment_response)

            # Sending a mail
            try:
                msg_plain = render_to_string('email.txt')
                msg_html = render_to_string(
                    'confirmationEmail.html', {'date': data['ticket'].date, 'location': data['ticket'].location, 'link': link})

                send_mail("Confirmation email",
                          msg_plain,
                          settings.EMAIL_HOST_USER,
                          [user.email],
                          html_message=msg_html)
            except Exception as e:
                return Response({
                    'detail': 'Problem with the email service -> ' + str(e)
                }, status=503)

            # Rendering successfull payment page
            return render(request, 'success.html')
        else:
            return HttpResponse("Some error occured. Payment not successful any money deducted will be refunded within 5 to 7 days")
    else:
        return Response({
            'detail': payment_object.errors
        }, status=500)

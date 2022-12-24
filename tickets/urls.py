from django.urls import path
from .views import bookTicket, book_Ticket, index

app_name = 'ticket'

urlpatterns = [
    path('bookticket/', bookTicket, name='bookTicket'),
    path('bookticket/<int:locationID>/', book_Ticket, name='book_Ticket'),
    path('', index, name='index')
]

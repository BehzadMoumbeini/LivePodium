from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from events.models import Event
from .models import Order, Ticket
from mollie.api.client import Client
from mollie.api.error import Error as MollieError  # Correct import


@login_required
def create_order(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        quantity = int(request.POST['quantity'])
        total = event.price * quantity
        
        order = Order.objects.create(
            user=request.user,
            event=event,
            quantity=quantity,
            total_price=total
        )
        
        checkout_url = order.create_mollie_payment(request)
        return redirect(checkout_url)
    
    return redirect('event_detail', pk=event_id)


def order_success(request, order_uuid):
    order = get_object_or_404(Order, order_id=order_uuid)
    return render(request, 'order_success.html', {'order': order})


@csrf_exempt
def mollie_webhook(request):
    if request.method == 'POST':
        payment_id = request.POST.get('id')
        if not payment_id:
            return HttpResponse(status=400)
        
        mollie_client = Client()
        mollie_client.set_api_key(settings.MOLLIE_API_KEY)
        
        try:
            payment = mollie_client.payments.get(payment_id)
            order_id = payment.metadata['order_id']
            order = Order.objects.get(order_id=order_id)
            
            if payment.is_paid() and order.status != 'paid':
                order.status = 'paid'
                order.save()
                
                # Generate individual tickets with QR codes
                tickets = []
                for _ in range(order.quantity):
                    ticket = Ticket.objects.create(order=order)
                    ticket.generate_qr()
                    tickets.append(ticket)
                
                # Send confirmation email with embedded + attached QR codes
                subject = f"Je tickets voor {order.event.title} - LivePodium"
                html_content = render_to_string('emails/ticket_confirmation.html', {
                    'user': order.user,
                    'event': order.event,
                    'quantity': order.quantity,
                    'total_price': order.total_price,
                    'tickets': tickets,
                })
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email='LivePodium <noreply@livepodium.nl>',
                    to=[order.user.email],
                )
                email.attach_alternative(html_content, "text/html")

                # Attach and embed QR codes using CID
                for idx, ticket in enumerate(tickets, start=1):
                    if ticket.qr_code:
                        with ticket.qr_code.open('rb') as img_file:
                            img_data = img_file.read()
                        cid = f"ticket_{idx}.png"
                        email.attach(cid, img_data, 'image/png')
                        # Embed in HTML using CID
                        email.attach_alternative(
                            f'<img src="cid:{cid}" alt="QR Ticket {idx}" style="width:250px;height:250px;">',
                            "text/html"
                        )

                email.send(fail_silently=False)
                
            elif payment.is_failed() or payment.is_canceled():
                order.status = 'failed' if payment.is_failed() else 'cancelled'
                order.save()
                
        except MollieError:
            # Log this in production (e.g., with logging module)
            pass
    
    return HttpResponse(status=200)


@login_required
def my_tickets(request):
    """
    View to display all paid tickets for the logged-in user.
    Shows orders with individual QR codes.
    """
    orders = Order.objects.filter(user=request.user, status='paid').order_by('-created_at')
    return render(request, 'tickets/my_tickets.html', {'orders': orders})
from django.db import models
from django.contrib.auth.models import User
from events.models import Event
from django.conf import settings
from mollie.api.client import Client
import qrcode
from io import BytesIO
from django.core.files import File
import uuid


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    mollie_payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def get_absolute_url(self):
        return f"/order/success/{self.order_id}/"

    def create_mollie_payment(self, request):
        mollie_client = Client()
        mollie_client.set_api_key(settings.MOLLIE_API_KEY)

        payment = mollie_client.payments.create({
            "amount": {
                "currency": "EUR",
                "value": f"{self.total_price:.2f}"
            },
            "description": f"{self.quantity} ticket(s) voor {self.event.title}",
            "redirectUrl": request.build_absolute_uri(self.get_absolute_url()),
            "webhookUrl": request.build_absolute_uri('/tickets/webhook/'),
            "metadata": {
                "order_id": str(self.order_id)
            },
        })
        self.mollie_payment_id = payment.id
        self.save()
        return payment.get_checkout_url()

    def __str__(self):
        return f"Order {self.order_id} - {self.event.title} ({self.quantity} tickets)"


class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)

    def generate_qr(self):
        data = f"LivePodium Ticket\nOrder: {self.order.order_id}\nEvent: {self.order.event.title}\nDate: {self.order.event.date}\nHolder: {self.order.user.username}"
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        filename = f"ticket_{self.order.order_id}_{self.id}.png"
        self.qr_code.save(filename, File(buffer), save=True)

    def __str__(self):
        return f"Ticket for Order {self.order.order_id}"
from django.contrib import admin
from django.urls import path, include
from events.views import HomeView, EventDetailView
from tickets.views import create_order, order_success, mollie_webhook, my_tickets
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    return HttpResponse("""
        <!DOCTYPE html>
        <html lang="nl">
        <head>
            <meta charset="UTF-8">
            <title>LivePodium</title>
            <style>
                body { font-family: sans-serif; background: #f3f4f6; text-align: center; padding-top: 100px; }
                h1 { font-size: 3.5rem; color: #1d4ed8; }
                p { font-size: 1.8rem; }
                a { font-size: 1.5rem; color: #1d4ed8; text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>LivePodium is running successfully! 🎉</h1>
            <p>your platform is up and running.</p>
            <p>NB) In production, set a strong, unique SECRET_KEY as an environment variable (never hardcode it in settings.py or commit it to version control), and ensure DEBUG = False for security.</p>
            <p><a href="/admin/">go to Admin</a> to add events.</p>
        </body>
        </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('event/<int:event_id>/order/', create_order, name='create_order'),
    path('order/success/<uuid:order_uuid>/', order_success, name='order_success'),
    path('tickets/webhook/', mollie_webhook, name='mollie_webhook'),
    path('my-tickets/', my_tickets, name='my_tickets'),
    # Auth URLs
    path('accounts/', include('django.contrib.auth.urls')),  # Login, logout, password change/reset
    path('register/', include('users.urls')),  # We'll create this for registration
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
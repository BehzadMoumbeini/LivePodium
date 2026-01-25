from django.views.generic import ListView, DetailView
from .models import Event

class HomeView(ListView):
    model = Event
    template_name = 'home.html'
    context_object_name = 'events'
    queryset = Event.objects.filter(is_local=True).order_by('date')

class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'  # We'll create this next
    context_object_name = 'event'
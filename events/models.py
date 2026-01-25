from django.db import models

class Venue(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=300)

class Event(models.Model):
    title = models.CharField(max_length=300)
    artist = models.CharField(max_length=200)
    date = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_local = models.BooleanField(default=True)  # Focus on NL indie
    image = models.ImageField(upload_to="events/", null=True, blank=True)
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse

# Create your models here.
class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name="conversations")

    def get_absolute_url(self):
        return reverse('convo', args=[str(self.id)])

    def __str__(self):
        return '{}'.format(self.participants.values_list('username', flat=True))

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="sender", null = True)
    receiver = models.ManyToManyField(User, related_name="receivers")
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    text = models.CharField(max_length=2048)
    datetime = models.DateTimeField(auto_now_add=True)
    ordering = ["-datetime"]

    def __str__(self):
        return '{}: {}'.format(self.sender.username, self.text)
from django import forms
from django.contrib.auth.models import User

from .models import Conversation, Message

class ConversationCreateForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user')
    #     # self.q = kwargs.pop('q')
    #     super(ConversationCreateForm, self).__init__(*args, **kwargs)
    #     # if self.q:
    #     #     self.fields['participants'].queryset = User.objects.filter(username__icontains=self.q)

    # def clean_participants(self):
    #     data = self.cleaned_data.get('participants')
    #     if not self.user in data:
    #         data |
    #     return data

    class Meta:
        model = Conversation
        fields = {'participants'}
        widgets = {
            'participants': forms.CheckboxSelectMultiple()
        }

class MessageCreateForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = {'text', 'sender', 'conversation', 'receiver'}
        widgets = {
            'text': forms.Textarea(attrs={'rows':2,}), 
            'sender': forms.HiddenInput(),
            'conversation': forms.HiddenInput(),
            'receiver': forms.MultipleHiddenInput()
        }
        labels = {'text': ''}
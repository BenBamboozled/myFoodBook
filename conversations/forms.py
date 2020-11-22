from django import forms

from .models import Conversation, Message

class ConversationCreateForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = {'participants'}
        # widgets = {
        #     'participants': forms.CheckboxSelectMultiple()
        # }

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
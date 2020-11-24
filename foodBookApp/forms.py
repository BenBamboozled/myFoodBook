from django import forms 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Post,  Profile, Comment
from dal import autocomplete

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username','email','password1','password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username','email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['privacy', 'profilePic', 'bio']

class UpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields=['image','body', 'tags' , 'privacy']
        widgets = {
            'body': forms.Textarea(attrs={'rows':3,}),
            'tags': autocomplete.TaggitSelect2(url='tags-autocomplete'),
        }

class SearchForm(forms.Form):
    query = autocomplete.TaggitSelect2(url='tags-autocomplete')


class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']





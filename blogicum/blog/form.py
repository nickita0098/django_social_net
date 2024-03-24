from django import forms
from .models import Comments, Post, User


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'pub_date', 'location', 'image')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'email')

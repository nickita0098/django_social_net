from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .form import UserForm

User = get_user_model()


class UserCreateView(CreateView):
    model = User
    template_name = 'registration/registration_form.html'
    form_class = UserForm
    success_url = reverse_lazy('blog:index')

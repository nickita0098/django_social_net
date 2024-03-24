from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import include, path, reverse_lazy
from django.conf.urls.static import static
from django.conf import settings

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.internal_server_error'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', CreateView.as_view(
        template_name='registration/registration_form.html',
        form_class=UserCreationForm,
        success_url=reverse_lazy('blog:index')), name='registration'),
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    path('', include('blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

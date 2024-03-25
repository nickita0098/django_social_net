from django.contrib import admin
from django.urls import include, path
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from .views import UserCreateView

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.internal_server_error'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', UserCreateView.as_view(), name='registration'),
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    path('', include('blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

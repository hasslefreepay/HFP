
from django.contrib import admin
from django.urls import path, include
from email_services.api.views import EmailApiView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('adminuser.api.urls')),
    path('send-email/', EmailApiView.as_view(), name='send-email'),
]

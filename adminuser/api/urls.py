from rest_framework.routers import DefaultRouter
from django.urls import path
from adminuser.api.view import userviewset, transferenciasviewset, transferenciasBancosViewset, importeViewset, \
    envioViewset, estadisticas
from adminuser.api.view import mvviewset
from adminuser.api.views_user import UserValidationAPIView  # Asegúrate de que este archivo exista
from adminuser.api.view import TarjetaListView
from adminuser.api.view import CrearTarjeta
from adminuser.api.view import viewUser

# Configuración del enrutador
router = DefaultRouter()
router.register(r'users', userviewset, basename='user')
router.register(r'mv', mvviewset, basename='mv')
router.register(r'transferencias', transferenciasviewset, basename='transferencias')
router.register(r'transferenciasBancos', transferenciasBancosViewset, basename='transferenciasBancos')
router.register(r'notificacion', transferenciasviewset, basename='notificacion')
router.register(r'importe', importeViewset, basename='importe')
router.register(r'envio', envioViewset, basename='envio')
router.register(r'estadisticas', estadisticas, basename='estadisticas')

# Definición de las URLs
urlpatterns = [
    path('validate_user/', UserValidationAPIView.as_view(), name='validate_user'),  # Corrige la ruta si es necesario
    path('vertarjetas/<int:user_id>/', TarjetaListView.as_view(), name='tarjeta-list'),
    path('datos/', viewUser.as_view(), name='userm'),  # Corrige la ruta si es necesario
    path('tarjetas/', CrearTarjeta.as_view(), name='tarjeta-create'),
] + router.urls

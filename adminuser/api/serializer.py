from rest_framework import serializers
from adminuser.models import user, trasferencias, trasferencias_Bancos, notificacion, envio, importe
from adminuser.models import Tarjeta
from adminuser.models import mv

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model=user
        fields='__all__'
        
        

class Tarjetaserializer(serializers.ModelSerializer):
    class Meta:
        model=Tarjeta
        fields='__all__'


class mvserializer(serializers.ModelSerializer):
    class Meta:
        model=mv
        fields='__all__'


class transferenciaserializer(serializers.ModelSerializer):
    class Meta:
        model=trasferencias
        fields='__all__'

class transferenciasBancosSerializer(serializers.ModelSerializer):
    class Meta:
        model=trasferencias_Bancos
        fields='__all__'

class notificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model=notificacion
        fields='__all__'


class envioSerializer(serializers.ModelSerializer):
    class Meta:
        model=envio
        fields='__all__'

class importeSerializer(serializers.ModelSerializer):
    class Meta:
        model=importe
        fields='__all__'
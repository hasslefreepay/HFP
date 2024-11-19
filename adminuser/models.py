# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, correo, password, **extra_fields):
        if not correo:
            raise ValueError('El correo debe ser proporcionado')
        if not password:
            raise ValueError('La contraseña debe ser proporcionada')

        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)  # Encripta y guarda la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(correo, password, **extra_fields)


class user(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    correo = models.EmailField(max_length=50, unique=True)
    telefono = models.BigIntegerField(null=True)
    pais = models.CharField(max_length=50)
    departamento = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    codp = models.IntegerField( null=True)
    saldo = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre', 'apellidos']

    def __str__(self):
        return self.correo

    
class Tarjeta(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    nombre= models.CharField(max_length=50)
    numero = models.BigIntegerField()  # Usualmente las tarjetas tienen 16 dígitos
    cvv = models.IntegerField()      # Generalmente el CVV es de 3 dígitos
    fecha_ano = models.PositiveIntegerField() # Año de expiración
    fecha_mes = models.PositiveIntegerField() # Mes de expiración
    apodo=models.CharField(max_length=20, null=True, blank=True)


class mv(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    destino=models.CharField(max_length=100, null=True, blank=True)
    tarjeta=models.CharField(max_length=20, null=True, blank=True)
    cantidad = models.BigIntegerField(null=True, blank=True)
    fecha=models.DateTimeField()
    tipo=models.TextField(max_length=20)
    estado=models.TextField(max_length=20)


class trasferencias(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    tarjeta=models.CharField(max_length=100, )
    destino=models.CharField(user,max_length=100, )
    cantidad = models.BigIntegerField(null=True,)
    fecha=models.DateTimeField()
    estado=models.TextField(max_length=20, default='pendiente')


class trasferencias_Bancos(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    tarjeta=models.CharField(max_length=100, )
    banco=models.CharField(max_length=100,)
    cuenta=models.CharField(max_length=100,)
    nombre=models.CharField(max_length=100,)
    cantidad = models.BigIntegerField(null=True,)
    fecha=models.DateTimeField()
    estado=models.TextField(max_length=20, default='pendiente')



class notificacion(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    mensaje=models.TextField(max_length=100)
    fecha=models.DateTimeField(null=True,)

class envio(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    provenir=models.CharField(user,max_length=100, )
    cantidad = models.BigIntegerField(null=True,)
    fecha=models.DateTimeField()
    estado=models.TextField(max_length=20, default='aprovado')


class importe(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    tarjeta=models.CharField(max_length=100, )
    cantidad = models.BigIntegerField(null=True,)
    fecha=models.DateTimeField()

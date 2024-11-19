from rest_framework import viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminuser.models import user, trasferencias, trasferencias_Bancos, notificacion, envio, importe
from adminuser.api.serializer import Userserializer, transferenciaserializer, transferenciasBancosSerializer, \
    notificacionSerializer, envioSerializer, importeSerializer
from adminuser.models import Tarjeta
from adminuser.models import mv
from adminuser.api.serializer import mvserializer
from adminuser.api.serializer import Tarjetaserializer
from rest_framework.permissions import IsAuthenticated
from adminuser.api.permissions import IsAuthenticatedOrReadOnly, escribir



import pytz
from django.utils import timezone

# Obtén la zona horaria local
timezone_name = pytz.timezone('UTC')
hora_actual = timezone.now().astimezone(timezone_name).date()


class userviewset(viewsets.ModelViewSet):
    queryset=user.objects.all()
    serializer_class=Userserializer
    permission_classes = [escribir]

    def list(self, request, *args, **kwargs):
        return Response({'detail': 'GET method is not allowed.'}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, *args, **kwargs):
        return Response({'detail': 'GET method is not allowed.'}, status=status.HTTP_403_FORBIDDEN)

    

class mvviewset(viewsets.ModelViewSet):
    queryset=mv.objects.all()
    serializer_class=mvserializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra los objetos según el ID del usuario autenticado
        user = self.request.user
        return mv.objects.filter(user_id=user.id)

class TarjetaListView(generics.ListAPIView):
    serializer_class = Tarjetaserializer
    permission_classes = []

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Tarjeta.objects.filter(user_id=user_id)
    

class CrearTarjeta(generics.CreateAPIView):
    queryset = Tarjeta.objects.all()
    serializer_class = Tarjetaserializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            card_number = serializer.validated_data['numero']
            print(card_number)
            if validate_card(card_number):
                print('Hora actual:', timezone.now().strftime('%Y-%m-%d %H:%M:%S'))
                tarjeta = serializer.save()  # Guarda la tarjeta en la base de datos
                mv_data = {
                    'user': request.user.id,  # Asocia el movimiento al usuario autenticado
                    'destino': tarjeta.nombre,  # Cambia según lo que necesites
                    'tarjeta': tarjeta.id,  # O el número de la tarjeta si así lo prefieres
                    'cantidad': 0,  # Cambia según lo que necesites
                    'fecha':  timezone.now(),  # Cambia según la lógica de tu negocio
                    'tipo': "Registro de tarjeta",  # O el tipo que necesites
                    'estado': "exitoso"  # O el estado que necesites
                }
                mv_serializer = mvserializer(data=mv_data)
                mv_serializer.is_valid(raise_exception=True)
                mv_serializer.save()  # Guarda el movimiento en la base de datos
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'La tarjeta no es válida.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({' tengo un error aqui': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    
    
class viewUser(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        
        try:
            user_instance = user.objects.get(id=id)
            serializer = Userserializer(user_instance)  # Serializa el usuario encontrado
            return Response(serializer.data, status=status.HTTP_200_OK)      
        except user.DoesNotExist:
            return Response({'exists': False}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return Response({'detail': 'POST method is not allowed.'}, status=status.HTTP_403_FORBIDDEN)


def validate_card(card_number):
    # Convertir el número de tarjeta a cadena y luego en una lista de dígitos
    digits = [int(d) for d in str(card_number)][::-1]

    # Duplicar cada segundo dígito desde la derecha
    for i in range(1, len(digits), 2):
        digits[i] *= 2
        # Si el resultado es mayor que 9, restar 9
        if digits[i] > 9:
            digits[i] -= 9

    # Sumar todos los dígitos
    total = sum(digits)

    # El número es válido si la suma es múltiplo de 10
    return total % 10 == 0



class transferenciasviewset(viewsets.ModelViewSet):
    queryset=trasferencias.objects.all()
    serializer_class=transferenciaserializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra los objetos según el ID del usuario autenticado
        user2 = self.request.user
        return trasferencias.objects.filter(user_id=user.user)

    def create(self, request, *args, **kwargs):
        # Obtiene el usuario autenticado
        user2 = request.data.get('user')
        # Obtiene el monto a transferir
        cantidad = request.data.get('cantidad')
        # Obtiene el destinatario
        destino = request.data.get('destino')
        # Obtiene la tarjeta de origen
        tarjeta = request.data.get('tarjeta')
        # Obtiene la fecha actual
        fecha = timezone.now()

        # Obtiene el estado de la transferencia


        # Crea un diccionario con los datos de la transferencia
        transferencia_data = {
            'user': user2,
            'destino': destino,
            'tarjeta': tarjeta,
            'cantidad': cantidad,
            'fecha': fecha,
            'estado': 'exitoso'

        }

        # Serializa los datos de la transferencia
        serializer = transferenciaserializer(data=transferencia_data)
        # Valida los datos
        serializer.is_valid(raise_exception=True)
        comprovarSaldo = user.objects.get(id=user2)

        if tarjeta=='app':

            if comprovarSaldo.saldo > cantidad:
                comprovarSaldo.saldo -= cantidad
                comprovarSaldo.save()
                print(comprovarSaldo.saldo)

                exite = user.objects.filter(correo=destino).exists()


                if exite:
                    agregarSaldo = user.objects.get(correo=destino)
                    print("corro")
                    # Guarda la transferencia en la base de datos
                    agregarSaldo.saldo += cantidad
                    agregarSaldo.save()
                    serializer.save()

                    edata = {
                        'user': user2,
                        'provenir': comprovarSaldo.nombre + ' ' + comprovarSaldo.apellidos,
                        'cantidad': cantidad,
                        'fecha': fecha
                    }
                    serializer3=envioSerializer(data=edata)
                    serializer3.is_valid(raise_exception=True)
                    serializer3.save()

                    ndata = {
                        'user': agregarSaldo.id,
                        'mensaje': 'Se te ha realizado una transferencia de $' + str(cantidad) + ' de ' + comprovarSaldo.nombre + ' ' + comprovarSaldo.apellidos,
                        'fecha': fecha
                    }
                    serializer2 = notificacionSerializer(data=ndata)
                    # Valida los datos
                    serializer2.is_valid(raise_exception=True)

                    # Guarda la notificación en la base de datos
                    serializer2.save()

                    mvdata = {
                        'user': user2,
                        'destino': agregarSaldo.nombre + ' ' + agregarSaldo.apellidos,
                        'tarjeta': tarjeta,
                        'cantidad': cantidad,
                        'fecha': fecha,
                        'tipo': 'Transferencia',
                        'estado': 'exitoso'
                    }
                    serializer4=mvserializer(data=mvdata)
                    serializer4.is_valid(raise_exception=True)
                    serializer4.save()

                    mvdata2 = {
                        'user': agregarSaldo.id,
                        'destino': agregarSaldo.nombre + ' ' + agregarSaldo.apellidos,
                        'tarjeta': tarjeta,
                        'cantidad': cantidad,
                        'fecha': fecha,
                        'tipo': 'Envio',
                        'estado': 'exitoso'
                    }
                    serializer5 = mvserializer(data=mvdata2)
                    serializer5.is_valid(raise_exception=True)
                    serializer5.save()

                    email = user.objects.filter(id=user2).values_list('correo', flat=True).first()
                    destino = agregarSaldo.nombre + ' ' + agregarSaldo.apellidos
                    id_t = serializer.data['id']
                    enviar_transferencia(email, serializer.data['id'], destino, cantidad)

                    # Retorna una respuesta exitosa
                    return Response({'data': serializer.data, 'm': 0}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'El destinatario no existe.', 'm': 1}, status=status.HTTP_200_OK)


            else:
                print(comprovarSaldo.saldo)
                return Response({'error': 'Saldo insuficiente', 'm': 1}, status=status.HTTP_200_OK)

        else:
            exite = user.objects.filter(correo=destino).exists()


            if exite:
                agregarSaldo = user.objects.get(correo=destino)
                agregarSaldo.saldo += cantidad
                agregarSaldo.save()
                # Guarda la transferencia en la base de datos
                serializer.save()
                queryset2 = notificacion.objects.all()
                serializer_class2 = notificacionSerializer
                ndata = {
                    'user': agregarSaldo.id,
                    'mensaje': 'Se te ha realizado una transferencia de $' + str(
                        cantidad) + ' de ' + comprovarSaldo.nombre + ' ' + comprovarSaldo.apellidos,
                    'fecha': fecha
                }
                serializer2 = notificacionSerializer(data=ndata)
                # Valida los datos
                serializer2.is_valid(raise_exception=True)

                # Guarda la notificación en la base de datos
                serializer2.save()

                edata = {
                    'user': agregarSaldo.id,
                    'provenir': comprovarSaldo.nombre + ' ' + comprovarSaldo.apellidos,
                    'cantidad': cantidad,
                    'fecha': fecha
                }
                serializer3 = envioSerializer(data=edata)
                serializer3.is_valid(raise_exception=True)
                serializer3.save()

                mvdata = {
                    'user': user2,
                    'destino': agregarSaldo.nombre + ' ' + agregarSaldo.apellidos,
                    'tarjeta': tarjeta,
                    'cantidad': cantidad,
                    'fecha': fecha,
                    'tipo': 'Transferencia',
                    'estado': 'exitoso'
                }
                serializer4 = mvserializer(data=mvdata)
                serializer4.is_valid(raise_exception=True)
                serializer4.save()

                mvdata2 = {
                    'user': agregarSaldo.id,
                    'destino': agregarSaldo.nombre + ' ' + agregarSaldo.apellidos,
                    'tarjeta': tarjeta,
                    'cantidad': cantidad,
                    'fecha': fecha,
                    'tipo': 'Envio',
                    'estado': 'exitoso'
                }
                serializer5 = mvserializer(data=mvdata2)
                serializer5.is_valid(raise_exception=True)
                serializer5.save()
                email = user.objects.filter(id=user2).values_list('correo', flat=True).first()
                destino = agregarSaldo.nombre + ' ' + agregarSaldo.apellidos
                id_t = serializer.data['id']
                enviar_transferencia(email, serializer.data['id'], destino, cantidad)

                # Retorna una respuesta exitosa
                return Response({'data': serializer.data, 'm': 0}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'El destinatario no existe.', 'm': 1}, status=status.HTTP_200_OK)


class transferenciasBancosViewset(viewsets.ModelViewSet):
    queryset=trasferencias_Bancos.objects.all()
    serializer_class=transferenciasBancosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra los objetos según el ID del usuario autenticado
        user = self.request.user
        return trasferencias_Bancos.objects.filter(user_id=user.id)

    def create(self, request, *args, **kwargs):
        # Obtiene el usuario autenticado
        user2 = request.data.get('user')
        # Obtiene la tarjeta de origen
        tarjeta = request.data.get('tarjeta')
        # Banco de destino
        banco = request.data.get('banco')
        # Cuenta de destino
        cuenta = request.data.get('cuenta')
        # Nombre de destino
        nombre = request.data.get('nombre')
        # Obtiene el monto a transferir
        cantidad = request.data.get('cantidad')
        # Obtiene la fecha actual
        fecha = timezone.now()
        # Obtiene el estado de la transferencia

        # Crea un diccionario con los datos de la transferencia
        transferencia_data = {
            'user': user2,
            'tarjeta': tarjeta,
            'banco': banco,
            'cuenta': cuenta,
            'nombre': nombre,
            'cantidad': cantidad,
            'fecha': fecha,

        }

        # Serializa los datos de la transferencia
        serializer = transferenciasBancosSerializer(data=transferencia_data)
        # Valida los datos
        existe=serializer.is_valid(raise_exception=True)
        comprovarSaldo = user.objects.get(id=user2)

        if tarjeta=='app':

            if comprovarSaldo.saldo > cantidad:
                comprovarSaldo.saldo -= cantidad
                comprovarSaldo.save()
                print(comprovarSaldo.saldo)
                serializer.save()

                mvdata = {
                    'user': user2,
                    'destino': nombre+' Cuenta: '+cuenta,
                    'tarjeta': tarjeta,
                    'cantidad': cantidad,
                    'fecha': fecha,
                    'tipo': 'Transferencia',
                    'estado': 'exitoso'
                }
                serializer4 = mvserializer(data=mvdata)
                serializer4.is_valid(raise_exception=True)
                serializer4.save()
                email = user.objects.filter(id=user2).values_list('correo', flat=True).first()
                destino = nombre + ' Cuenta: ' + cuenta
                id_t = serializer.data['id']
                enviar_transferencia(email, serializer.data['id'], destino, cantidad)
                return Response({'data':serializer.data,'mensaje':'se transfirio'}, status=status.HTTP_201_CREATED)

            else:
                print(comprovarSaldo.saldo)
                return Response({'error': 'Saldo insuficiente', 'm': 1}, status=status.HTTP_200_OK)


        else:
            serializer.save()
            mvdata = {
                'user': user2,
                'destino': nombre + ' Cuenta: ' + cuenta,
                'tarjeta': tarjeta,
                'cantidad': cantidad,
                'fecha': fecha,
                'tipo': 'Transferencia',
                'estado': 'exitoso'
            }
            serializer4 = mvserializer(data=mvdata)
            serializer4.is_valid(raise_exception=True)
            serializer4.save()
            email = user.objects.filter(id=user2).values_list('correo', flat=True).first()
            destino= nombre + ' Cuenta: ' + cuenta
            id_t=serializer.data['id']
            enviar_transferencia(email, serializer.data['id'], destino, cantidad)
            return Response({'data':serializer.data,'mensaje':'se transfirio'}, status=status.HTTP_201_CREATED)


class notificacionviewset(viewsets.ModelViewSet):
    queryset=notificacion.objects.all()
    serializer_class=notificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra los objetos según el ID del usuario autenticado
        user = self.request.user
        return notificacion.objects.filter(user_id=user.id)

    def create(self, request, *args, **kwargs):
        # Obtiene el usuario autenticado
        user = request.data.get('user')
        # Obtiene el mensaje
        mensaje = request.data.get('mensaje')
        # Crea un diccionario con los datos de la notificación
        notificacion_data = {
            'user': user,
            'mensaje': mensaje
        }

        # Serializa los datos de la notificación
        serializer = notificacionSerializer(data=notificacion_data)
        # Valida los datos
        serializer.is_valid(raise_exception=True)
        # Guarda la notificación en la base de datos
        serializer.save()
        # Retorna una respuesta exitosa
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class importeViewset(viewsets.ModelViewSet):
    queryset=importe.objects.all()
    serializer_class=importeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra los objetos según el ID del usuario autenticado
        user = self.request.user
        return importe.objects.filter(user_id=user.id)

    def create(self, request, *args, **kwargs):
        # Obtiene el usuario autenticado
        user2 = request.data.get('user')
        tj = request.data.get('user')
        # Obtiene el monto
        cantidad = request.data.get('cantidad')
        # Obtiene la fecha actual
        fecha = timezone.now()
        # Crea un diccionario con los datos del importe
        importe_data = {
            'user': user2,
            'tarjeta': tj,
            'cantidad': cantidad,
            'fecha': fecha
        }

        # Serializa los datos del importe
        serializer = importeSerializer(data=importe_data)
        # Valida los datos
        serializer.is_valid(raise_exception=True)
        # Guarda el importe en la base de datos
        serializer.save()
        comprovarSaldo = user.objects.get(id=user2)
        comprovarSaldo.saldo += cantidad
        comprovarSaldo.save()

        mvdata = {
            'user': user2,
            'destino': 'Importe',
            'tarjeta': tj,
            'cantidad': cantidad,
            'fecha': fecha,
            'tipo': 'Importe',
            'estado': 'exitoso'
        }
        serializer4 = mvserializer(data=mvdata)
        serializer4.is_valid(raise_exception=True)
        serializer4.save()
        # Retorna una respuesta exitosa
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class envioViewset(viewsets.ModelViewSet):
    queryset=envio.objects.all()
    serializer_class=envioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra los objetos según el ID del usuario autenticado
        user = self.request.user
        return envio.objects.filter(user_id=user.id)

class estadisticas(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = transferenciaserializer


    def list(self, request, *args, **kwargs):
        user2 = request.query_params.get('user')
        print(user2)
        # Obtiene el total de transferencias
        total_transferencias = trasferencias.objects.filter(user_id=user2).count()
        # Obtiene el total de transferencias a bancos
        total_transferencias_bancos = trasferencias_Bancos.objects.filter(user_id=user2).count()
        # Obtiene el total de importes
        total_importes = importe.objects.filter(user_id=user2).count()
        # Obtiene el total de envíos
        total_envios = envio.objects.filter(user_id=user2).count()
        # Obtiene el saldo actual
        saldo = user.objects.get(id=user2).saldo
        # Obtiene el total de movimientos
        total_movimientos = total_transferencias + total_transferencias_bancos + total_importes + total_envios
        # Retorna una respuesta con los datos obtenidos
        hace_un_mes = timezone.now() - timedelta(days=30)

        suma_cantidad = trasferencias.objects.filter(fecha__gte=hace_un_mes, user_id=user2).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        suma_cantidad2 = trasferencias_Bancos.objects.filter(fecha__gte=hace_un_mes, user_id=user2).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        suma_envios = envio.objects.filter(fecha__gte=hace_un_mes, user_id=user2).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        datosmestl=trasferencias.objects.filter(fecha__gte=hace_un_mes, user_id=user2).values('cantidad')
        datosmestx=trasferencias_Bancos.objects.filter(fecha__gte=hace_un_mes, user_id=user2).values('cantidad')

        mm=[]

        for x in datosmestl:
            mm.append(x['cantidad'])

        for x in datosmestx:
            mm.append(x['cantidad'])

        print(mm)

        enviosm = envio.objects.filter(fecha__gte=hace_un_mes, user_id=user2).values('cantidad')

        # Calcula el total de transferencias y el balance
        cantidadT = suma_cantidad + suma_cantidad2
        balance = suma_envios - cantidadT
        porcentaje_uso_tarjeta=calcular_porcentaje_uso_tarjetas_por_usuario(user2)
        meses=calcular_transferencias_por_mes(user2)
        print(meses)
        return Response({'total_transferencias': total_transferencias, 'total_transferencias_bancos': total_transferencias_bancos,
                         'total_importes': total_importes, 'total_envios': total_envios, 'saldo': saldo,
                         'total_movimientos': total_movimientos, 'cantidad_transferida': cantidadT, 'cantidad_recivida': suma_envios, 'balance': balance, 'porcT': porcentaje_uso_tarjeta, 'meses':meses, 'listatm': mm, 'listae':enviosm }, status=status.HTTP_200_OK)


from django.db.models import Count, F, FloatField
from django.db.models.functions import Coalesce, Cast


def calcular_porcentaje_uso_tarjetas_por_usuario(user_id):
    tarjetas = Tarjeta.objects.filter(user_id=user_id).values('numero', 'apodo')
    print(tarjetas)


    # Lista de todas las tarjetas del usuario con apodo o número
    tarjetas_disponibles =[]

    for tarjeta in tarjetas:
        print(f"Número: {tarjeta['numero']}, Apodo: {tarjeta['apodo']}")
        if(tarjeta['apodo']==None or tarjeta['apodo']=='') :
            tarjetas_disponibles.append(str(tarjeta['numero']))
        else:
            tarjetas_disponibles.append(tarjeta['apodo'])

    tarjetas_disponibles.append('app')
    print(f'Tarjetas disponibles: {list(tarjetas_disponibles)}')


    tarjetas = Tarjeta.objects.filter(user_id=user_id).values_list('apodo', 'numero')
    print(tarjetas)

    # Filtra las transferencias para el usuario específico
    total_uso_tarjetas1 = trasferencias.objects.filter(user_id=user_id).count()
    total_uso_tarjetas2 = trasferencias_Bancos.objects.filter(user_id=user_id).count()
    total_uso_tarjetas = total_uso_tarjetas1 + total_uso_tarjetas2
    print(f'total de uso ', total_uso_tarjetas)

    # Agrupa las transferencias y cuenta el uso de cada tarjeta
    tarjetas_porcentaje = (
        trasferencias.objects
        .filter(user_id=user_id)
        .values('tarjeta')
        .annotate(uso_count=Count('tarjeta'))
    )
    print(tarjetas_porcentaje)
    # Si tienes también que considerar las transferencias de 'trasferencias_Bancos', agrégalas
    tarjetas_bancos_porcentaje = (
        trasferencias_Bancos.objects
        .filter(user_id=user_id)
        .values('tarjeta')  # Asegúrate de que 'tarjeta' es un campo en esta tabla
        .annotate(uso_count=Count('tarjeta'))
    )
    print(tarjetas_bancos_porcentaje)
    # Combina ambos resultados en un solo diccionario
    tarjetas_combined = {}


    # Agrega los conteos de 'tarjetas_porcentaje'
    for t in tarjetas_porcentaje:
        tarjeta = t['tarjeta']
        uso_count = t['uso_count']
        tarjetas_combined[tarjeta] = tarjetas_combined.get(tarjeta, 0) + uso_count

    # Agrega los conteos de 'tarjetas_bancos_porcentaje'
    for t in tarjetas_bancos_porcentaje:
        tarjeta = t['tarjeta']
        uso_count = t['uso_count']
        tarjetas_combined[tarjeta] = tarjetas_combined.get(tarjeta, 0) + uso_count
    print(tarjetas_combined)
    # Cálculo del porcentaje de uso por tarjeta
    resultado_final = []
    if total_uso_tarjetas > 0:
        for tarjeta, uso_count in tarjetas_combined.items():
            porcentaje_uso = (uso_count / total_uso_tarjetas) * 100
            resultado_final.append({
                'tarjeta': tarjeta,
                'uso_count': uso_count,
                'porcentaje_uso': porcentaje_uso
            })
    else:
        for tarjeta in tarjetas_combined.keys():
            resultado_final.append({
                'tarjeta': tarjeta,
                'uso_count': 0,
                'porcentaje_uso': 0
            })
    print(tarjetas_combined)
    print('voy')
    print(f'Tarjetas disponibles: {tarjetas_disponibles}')
    # Añade las tarjetas no usadas con porcentaje 0
    uso_count_dict = {tarjeta: 0 for tarjeta in tarjetas_disponibles}
    print(f'uso cont',uso_count_dict)

    for item in resultado_final:
        tarjeta = item['tarjeta']
        uso_count_dict[tarjeta] = item['uso_count']

    resultado_final = [
        {
            'tarjeta': tarjeta,
            'uso_count': uso_count_dict.get(tarjeta, 0),
            'porcentaje_uso': (uso_count_dict.get(tarjeta, 0) / total_uso_tarjetas) * 100 if total_uso_tarjetas > 0 else 0
        }
        for tarjeta in tarjetas_disponibles
    ]

    print(f'Este es el resultado final: ', resultado_final)

    return resultado_final


from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

def calcular_transferencias_por_mes(user):
    # Lista para almacenar los resultados de cada mes en el formato [["mes", tr, ev], ...]
    resultados_mensuales = []

    # Fecha actual
    ahora = timezone.now()

    # Iterar sobre los últimos 12 meses
    for i in range(12):
        # Calcular el mes y año relativo para los últimos 12 meses
        mes_actual = (ahora.month - 1 - i) % 12 + 1
        año_actual = ahora.year - (1 if (ahora.month - 1 - i) < 0 else 0)

        # Calcular el primer y último día del mes
        primer_dia_mes = ahora.replace(day=1, month=mes_actual, year=año_actual)
        if mes_actual == 12:
            ultimo_dia_mes = ahora.replace(day=31, month=12, year=año_actual)
        else:
            ultimo_dia_mes = (primer_dia_mes + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Sumar las transferencias y envíos del mes actual
        suma_cantidad = (
            trasferencias.objects.filter(fecha__gte=primer_dia_mes, fecha__lte=ultimo_dia_mes, user_id=user)
            .aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        )
        suma_cantidad2 = (
            trasferencias_Bancos.objects.filter(fecha__gte=primer_dia_mes, fecha__lte=ultimo_dia_mes, user_id=user)
            .aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        )
        suma_envios = (
            envio.objects.filter(fecha__gte=primer_dia_mes, fecha__lte=ultimo_dia_mes, user_id=user)
            .aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        )

        # Total de transferencias para el mes
        cantidadT = suma_cantidad + suma_cantidad2

        # Agregar el nombre del mes (por ejemplo, "Enero", "Febrero", etc.) y los valores [tr, ev]
        mes_nombre = primer_dia_mes.strftime("%b")
        resultados_mensuales.append([mes_nombre, cantidadT, suma_envios])

    # Invertir la lista para tener el orden de los meses del más antiguo al más reciente
    resultados_mensuales.reverse()

    return resultados_mensuales

import requests
from django.http import JsonResponse

def enviar_transferencia(email_destinatario,referencia,destinatario,cantidad):

        # Configura la URL del endpoint de Express
        express_url = "http://localhost:3000/send-emailT"

        # Prepara el payload
        payload = {
            "to": email_destinatario,
            "id": referencia,
            "destino": destinatario,
            "cabtidad": cantidad
        }

        try:
            # Realiza la solicitud POST a la API de Express
            response = requests.post(express_url, json=payload)

            # Procesa la respuesta de la API
            if response.status_code == 200:
                print("envie el correo")
            else:
                print("no envie el correo")
        except requests.exceptions.RequestException as e:
            # Maneja errores de red
            print("error de conecxion")

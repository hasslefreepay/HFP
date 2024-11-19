from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from email_services.models import EmailVerification
from email_services.api.serializer import EmailSerializer
import random

class EmailApiView(APIView):
    def post(self, request,):
        serializer = EmailSerializer(data=request.data)
        
        if serializer.is_valid():
            recipient_email = serializer.validated_data['recipient_email']
            
            verification_code = random.randint(10000000, 99999999)
            VerificationCode.objects.create(code=code)
            
            # Aquí puedes implementar la lógica para enviar el correo
            # Ejemplo simple usando send_mail
            try:
                send_mail(
                    subject='Código de Verificación',
                    message=f'Tu código de verificación es: {code_str}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                )
                
                # Solo si el correo se envía exitosamente, guardar el código en la base de datos
                EmailVerification.objects.create(
                    code=code_str
                )
                
                return Response({'message': 'Correo enviado y código guardado exitosamente.'}, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'error': f'Error al enviar el correo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST),"error de envio"
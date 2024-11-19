from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from adminuser.models import user  # Asegúrate de que el nombre sea correcto
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from adminuser.api.permissions import validacion


class UserValidationAPIView(APIView):
    permission_classes = []
    def get(self, request, *args, **kwargs):
        email = request.query_params.get('correo')
        password = request.query_params.get('password')
        print(email)
        print(password)
        

        if not email or not password:
            return Response({'error': 'Both email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_instance = user.objects.get(correo=email)
        except user.DoesNotExist:
            return Response({'exists_1': False}, status=status.HTTP_200_OK)



        if user_instance.password ==password:  # Utiliza check_password en lugar de comparar directamente
            # La contraseña es correcta
            refresh = RefreshToken.for_user(user_instance)
            access_token = str(refresh.access_token)
            return Response({
                'exists': True,
                'n':2,
                'id': user_instance.id,
                'access_token': access_token,
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'exists_2': False}, status=status.HTTP_200_OK)
    def post(self, request, *args, **kwargs):
        return Response({'detail': 'POST method is not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        
        





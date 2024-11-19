from django.contrib.auth.management.commands.createsuperuser import Command as BaseCreateSuperUserCommand

class Command(BaseCreateSuperUserCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--contraseña', dest='contraseña', required=False, help='Contraseña para el superusuario')

    def handle(self, *args, **options):
        contraseña = options.get('contraseña')
        if contraseña:
            options['password'] = contraseña  # Mapear `contraseña` a `password`
        super().handle(*args, **options)

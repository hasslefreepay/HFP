from django.contrib import admin
from adminuser.models import user, trasferencias_Bancos, trasferencias
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = user
    list_display = ['nombre', 'apellidos', 'correo', 'is_staff', 'is_active']
    list_filter = ('pais', 'departamento', 'ciudad', 'codp')
    search_fields = ['correo', 'nombre', 'apellidos', 'pais', 'departamento', 'ciudad', 'codp']
    ordering = ['correo']
    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Personal info', {'fields': ('nombre', 'apellidos', 'telefono', 'pais', 'departamento', 'ciudad', 'codp')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'password1', 'password2', 'nombre', 'apellidos'),
        }),
    )


class TrasferenciasBancosAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'banco', 'cuenta', 'nombre', 'cantidad', 'fecha', 'estado')
    list_filter = ('estado', 'fecha', 'user','banco')  # Filtros por estado, fecha y usuario
    search_fields = ('user__correo', 'banco', 'cuenta', 'nombre')  # Busqueda por correo del usuario, banco, cuenta o nombre
    readonly_fields = ('user', 'tarjeta', 'banco', 'cuenta', 'nombre', 'cantidad', 'fecha')


    def has_add_permission(self, request):
        return False  # Deshabilita la creación de objetos


class TrasferenciasAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'destino', 'cantidad', 'fecha', 'estado')  # Muestra estos campos
    list_filter = ('estado', 'fecha', 'user')  # Filtros por estado, fecha y usuario
    search_fields = ('user__correo', 'destino', 'tarjeta')  # Busqueda por correo del usuario, destino o tarjeta
    readonly_fields = ('user', 'tarjeta', 'destino', 'cantidad', 'fecha')  # Campos no editables


    def has_add_permission(self, request):
        return False  # Deshabilita la creación de objetos


admin.site.register(user, CustomUserAdmin)
admin.site.register(trasferencias_Bancos, TrasferenciasBancosAdmin)
admin.site.register(trasferencias, TrasferenciasAdmin)
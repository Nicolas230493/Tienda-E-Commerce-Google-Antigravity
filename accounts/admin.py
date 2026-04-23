from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address

class AddressInline(admin.StackedInline):
    """
    Permite editar las direcciones del usuario directamente 
    desde el panel de edición de usuario.
    """
    model = Address
    extra = 1
    fieldsets = (
        (None, {
            'fields': ('name', 'recipient_name', 'street_address', 'city', 'state', 'postal_code', 'country', 'is_default')
        }),
    )

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Configuración personalizada del admin para el modelo User.
    Elimina campos redundantes y agrega soporte para direcciones relacionales.
    """
    inlines = [AddressInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_client']
    
    # Limpiamos fieldsets de campos inexistentes (address, city)
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Perfil', {'fields': ('is_client', 'phone')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Perfil', {'fields': ('is_client', 'phone')}),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'city', 'is_default']
    list_filter = ['city', 'is_default']
    search_fields = ['user__username', 'street_address', 'recipient_name']

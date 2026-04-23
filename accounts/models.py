from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modelo de usuario personalizado.
    Refactorizado para eliminar redundancia de dirección.
    """
    is_client = models.BooleanField(default=True, verbose_name="Es cliente")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username

    def get_default_address(self):
        """
        Devuelve la dirección marcada como predeterminada o la más reciente.
        """
        return self.addresses.filter(is_default=True).first() or self.addresses.first()

class Address(models.Model):
    user = models.ForeignKey(
        User, 
        related_name='addresses', 
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    name = models.CharField(max_length=100, verbose_name="Nombre referencia (ej. Casa, Trabajo)")
    recipient_name = models.CharField(max_length=100, verbose_name="Nombre de quien recibe")
    street_address = models.CharField(max_length=255, verbose_name="Calle y número")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    state = models.CharField(max_length=100, verbose_name="Provincia/Estado")
    postal_code = models.CharField(max_length=20, verbose_name="Código Postal")
    country = models.CharField(max_length=100, default='Argentina', verbose_name="País")
    is_default = models.BooleanField(default=False, verbose_name="Es predeterminada")

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"

    def __str__(self):
        return f"{self.name} - {self.street_address}"

    def save(self, *args, **kwargs):
        # Asegurar que solo haya una dirección predeterminada por usuario
        if self.is_default:
            Address.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)

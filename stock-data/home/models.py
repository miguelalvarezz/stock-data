from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class ClientUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Número de teléfono")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biografía")
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, verbose_name="Foto de perfil")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = 'custom_user'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

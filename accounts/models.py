from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.text import slugify

class Agency(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100)  # à migrer vers City plus tard
    address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    logo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Agence"
        verbose_name_plural = "Agences"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN_PLATFORM = 'admin_platform', _('Admin plateforme')
        AGENCY_ADMIN = 'agency_admin', _('Admin agence')
        AGENT = 'agent', _('Agent')
        CUSTOMER = 'customer', _('Client')

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CUSTOMER,
    )
    agency = models.ForeignKey(
        Agency,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='users'
    )

    # champs natifs AbstractUser: username, email, password, first_name, last_name, is_active, etc.

    def is_platform_admin(self):
        return self.role == self.Roles.ADMIN_PLATFORM

    def is_agency_admin(self):
        return self.role == self.Roles.AGENCY_ADMIN

    def is_agent(self):
        return self.role == self.Roles.AGENT

    def __str__(self):
        return f"{self.username} ({self.role})"
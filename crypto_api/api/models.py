from django.db import models

# Create your models here.
class CurrencyModel(models.Model):
    name = models.CharField(max_length=32)
    symbol = models.CharField(max_length=32)
    description = models.CharField(max_length=512)
    slug = models.CharField(max_length=32)
    isActive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.description
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(limit_value=0), MaxValueValidator(limit_value=100)], help_text='Percentage value (0 to 100)')
    active = models.BooleanField()

    def __str__(self) -> str:
        return self.code
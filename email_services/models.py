from django.db import models

# Create your models here.
class EmailVerification(models.Model):
    verification_code = models.IntegerField()
    is_used = models.BooleanField(default=False)
    def __str__(self):
        return f' {self.verification_code}'
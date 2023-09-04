from django.db import models

class CustomUser(models.Model):
    id = models.CharField(primary_key=True,max_length=255)
    name = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    USERNAME_FIELD = 'id'

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name
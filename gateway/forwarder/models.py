from django.db import models

# Create your models here.

class ForwardMapping(models.Model):

    student_id = models.CharField(max_length=36, db_index=True)
    target_host = models.CharField(max_length=128)
    first_name = models.CharField(max_length=36, blank=True, null=True)
    last_name = models.CharField(max_length=36, blank=True, null=True)
    email = models.EmailField()
    created = models.BooleanField(default=False)









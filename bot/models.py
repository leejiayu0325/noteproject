from django.db import models

# Create your models here.
class Linebotuser(models.Model):
    user = models.CharField(max_length=128, null=False, blank=False, unique=True)
    step = models.PositiveIntegerField(default=0)    
    booktype = models.CharField(max_length=50, null=True, blank=True)    
    updatasstr = models.CharField(max_length=50, null=True, blank=True)    

    class Meta:
        db_table = "linebotinfo"  
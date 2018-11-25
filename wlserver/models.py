from django.db import models


# Create your models here.


class Info(models.Model):
    customer_alias = models.CharField(max_length=128)
    ca_user_id = models.CharField(max_length=128, null=True, blank=True)
    itp_user_id = models.CharField(max_length=128)
    company = models.CharField(max_length=128)
    plb = models.CharField(max_length=128)
    cs_name = models.CharField(max_length=128, null=True, blank=True)
    app_flag_chioces = ((0, "WX"), (1, "Line"))
    app_flag = models.SmallIntegerField(choices=app_flag_chioces)



class FAQ(models.Model):
    questions = models.CharField(max_length=256)
    answers = models.CharField(max_length=300)
    key_words = models.CharField(max_length=128)

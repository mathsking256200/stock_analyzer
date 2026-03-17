from django.db import models
from django.utils.text import slugify

class Stock(models.Model):
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(unique=True)
    sector = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
    
class User(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    password = models.CharField(max_length=200)

    dob = models.DateField()
    gender = models.CharField(max_length=20)

    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    #Email Reset Link
    reset_token = models.CharField(max_length=255, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "analyzer_users"
    

class Payment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    razorpay_order_id = models.CharField(max_length=200)
    razorpay_payment_id = models.CharField(max_length=200)

    amount = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_payment"
 
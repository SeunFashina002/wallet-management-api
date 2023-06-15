from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

from .managers import UserManager
from .validators import validate_otp_length

# Create your models here.

class User(AbstractUser):
    # additional fields 
    username=None
    email = models.EmailField(_('email address'), unique=True, error_messages={'unique': 'Email address already exists for another user'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # custom user manager
    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# wallet balance

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # gave users a default of 100, 000 in their balance for the voucher to be tested
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=100000.00)


    def __str__(self):
        return f"{self.balance}"



class VoucherOtp(models.Model):
    otp = models.CharField(max_length=4,  unique=True, validators=[validate_otp_length])
    has_expired = models.BooleanField(default=False)


class Voucher(models.Model):

    SINGLE = 'single'
    MULTI = 'multi'

    VOUCHER_TYPE = (
        (SINGLE, 'single'),
        (MULTI, 'multi')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=9, unique=True)
    otp = models.ForeignKey(VoucherOtp, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    voucher_type = models.CharField(choices=VOUCHER_TYPE, max_length=10)    
    is_redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code}"
    

class Transactions(models.Model):    
    # types of transactions
    VOUCHER = 'voucher'
    SENT = 'sent'
    RECEIVED = 'received'
    TRANSACTION_TYPES = [
        (VOUCHER, 'Vouchers'),
        (SENT, 'Sent'),
        (RECEIVED, 'Received'),
    ]

    voucher = models.ForeignKey(Voucher, on_delete=models.SET_NULL, null=True)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_type = models.CharField(choices=TRANSACTION_TYPES, max_length=15)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type}"
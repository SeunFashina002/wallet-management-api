import string
import random
from core.models import Voucher, VoucherOtp

code_length = 9
code_char = string.digits #(0-9) digits

def generate_voucher_code():
    while True:
        voucher_code = ''.join(random.choice(code_char) for _ in range(code_length))
        if not Voucher.objects.filter(code=voucher_code).exists():
            return voucher_code

def generate_otp():
    while True:
        otp = ''.join(random.choice(code_char) for _ in range(4))
        if not VoucherOtp.objects.filter(otp=otp).exists():
            return otp

# welcome data response

message = "Welcome to okeowo wallet api, while we wait for the api documentation. Here is a list of the available endpoints: (1) https://wallet-api-2dca.onrender.com/api/v1/auth/login/  (2) https://wallet-api-2dca.onrender.com/api/v1/auth/register/   (3)  https://wallet-api-2dca.onrender.com/api/v1/auth/transactions/   (4)  https://wallet-api-2dca.onrender.com/api/v1/auth/transactions/sent   (5)  https://wallet-api-2dca.onrender.com/api/v1/auth/transactions/received   (6)  https://wallet-api-2dca.onrender.com/api/v1/auth/vouchers/  (7)  https://wallet-api-2dca.onrender.com/api/v1/auth/vouchers/all   (8)  https://wallet-api-2dca.onrender.com/api/v1/auth/vouchers/redeem"

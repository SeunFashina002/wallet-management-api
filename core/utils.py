import string
import random
from core.models import Wallet

code_length = 9
code_char = string.digits #(0-9) digits

def generate_voucher_code():
    voucher_code = ''.join(random.choice(code_char) for _ in range(code_length))
    return voucher_code

# welcome data response

message = "Welcome to okeowo wallet api, while we wait for the api documentation. Here is a list of the available endpoints: (1) api/v1/auth/login/  (2) api/v1/auth/register/   (3)  api/v1/auth/transactions/   (4)  api/v1/auth/transactions/sent   (5)  api/v1/auth/transactions/received   (6)  api/v1/auth/vouchers/  (7)  api/v1/auth/vouchers/all   (8)  api/v1/auth/vouchers/redeem"

import string
import random

code_length = 9
code_char = string.digits #(0-9) digits

def generate_voucher_code():
    voucher_code = ''.join(random.choice(code_char) for _ in range(code_length))
    return voucher_code


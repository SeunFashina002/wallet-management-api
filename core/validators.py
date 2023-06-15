from rest_framework.validators import ValidationError

def validate_otp_length(value):
    if len(str(value)) > 4:
        raise ValidationError("OTP must be a 4 digit number.")
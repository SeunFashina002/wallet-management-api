from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Voucher, Transactions

User = get_user_model()


# customize token claim
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email

        return token



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # fields = '__all__'
        exclude = ('password', 'groups', 'user_permissions')



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'confirm_password')

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.pop('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError(_('password does not match'))


        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# other serializers

class VoucherTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ('amount',)


class RedeemVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ('amount', 'code')

class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        # exclude = ('user',)
        fields = "__all__"

# get all transactions

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = "__all__"
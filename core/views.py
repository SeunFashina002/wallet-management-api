from django.shortcuts import render
from .serializers import UserRegisterSerializer, UserSerializer, MyTokenObtainPairSerializer, VoucherSerializer, TransactionSerializer, VoucherTransactionSerializer
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from .models import Voucher, Transactions


from .utils import generate_voucher_code

# Create your views here.

# create an account for a user
class UserRegister(CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({        
        'user': UserSerializer(user, context={'request': request}).data,
        'success':'Sign up successful!'
        }, status=status.HTTP_201_CREATED)

# login the user
class UserLogin(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]

# create a voucher

class VoucherCreate(CreateAPIView):
    serializer_class = VoucherTransactionSerializer


# create a voucher
    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        available_balance = 100000.00

        print(self.request.user)
        if float(amount) <= float(available_balance):
            #  generate the voucher code 
            voucher_code = generate_voucher_code()
            voucher = Voucher.objects.create(
                code = voucher_code,
                amount = amount,
                is_redeemed = False,
            )

            # simultaneously create a transaction history for this voucher
            transaction = Transactions.objects.create(
                voucher = voucher,
                transaction_amount = amount,
                transaction_type = Transactions.VOUCHER,
                user = self.request.user
            )

            return Response({
                'success': 'Pay code generated successfully. Copy or share the code to the recipient to redeem it.',
                'Pay code balance' : amount,
                'Generated code' : voucher_code
                 }, status=status.HTTP_201_CREATED)
        
        return Response({'error': "sorry, you don't enough balance in your wallet, fund your wallet and try again",
                }, status=status.HTTP_400_BAD_REQUEST)

# get all vouchers

class VoucherList(ListAPIView):
    serializer_class = VoucherSerializer
    queryset = Voucher.objects.all()
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if qs.exists():
            serializer = self.get_serializer(qs, many=True)
            return Response({
                'success':'all vouchers',
                'vouchers':serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'data':'no vouchers found',
        }, status=status.HTTP_404_NOT_FOUND)



# get all transactions
class TransactionsList(ListAPIView):
    serializer_class = TransactionSerializer
    queryset = Transactions.objects.all()

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if qs.exists():
            serializer = self.get_serializer(qs, many=True)
            return Response({
                'success':'all transactions',
                'transactions':serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'data':'no transaction found',
        }, status=status.HTTP_404_NOT_FOUND)
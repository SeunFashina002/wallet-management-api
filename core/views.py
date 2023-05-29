from math import perm
from .serializers import UserRegisterSerializer, UserSerializer, MyTokenObtainPairSerializer, VoucherSerializer, TransactionSerializer, VoucherTransactionSerializer, RedeemVoucherSerializer
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import Voucher, Transactions, Wallet

from decimal import Decimal


from .utils import generate_voucher_code, message

# welcome response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_home(request):
    return Response(message)

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

        # retrieve wallet instance 
        wallet = Wallet.objects.get(user=request.user)
        available_balance = wallet.balance


        if Decimal(amount) <= available_balance:

            # deduct amount from the wallet
            wallet.balance -= Decimal(amount)
            wallet.save()

            #  generate the voucher code 
            voucher_code = generate_voucher_code()
            voucher = Voucher.objects.create(
                user = request.user,
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


# filter transaction history by sent
class TransactionSentList(ListAPIView):

    def get(self, request):
        transactions = Transactions.objects.filter(transaction_type=Transactions.SENT, user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# filter transaction history by received
class TransactionReceivedList(ListAPIView):

    def get(self, request):
        transactions = Transactions.objects.filter(transaction_type=Transactions.RECEIVED, user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# Redeem voucher

class VoucherRedeem(CreateAPIView):
    serializer_class = RedeemVoucherSerializer

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        code = request.data.get('code')

        try:
            # get the voucher and the owner attached to it
            voucher = Voucher.objects.get(code=code, is_redeemed=False)
            voucher_owner = voucher.user
            

            # ensure there is sufficient balance in the voucher
            if Decimal(amount) <= voucher.amount:
                voucher.amount -= Decimal(amount)
                voucher.is_redeemed = True
                voucher.save()

                # create a transaction for the sender of the voucher
                transaction = Transactions.objects.create(
                    voucher = voucher,
                    transaction_amount = amount,
                    transaction_type = Transactions.SENT,
                    user = self.request.user
                )
                
                
                # recipient receives balance in wallet
                receiver_wallet = Wallet.objects.get(user=request.user)
                receiver_wallet.balance += Decimal(amount)
                receiver_wallet.save()

                # create a transaction for the reciepient
                transaction = Transactions.objects.create(
                    voucher = voucher,
                    transaction_amount = amount,
                    transaction_type = Transactions.RECEIVED,
                    user = voucher_owner
                )

                return Response({'success': 'Voucher redeemed successfully.'}, status=status.HTTP_200_OK)

            return Response({'error': 'Insufficient voucher amount.'}, status=status.HTTP_400_BAD_REQUEST)

        except Voucher.DoesNotExist:
            return Response({'error': 'Invalid voucher code or voucher has already been redeemed.'}, status=status.HTTP_400_BAD_REQUEST)



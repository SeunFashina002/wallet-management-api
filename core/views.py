from .serializers import UserRegisterSerializer, UserSerializer, MyTokenObtainPairSerializer, VoucherSerializer, TransactionSerializer, VoucherTransactionSerializer, RedeemVoucherSerializer
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import Voucher, Transactions, Wallet , VoucherOtp

from decimal import Decimal


from .utils import generate_voucher_code, message, generate_otp

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


"""
single use voucher (steps)

creating the voucher 

1. generate a voucher: amount (input) responses(code(9-digits), system generated pin only visble to the receiver(4-digits))
2. check if the balance in the users wallet is sufficient

redeeming the voucher

3. check if the user redeeming the voucher is not the owner of the voucher
4. check if the amount of the voucher is and only equal to the amount to be redeemed
5. add the balance to the recipient wallet
6. set the voucher to redeemed 
7. set the pin to expired

"""

# creates voucher for single use

class VoucherSingleCreate(CreateAPIView):
    serializer_class = VoucherTransactionSerializer

    def post(self, request, *args, **kwargs):

        # get the amount from the user
        amount = request.data.get('amount')

        # get the users wallet balance
        wallet = Wallet.objects.get(user=request.user)
        available_balance = wallet.balance

        # check if the wallet has sufficient balance
        if Decimal(amount) <= available_balance:

            # deduct the amount from the wallet
            wallet.balance -= Decimal(amount)
            wallet.save()

            # generate 9-digits paycode
            voucher_code = generate_voucher_code()
            
            # generate 4 digits otp
            voucher_pin = generate_otp()

            voucher_otp = VoucherOtp.objects.create(otp=voucher_pin, has_expired=False)
            # create a voucher with that code
            voucher = Voucher.objects.create(
                user = request.user,
                code = voucher_code,
                otp = voucher_otp,
                voucher_type = Voucher.SINGLE,
                is_redeemed = False,
            )
            voucher.amount += Decimal(amount)
            voucher.save()

            return Response({
                'success': 'Your single use pay code was generated successfully. Copy or share the code to the recipient to redeem it.',
                'Pay code balance' : amount,
                'Pay code' : voucher_code,
                'otp' : voucher_pin,
            }, status=status.HTTP_201_CREATED)
            # will be excluding the pin from the response for the sender later


        return Response({'error': "sorry, you don't enough balance in your wallet, fund your wallet and try again",
        }, status=status.HTTP_400_BAD_REQUEST)


# create a transaction for the sender of the voucher when we implement send voucher functionality
# transaction = Transactions.objects.create(
#     voucher = voucher,
#     transaction_amount = amount,
#     transaction_type = Transactions.SENT,
#     user = voucher_owner
# )


# Redeem voucher(single use and multi use)

class VoucherRedeem(CreateAPIView):
    serializer_class = RedeemVoucherSerializer

    def post(self, request, *args, **kwargs):
        # temporarily getting the amount and code by user input
        amount = request.data.get('amount')
        code = request.data.get('code')
        try:
            pin = request.data.get('pin')
        except pin is None or pin == "":
            return Response({'message': 'you must provide a pin'}, status=status.HTTP_204_NO_CONTENT)        

        try:
            # get the voucher and the owner attached to it
            voucher = Voucher.objects.get(code=code)
            voucher_owner = voucher.user
        except Voucher.DoesNotExist:
            return Response({'error': 'Invalid voucher code.'}, status=status.HTTP_400_BAD_REQUEST)


        # return Response({"vocuher owner": voucher_owner.first_name, "voucher owner": voucher_owner.last_name})

        # single use voucher implementation
        if voucher.voucher_type == Voucher.SINGLE:
            if not voucher_owner == request.user:
                if voucher.is_redeemed == False:
                    if str(pin) == voucher.otp.otp:
                        if voucher.otp and voucher.otp.has_expired == False:
                            if Decimal(amount) == voucher.amount:
                                
                                voucher.amount -= Decimal(amount)
                                voucher.is_redeemed = True
                                voucher.save()

                                # recipient receives balance in wallet
                                receiver_wallet = Wallet.objects.get(user=request.user)
                                receiver_wallet.balance += Decimal(amount)
                                receiver_wallet.save()

                                # invalidate the otp
                                voucher.otp.has_expired = True
                                voucher.otp.delete()

                                # create a transaction for the recipient
                                Transactions.objects.create(
                                    voucher=voucher,
                                    transaction_amount=amount,
                                    transaction_type=Transactions.RECEIVED,
                                    user=request.user
                                )
                                return Response({'success': 'Voucher redeemed successfully.'}, status=status.HTTP_200_OK)
                            return Response({'message': 'Sorry, for a single use voucher you have to redeem the exact amount'}, status=status.HTTP_400_BAD_REQUEST)
                        return Response({'error': 'This pin has been used for this voucher'}, status=status.HTTP_400_BAD_REQUEST)        
                    return Response({'error': 'Invalid pin'}, status=status.HTTP_400_BAD_REQUEST)        
                return Response({'error': 'This voucher has been used'}, status=status.HTTP_400_BAD_REQUEST)                
            return Response({'message': 'Sorry, you cannot redeem your own voucher'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Multi use vouchers are not yet available'}, status=status.HTTP_204_NO_CONTENT)

        #Todo: code for multi use goes here



# create a voucher
# this is the old way of creating voucher, code will be deleted soon

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

            # temporary: simultaneously create a transaction history for this voucher
            # this code will be in the share code functionality
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
    
    def get(self, request, *args, **kwargs):
        qs = Voucher.objects.filter(user=request.user)
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
    

    def list(self, request, *args, **kwargs):
        qs = Transactions.objects.filter(user=request.user)
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

    serializer_class = TransactionSerializer
    def get(self, request):
        transactions = Transactions.objects.filter(transaction_type=Transactions.SENT, user=request.user)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# filter transaction history by received
class TransactionReceivedList(ListAPIView):
    serializer_class = TransactionSerializer

    def get(self, request):
        transactions = Transactions.objects.filter(transaction_type=Transactions.RECEIVED, user=request.user)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




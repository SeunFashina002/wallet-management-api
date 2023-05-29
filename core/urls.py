from django.urls import path
from .views import UserRegister, UserLogin, TransactionsList, VoucherCreate, VoucherList
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/login/', UserLogin.as_view(), name='token_obtain_pair'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
    path('auth/register/', UserRegister.as_view(), name='register_user'),

    # get all transactions
    path('transactions/', TransactionsList.as_view(), name='all_transactions'),
    
    # post request to create voucher, get request to list all vouchers
    path('vouchers/', VoucherCreate.as_view(), name='create_voucher'),
    path('vouchers/all', VoucherList.as_view(), name='list_voucher'),
]
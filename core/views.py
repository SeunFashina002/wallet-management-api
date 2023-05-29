from django.shortcuts import render
from .serializers import UserRegisterSerializer, UserSerializer, MyTokenObtainPairSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status

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
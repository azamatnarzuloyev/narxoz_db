from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from .serializers import LoginSerializer, UserSerializer, ChangePasswordSerializer
import logging

logger = logging.getLogger(__name__)

class LoginView(APIView):
    """
    User login endpoint
    """
    permission_classes = []

    # @extend_schema(
    #     summary="User login",
    #     description="Authenticate user and return token",
    #     request=LoginSerializer,
    #     responses={200: {'token': 'string', 'user': UserSerializer}}
    # )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    logger.info(f"User {username} logged in successfully")
                    
                    return Response({
                        'token': token.key,
                        'user': UserSerializer(user).data
                    })
                else:
                    return Response(
                        {'error': 'Account is disabled'}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """
    User logout endpoint
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User logout",
        description="Logout user and delete token"
    )
    def post(self, request):
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            logger.info(f"User {request.user.username} logged out successfully")
            return Response({'message': 'Successfully logged out'})
        except:
            return Response(
                {'error': 'Error logging out'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ProfileView(APIView):
    """
    User profile endpoint
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user profile",
        description="Get current user profile information",
        responses={200: UserSerializer}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update user profile",
        description="Update current user profile information",
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {request.user.username} updated profile")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    """
    Change password endpoint
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change password",
        description="Change user password",
        request=ChangePasswordSerializer
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Invalid old password'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Delete all tokens to force re-login
            Token.objects.filter(user=user).delete()
            
            logger.info(f"User {user.username} changed password")
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

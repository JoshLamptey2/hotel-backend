from django.shortcuts import render
import re
import logging
import arrow
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import action
from apps.accounts.auth import Authenticator
from rest_framework import viewsets, status,permissions
from rest_framework.response import Response
from apps.accounts.permissions import TokenRequiredPermission
from apps.accounts.models import User, UserRole, Branch, CustomerProfile,StaffProfile
from django.db.models import Q
from apps.accounts.serializers import(
    UserRoleSerializer,
    UserCreateUpdateSerializer,
    UserListSerializer,
    BranchListSerializer,
    CustomerProfileCreateUpdateSerializer,
    CustomerProfileListSerializer,
    StaffProfileCreateUpdateSerializer,
    StaffProfileListSerializer,   
)
auth = Authenticator()
logger = logging.getLogger(__name__)
# Create your views here.

class UserRoleViewset(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    permission_classes = [TokenRequiredPermission]
    serializer_class = UserRoleSerializer
    lookup_field='uid'
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {'success': True, 'message': serializer.data}, status=status.HTTP_200_OK
            )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {'success': True, 'message': serializer.data}, status=status.HTTP_200_OK
            )
    
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            name = data.get('name')
            
            if not name:
                return Response(
                    {'success': False, 'message': 'name is required'}, status=status.HTTP_400_BAD_REQUEST
                    )
            role = UserRole.objects.filter(name=name)
            
            if role.exists():
                return Response(
                    {'success': False, 'message': 'user role already exists'}, status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return Response(
                {'success': False,
                 'message': 'An error occured whilst processing your request'},
                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    lookup_field = 'uid'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserListSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {'success': True, 'message': serializer.data}, status=status.HTTP_200_OK
            )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'message': serializer.data}, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        
        customer_required_fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "location"
        ]
        
        staff_required_fields = [
            "first_name",
            "last_name",
            "dob",
            "location"
            "email",
            "phone_number"
            "id_card_number",
            "role",
            "branch",
        ]
        
        role_data = data.get("role")
        
        role = UserRole.objects.filter(id=role_data).first()
        
        if role.name in ["staff", "admin"]:
            required_fields = staff_required_fields
        else:
            required_fields = customer_required_fields
        
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {'success': False, 'message': f'{field} is required'},
                                status=status.HTTP_400_BAD_REQUEST
                )
        
        if User.objects.filter(phone_number=data.get('phone_number')).exists():
            return Response(
                {'success': False, 'message': 'User already exists'},
                status=status.HTTP_400_BAD_REQUEST
                )
        
        if User.objects.filter(email=data.get('email')).exists():
            return Response(
                {'success': False, 'message': 'User already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if data.get('branch'):
            branch = Branch.objects.filter(id=data.get('branch')).first()
            data["branch"] = branch.id
            
        if data.get("password"):
            data["password"] = make_password(data.get("password"))
            data["password_changed"] = True
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception= True)
        self.perform_create(serializer)
        
        return Response(
            {'success': True, 'message': "User Created Successfully"},
            status=status.HTTP_201_CREATED
            )
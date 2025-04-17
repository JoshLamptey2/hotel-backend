from rest_framework import serializers
from decouple import config
from apps.accounts.models import UserRole,User,StaffProfile,CustomerProfile, Branch
from drf_spectacular.utils import extend_schema_field

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'

class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    
    @extend_schema_field(UserRoleSerializer())
    def get_role(self, obj):
        if obj.role:
            return {"id":obj.role.id, "uid":obj.role.uid, "name": obj.role.name}
        else:
            return None
    
    @extend_schema_field(serializers.URLField())
    def get_profile(sel, obj):
        if obj.profile:
            return config("BASE_URL") + obj.profile.url
        else:
            return None
        
    
    class Meta:
        model = User
        fields = '__all__'



class StaffProfileCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = '__all__'



class StaffProfileListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    
    @extend_schema_field(UserRoleSerializer())
    def get_role(self, obj):
        if obj.role:
            return {"id":obj.role.id, "uid":obj.role.uid, "name": obj.role.name}
        else:
            return None
    
    @extend_schema_field(serializers.URLField())
    def get_profile(sel, obj):
        if obj.profile:
            return config("BASE_URL") + obj.profilr.url
        else:
            return None
        
    
    class Meta:
        model = StaffProfile
        fields = '__all__'


class CustomerProfileCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
 
 
        
class CustomerProfileListSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    
    @extend_schema_field(serializers.URLField())
    def get_profile(sel, obj):
        if obj.profile:
            return config("BASE_URL") + obj.profilr.url
        else:
            return None
    
    class Meta:
        model = CustomerProfile
        fields = '__all__'




class UserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    
    @extend_schema_field(UserRoleSerializer())
    def get_role(self, obj):
        if obj.role:
            return {"id":obj.role.id, "uid":obj.role.uid, "name": obj.role.name}
        else:
            return None
    
    @extend_schema_field(serializers.URLField())
    def get_profile(sel, obj):
        if obj.profile:
            return config("BASE_URL") + obj.profilr.url
        else:
            return None
        
    
    class Meta:
        model = CustomerProfile
        fields = '__all__'
    

class BranchCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class BranchListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    @extend_schema_field(serializers.URLField)
    def get_image(self, obj):
        if obj.image:
            return config("BASE_URL") + obj.image.url
        else:
            return None
        
    class Meta:
        model = Branch
        fields = ["id", "uid", "image", "name", "phone", "manager", "location"]
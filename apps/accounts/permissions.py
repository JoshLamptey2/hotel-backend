from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
import jwt
import arrow
from decouple import config
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

class TokenRequiredPermission(BasePermission):
    def has_permission(self, request, view):
        access_token = request.headers.get("Authorization")
        
        if not access_token:
            return PermissionDenied("Auth token is required")
        
        try:
            decoded_json = jwt.decode(
                access_token, config("SECRET_KEY"),algorithms=["HS256"]
            )
            
            expiration_time = arrow.get(decoded_json['exp'])
            logger.warning(expiration_time)
            
            #set the user on the request
            decoded_json.get("user_id")
            logged_user = User.objects.get(id=decoded_json.get("user_id"))
            
            if logged_user:
                request.user = logged_user
                
                user_data ={
                    "user" : request.user,
                    "isSuperuser" : request.user.is_superuser,
                    "email" : request.user.email,
                }
                
                logger.warning(f"Logged in user:{user_data}")
            else:
                raise PermissionDenied("User not found.")
        except jwt.ExpiredSignatureError:
            raise PermissionDenied("Token has expired.")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token error: {e}")
            raise PermissionDenied("Invalid access token.")
        return True
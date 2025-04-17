import logging
import arrow
import jwt
from decouple import config
from django.core.cache import cache
import random
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from apps.accounts.utils import send_notifications



User = get_user_model()
logger = logging.getLogger(__name__)

class Authenticator:
    def generate_token(self, email=None, phone_number=None):
        if email:
            field = "email"
            value = email
        elif phone_number:
            field = "phone_number"
            value = phone_number
        else:
            raise ValueError("Either email or phone_number must be provided")
        
        try:
            user = User.objects.get(**{field: value})
        except ObjectDoesNotExist:
            raise ValueError("User does not exist")
        
        payload = {
            "user_uid": str(user.uid),
            "user_id" : user.id,
            "full_name" : f"{user.first_name} {user.last_name}",
            "exp" : arrow.utcnow().shift(days=30).datetime,
            "iat" : arrow.utcnow().datetime
        }
        secret_key = config("SECRET_KEY")
        if not secret_key:
            raise ValueError("SECRET_KEY is not set")
        
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
    
    def generate_otp(self, email=None, phone_number=None):
        rand = random.randint(10000,99999)
        return rand
    
    def send_otp(self, email=None, phone_number=None):
        try:
            otp = self.generate_otp()
            logger.info(f'Generated OTP:{otp}')
            
            if email:
                cache.set(email, otp, timeout=300)
                context = {"template":"otp", "context":{"otp":otp}}
                #send the otp via email
                mail = send_notifications.delay(
                    medium="email", recipient=email, context=context
                )
                logger.warning(f"Email notification sent: {mail}")
            elif phone_number:
                cache.set(phone_number, otp, timeout=300)
                sms = send_notifications.delay(
                    medium="sms",
                    recipient=phone_number, 
                    message = f"Your OTP  for  Laurenz Hotel is {otp}"
                )
                logger.warning(f"SMS notification sent: {sms}")
            else:
                raise ValueError("Either email or phone_number must be provided")
            
            return otp
        
        except Exception as e:
            logger.error(f"Error sending OTP: {e}")
            return {'success':False, 'message':'Error sending OTP'}
        
    
    def verify_otp(self, user_entered_otp, email=None, phone_number=None):
        cache_key = email if email else phone_number
        cached_otp = cache.get(cache_key)
        logger.warning(f'Stored OTP for {cache_key}: {cached_otp}')
        
        if cached_otp is None:
            return False        
        try:
            user_otp = int(user_entered_otp)
        except ValueError:
            return False
        
        if user_otp != cached_otp:
            return False
        else :
            return True
    
    
    def forget_to_verify_otp(self, user_entered_otp,email=None, phone_number=None):
        cache_key = email if email else phone_number
        if not cache_key:
            return Response(
                {
                    'success': False, 
                    'message': 'Either email or phone_number must be provided'
                    },
                status=400,
            )   
        
        cached_otp = cache.get(cache_key)
        logger.warning(f'Stored otp for {cache_key}: {cached_otp}')
        
        if cached_otp is None:
            return Response(
                {
                    'success': False,
                    'message': 'Kindly click the resend otp button to get a new otp'
                    }, 
                status=400,
                )
        try:
            user_otp = int(user_entered_otp)
        except (ValueError, TypeError):
            return{
                'success': False,
                'message': 'Invalid OTP, Please enter a valid OTP'
            }
        
        if user_otp != cached_otp:
            retries_key = f'retries{cache_key}'
            retries = cache.get(retries_key, 0)
            retries += 1
            cache.set(retries_key, retries, 300) # 5 minutes
            
            if retries > 4:
                logger.warning(f'Max retries reached for {cache_key}')
                cache.delete(cache_key) #delete the otp
                cache.delete(retries_key) #delete the retries counter
                return Response(
                    {
                        'success': False, 
                        'message': 'Max retries reached , kindly click the resend otp button to get a new otp'
                        }, 
                    status=400,
                    )
            else:
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid OTP'},
                    status=400,
                    )
        #otp verificatation successfull
        cache.delete(cache_key)
        cache.delete(f'retries :{retries_key}')
        return Response(
            {
                'success': True, 
                'message': 'message'
                },
            status=200,
            )
        
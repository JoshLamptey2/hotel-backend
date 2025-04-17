import logging
import requests
from decouple import config
from post_office import mail
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def send_notifications(medium, recipient, context=None, message=None):
    try:
        if medium == 'email':
            template = context.get("template")
            if not template:
                logger.error("Email template not provided in context")
                return {'success': False, 'message': 'Email template not provided in context'}
            
            mail.send(
                recipient,
                config("DEFAULT_FROM_EMAIL"),
                template=template,
                context=context.get("context",{}),
                priority="now",
            )
            logger.info(f'Email notification sent to {recipient}')
            return {'success': True, 'message': 'Email is sent successfully'}
        
        elif medium == 'sms':
            apiKey=config("SMS_KEY")
            if not apiKey:
                logger.error("SMS API key not provided")
                return {'success': False, 'message': 'SMS API key not provided'}
            
            endPoint = "https://sms.arkesel.com/sms/api"
            params = {
                "action" : "send-sms",
                "api_key" : apiKey,
                "to" : recipient,
                "from" : "Laurenz Hotel",
                "sms"  : message
            }
            response = requests.get(endPoint, params=params)
            data = response.json()
            logger.warning(f'sms response: {data['code']}')
            
            if data['code'] == 200:
                logger.info(f'SMS notification sent to {recipient}')
                return {'success': True, 'message': 'SMS is sent successfully'}
            else:
                logger.error(f'Failed to send SMS to {recipient}')
                return {'success': False, 'message': 'Failed to send SMS'}
        else:
            logger.error("Neither context (for email) nor message (for SMS) was provided")
            return {'success': False, 'message': 'No context or message provided'}
    
    except Exception as e:
        logger.error(f"An error occurred while sending notification: {e}")
        return {'success': False, 'message': f'error sending notification: {str(e)}'}

@shared_task
def send_login_credentials(email,password, phone_number):
    context = {
        "template":"login-credentials",
        "context": {
            "email": email,
            "password": password,
        },
    }
    send_notifications.delay(
        medium="sms",
        recipient=phone_number,
        message=f"Your Login Credentials are : \n Email: {email} \n Password: {password}",
    )
    
    send_notifications.delay(medium="email", recipient=email, context=context)
    
            
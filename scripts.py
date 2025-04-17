import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_backend.settings")
django.setup()


import logging
import json


logger = logging.getLogger(__name__)

from post_office.models import EmailTemplate


def upload_templates(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r") as f:
                content = f.read()
                template_name = os.path.splitext(filename)[0]
                # Save or update the template in the database
                email_template, created = EmailTemplate.objects.update_or_create(
                    name=template_name,
                    defaults={"subject": template_name, "html_content": content},
                )
                if created:
                    print(f"Template '{template_name}' created successfully.")
                else:
                    print(f"Template '{template_name}' updated successfully.")


upload_templates('templates')


# from apps.users.utils import send_notification
# notif = send_notification.delay(
#     medium="sms", recipient="0209414099", message="hello world"
# )

# print(notif)

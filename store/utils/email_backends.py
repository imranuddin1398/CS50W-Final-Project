# myapp/utils/email_backends.py
import os
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives

class MyCustomEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        num_sent = 0
        api_key = os.getenv('MAILERSEND_API_KEY')  # Get API key from environment variables

        for message in email_messages:
            # Extract email details
            email_data = {
                'from': {
                    'email': message.from_email,
                    'name': message.extra_headers.get('From-Name', '')  # Use extra_headers for the name if provided
                },
                'to': [{'email': recipient} for recipient in message.to],
                'subject': message.subject,
                'text': message.body,
                'html': message.alternatives[0][0] if message.alternatives else ''
            }

            # Send the email via the MailerSend API
            response = requests.post(
                'https://api.mailersend.com/v1/email',
                json=email_data,
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            )

            # Check response status
            if response.status_code == 200:
                num_sent += 1
            else:
                # Handle failed email sending
                print(f"Failed to send email to {message.to}: {response.text}")

        return num_sent

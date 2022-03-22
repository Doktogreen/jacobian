from django.template.loader import render_to_string
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from decouple import config

def send_welcome_email(email: str, firstname: str):
    html = render_to_string('users/emails/welcome.html', dict(firstname=firstname))
    message = Mail(
        from_email="support@simplefinance.ng",
        to_emails=email,
        subject='Welcome to Simple Finance',
        html_content=html
    )
    client = SendGridAPIClient(
        api_key=config('SENDGRID_API_KEY')
    )
    
    try:
        response = client.send(message)
        print(response)
    except Exception as e:
        print(e)

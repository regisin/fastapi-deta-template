from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.config import settings
from app.models.User import UserRead


def send_verification_email(user: UserRead, verification_code: str):
    """
    Need to work on this url. Maybe an env instead of hardcoded deta.sh url? Not important right now, emails works, and api works too.
    """
    url = f'https://{settings.DETA_ID}.deta.sh/{settings.API_V1_STR}/auth/verify/{verification_code}'
    html_content = f'An account on {settings.APP_NAME} was created using this email address. Please verify your by visiting: <a href="{url}">{url}</a>'
    message = Mail(
        from_email=settings.NO_REPLY_EMAIL,
        to_emails=user.username,
        subject=f'{settings.APP_NAME} email verification',
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(
            settings.SENDGRID_API_KEY
        )
        response = sg.send(message)
    except Exception as e:
        print(e)

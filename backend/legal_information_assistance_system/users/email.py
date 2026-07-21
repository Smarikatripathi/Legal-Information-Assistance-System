from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from legal_information_assistance_system.users.models import User


def send_password_reset_email(*, user: User, reset_link: str) -> None:
    subject = "Password Reset Request"

    context = {
        "user": user,
        "reset_link": reset_link,
        "site_name": settings.SITE_NAME,
    }

    text_body = render_to_string(
        "email/password_reset.txt",
        context,
    )

    html_body = render_to_string(
        "email/password_reset.html",
        context,
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    message.attach_alternative(
        html_body,
        "text/html",
    )

    message.send(fail_silently=False)
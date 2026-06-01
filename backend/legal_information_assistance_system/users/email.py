from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from legal_information_assistance_system.users.models import User


def send_password_reset_email(*, user: User, reset_link: str) -> None:
    subject = _("Password reset request")
    context = {
        "user": user,
        "reset_link": reset_link,
        "site_name": getattr(settings, "SITE_NAME", "Legal Information Assistance System"),
    }
    text_body = render_to_string("users/email/password_reset.txt", context)
    html_body = render_to_string("users/email/password_reset.html", context)

    message = EmailMultiAlternatives(
        subject=str(subject),
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)

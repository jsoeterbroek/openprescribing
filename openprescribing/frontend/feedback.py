from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import get_template


def send_feedback_mail(user_name, user_email_addr, subject, message, url):
    connection = get_connection()

    ctx = {
        'name': user_name,
        'url': url,
        'message': message,
    }

    template = get_template('feedback_email.txt')
    body = template.render(ctx)

    email = EmailMultiAlternatives(
        subject='OpenPrescribing Feedback: {}'.format(subject),
        body=body,
        from_email='{} <{}>'.format(user_name, user_email_addr),
        to=[settings.SUPPORT_EMAIL],
        reply_to=[user_email_addr],
        connection=connection
    )

    return email.send()

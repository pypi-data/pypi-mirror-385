from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.translation import gettext as _

FROM_EMAIL = settings.DEFAULT_FROM_EMAIL

from localcosmos_server.models import App

import re 

def send_registration_confirmation_email(user, app_uuid):

    app = App.objects.get(uuid=app_uuid)

    legal_notice = app.get_legal_notice()
    frontend = app.get_frontend()

    # backwards compatibility
    support_email = None
    if 'configuration' in frontend['userContent'] and 'supportEmail' in frontend['userContent']['configuration']:
        support_email = frontend['userContent']['configuration']['supportEmail']
    
    CLEANR = re.compile('<.*?>') 

    legal_notice_plain_text = re.sub(CLEANR, '', legal_notice)
        
    subject = '{0} {1}'.format(app.name, _('Registration confirmation'))
    from_email = FROM_EMAIL
    to = user.email

    legal_notice_url = reverse('legal_notice', kwargs={'app_uid':app.uid}, urlconf='localcosmos_server.urls')
    privacy_statement_url = reverse('privacy_statement', kwargs={'app_uid':app.uid},
                                    urlconf='localcosmos_server.urls')

    ctx = {
        'user' : user,
        'app' : app,
        'legal_notice' : legal_notice,
        'legal_notice_plain_text': legal_notice_plain_text,
        'site' : Site.objects.get_current(),
        'legal_notice_url' : legal_notice_url,
        'privacy_statement_url' : privacy_statement_url,
        'support_email': support_email,
    }

    text_message = render_to_string('email/registration_confirmation.txt', ctx)
    html_message = get_template('email/registration_confirmation.html').render(ctx)

    msg = EmailMultiAlternatives(subject, text_message, from_email=from_email, to=[to])
    msg.attach_alternative(html_message, 'text/html')
    
    msg.send()


def send_user_contact_email(app_uuid, sender, receiver, subject, message):
    
    app = App.objects.get(uuid=app_uuid)
    
    legal_notice = app.get_legal_notice()
    frontend = app.get_frontend()

    # backwards compatibility
    support_email = None
    if 'configuration' in frontend['userContent'] and 'supportEmail' in frontend['userContent']['configuration']:
        support_email = frontend['userContent']['configuration']['supportEmail']
    
    CLEANR = re.compile('<.*?>') 

    legal_notice_plain_text = re.sub(CLEANR, '', legal_notice)
    
    headers = {
        'Reply-To': sender.email
    }

    legal_notice_url = reverse('legal_notice', kwargs={'app_uid':app.uid}, urlconf='localcosmos_server.urls')
    privacy_statement_url = reverse('privacy_statement', kwargs={'app_uid':app.uid},
                                    urlconf='localcosmos_server.urls')
    ctx = {
        'sender' : sender,
        'receiver' : receiver,
        'app' : app,
        'site' : Site.objects.get_current(),
        'subject': subject,
        'message': message,
        'legal_notice_url' : legal_notice_url,
        'privacy_statement_url' : privacy_statement_url,
        'support_email': support_email,
    }
    
    from_email = FROM_EMAIL
    to = receiver.email

    text_message = render_to_string('email/contact_user.txt', ctx)
    html_message = get_template('email/contact_user.html').render(ctx)
    
    subject = '[{0}] {1}'.format(app.name, subject)

    msg = EmailMultiAlternatives(subject, text_message, from_email=from_email, to=[to], headers=headers)
    msg.attach_alternative(html_message, 'text/html')
    
    msg.send()
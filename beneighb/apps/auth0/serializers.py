from django.conf import settings
from dj_rest_auth.serializers import PasswordResetSerializer


class LinkPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        extra_context = {
            'email_site_name': 'Beneighb',
            'site_protocol': settings.SITE_PROTOCOL,
        }

        return {
            'domain_override': settings.SITE_LINK_URL,
            'email_template_name': 'reset_password_email.html',
            # We'll need it for sure
            # 'html_email_template_name': 'reset_password_email.html',
            'extra_email_context': extra_context,
            'subject_template_name': 'password_reset_subject.txt',
        }

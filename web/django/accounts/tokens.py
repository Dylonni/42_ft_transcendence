from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        email_field = user.get_email_field_name()
        email = getattr(user, email_field, '') or ''
        return (f'{user.pk}{timestamp}{email}')
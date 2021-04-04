import datetime

from django.db import models


class TokenManager(models.Manager):

    def delete_expired_tokens(self):
        now = datetime.datetime.now().astimezone(datetime.timezone.utc)
        for token in self.all():
            if now > token.expires_at:
                if token.type == token.REGISTRATION_TOKEN:
                    token.user.delete()
                token.delete()

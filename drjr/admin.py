from django.contrib import admin

from drjr.models import Token


class TokenAdmin(admin.ModelAdmin):
    list_display = ('token', )


admin.site.register(Token, TokenAdmin)

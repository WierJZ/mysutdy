from django.contrib import admin

# Register your models here.
from wlserver.models import Info, FAQ


class InfoAdmin(admin.ModelAdmin):
    list_display = (
        'customer_alias',
        'company',
        'plb',
        'app_flag',
    )


class FAQAdmin(admin.ModelAdmin):
    list_display = (
        'questions',
        'key_words',
    )


admin.site.register(Info, InfoAdmin)
admin.site.register(FAQ, FAQAdmin)

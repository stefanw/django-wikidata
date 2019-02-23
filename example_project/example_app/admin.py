from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Politician


class PoliticianAdmin(admin.ModelAdmin):
    actions = ['update_fields']

    def update_fields(self, request, queryset):
        for obj in queryset:
            obj.wikidata.update_fields()
            obj.save()
        self.message_user(request, _("Fields updated"))
    update_fields.short_description = _("Update fields from Wikidata")


admin.site.register(Politician, PoliticianAdmin)

from django.db import models
from django.utils import translation

from .fields import WikidataEntityField
from . import client


def get_string(value):
    try:
        lang = translation.get_language()
        return value[lang]
    except KeyError:
        pass
    return value


class DefaultWikidataMeta:
    field_mapping = None
    constraints = None


class WikidataProxy:
    def __init__(self, instance):
        self.instance = instance

    @property
    def options(self):
        if hasattr(self.instance, 'WikidataMeta'):
            return self.instance.WikidataMeta
        return DefaultWikidataMeta

    @property
    def model(self):
        return type(self.instance)

    def collect_fields(self):
        self.fields = {}
        for field in self.model._meta.get_fields():
            if isinstance(field, WikidataEntityField):
                self.fields[field.name] = field

    def update_fields(self):
        if self.options.field_mapping is None:
            return
        for field_name, definition in self.options.field_mapping:
            self.update_field(field_name, definition)

    def update_field(self, field_name, definition):
        value = self.get_mapping_value(definition)
        update_field = self.model._meta.get_field(field_name)
        update_value = self.get_update_field_value(update_field, value)
        setattr(self.instance, field_name, update_value)

    def get_update_field_value(self, update_field, value):
        if isinstance(update_field, (models.TextField, models.CharField)):
            return get_string(value)
        return value

    def get_mapping_value(self, definition):
        entity_field, accessor = definition
        entity = getattr(self.instance, entity_field)
        if isinstance(accessor, str):
            prop = client.get(accessor)
            return entity[prop]
        return accessor(entity)


class WikidataMixin:
    @property
    def wikidata(self):
        if not hasattr(self, '_wikidataproxy'):
            self._wikidataproxy = WikidataProxy(self)
        return self._wikidataproxy

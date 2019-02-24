from django.db import models
from django.core import exceptions

from wikidata.entity import Entity

from . import client
from .forms import WikidataItemFormField
from .widgets import WikidataItemWidget
from .validators import validate_wikidata_item


def make_entity(value):
    validate_wikidata_item(value)
    return client.get(value)


class EntityDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        if self.field.name in instance.__dict__:
            entity = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            entity = getattr(instance, self.field.name)

        if not entity:
            instance.__dict__[self.field.name] = None

        elif isinstance(entity, str):
            attr = make_entity(entity)
            instance.__dict__[self.field.name] = attr

        # That was fun, wasn't it?
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        if not value:
            instance.__dict__[self.field.name] = None
        elif isinstance(value, str):
            attr = make_entity(value)
            instance.__dict__[self.field.name] = attr
        elif isinstance(value, Entity):
            instance.__dict__[self.field.name] = value
        else:
            raise ValueError('Cannot assign "{}" to Wikidata Item Field'.format(value))


class WikidataEntityField(models.CharField):
    descriptor_class = EntityDescriptor
    empty_values = ()

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 50)
        kwargs.setdefault('default', '')
        super().__init__(*args, **kwargs)
        self.validators = []  # FIXME: validate length of QID

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def validate(self, value, model_instance):
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'], code='null')

        if not self.blank and value is None:
            raise exceptions.ValidationError(self.error_messages['blank'], code='blank')

    def from_db_value(self, value, expression, connection):
        if not value:
            return None
        return client.get(value)

    def to_python(self, value):
        if isinstance(value, Entity):
            return value

        if value is None:
            return value

        return client.get(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        value = self.to_python(value)
        return value.id

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = dict(kwargs)
        defaults.update({
            'form_class': WikidataItemFormField,
            'widget': WikidataItemWidget,
        })
        return super().formfield(**defaults)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class WikidataItemField(WikidataEntityField):
    pass

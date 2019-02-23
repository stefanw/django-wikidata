from django import forms

from .widgets import WikidataItemWidget
from .validators import validate_wikidata_item
from . import client


class WikidataItemFormField(forms.CharField):
    widget = WikidataItemWidget

    def to_python(self, value):
        """Normalize data to a list of strings."""
        # Return an empty list if no input was given.
        if not value:
            return None
        if isinstance(value, str):
            validate_wikidata_item(value)
            return client.get(value)
        return value

    def clean(self, value):
        """Check if value consists only of valid emails."""
        value = self.to_python(value)
        if value is None and self.required:
            raise forms.ValidationError(self.error_messages['required'], code='required')
        return value

    def prepare_value(self, value):
        return value.id

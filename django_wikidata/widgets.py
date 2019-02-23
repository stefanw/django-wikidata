from django.forms import widgets


class WikidataItemWidget(widgets.TextInput):
    def __init__(self, attrs=None):
        if attrs is not None:
            attrs = attrs.copy()
        if attrs is None:
            attrs = {}
        attrs.setdefault('pattern', 'Q\d+')
        super().__init__(attrs)

    def format_value(self, value):
        """
        Return a value as it should appear when rendered in a template.
        """
        if not value:
            return None
        return value

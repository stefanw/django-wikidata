from django.db import models

from django_wikidata.fields import WikidataItemField
from django_wikidata.mixins import WikidataMixin


class Politician(WikidataMixin, models.Model):
    name = models.CharField(max_length=255)
    wd_item = WikidataItemField()

    birth_date = models.DateField(null=True, blank=True)

    party = models.CharField(max_length=255)

    party_wd_item = WikidataItemField()

    class Meta:
        verbose_name = 'Politician'

    class WikidataMeta:
        field_mapping = [
            ('name', ('wd_item', lambda x: x.label)),
            ('birth_date', ('wd_item', 'P569')),
            ('party_wd_item', ('wd_item', 'P102')),
            ('party', ('party_wd_item', lambda x: x.label)),
        ]
        constraints = {
            'wd_item': [
                'P106 Q82955'
            ]
        }

    def __str__(self):
        return self.name


if __name__ == "__main__":
    politician = Politician()
    politician.wd_item = 'Q1'
    # politician.wd_item = Entity('Q1')
    politician.wikidata.load_fields()
    politician.save()

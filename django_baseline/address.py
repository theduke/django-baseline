from __future__ import unicode_literals

from django.db import models

from django_countries.fields import CountryField

from .forms import CrispyModelForm


class Address(models.Model):
    country = CountryField()
    postal_code = models.CharField(max_length=20)
    state = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    street = models.CharField(max_length=100)


class AddressForm(CrispyModelForm):
 
    class Meta:
        model = Address
        fields = ['country', 'state', 'town', 'postal_code', 'street']

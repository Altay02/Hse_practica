from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime #for checking renewal date range.

class MatrixForm(forms.Form):
    rows_size = forms.IntegerField()
    cols_size = forms.IntegerField()
    matrix = forms.CharField()

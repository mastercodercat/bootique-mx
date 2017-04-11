from django import forms
from django.forms import ModelForm

from routeplanning.models import *


class TailForm(ModelForm):
    class Meta:
        model = Tail
        fields = '__all__'

class LineForm(forms.Form):
    name = forms.CharField(label='Name', required=True)
    part1 = forms.CharField(label='Part of Line 1', required=True)
    part2 = forms.CharField(label='Part of Line 2', required=False)
    part3 = forms.CharField(label='Part of Line 3', required=False)
    part4 = forms.CharField(label='Part of Line 4', required=False)
    part5 = forms.CharField(label='Part of Line 5', required=False)
    part6 = forms.CharField(label='Part of Line 6', required=False)
    part7 = forms.CharField(label='Part of Line 7', required=False)
    part8 = forms.CharField(label='Part of Line 8', required=False)
    part9 = forms.CharField(label='Part of Line 9', required=False)
    part10 = forms.CharField(label='Part of Line 10', required=False)
    part11 = forms.CharField(label='Part of Line 11', required=False)
    part12 = forms.CharField(label='Part of Line 12', required=False)

    class Meta:
        fields = ('name',)

class FlightForm(ModelForm):
    class Meta:
        model = Flight
        fields = '__all__'

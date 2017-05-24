from django import forms
from django.forms import ModelForm

from inspection.models import *


class InspectionProgramForm(ModelForm):
    class Meta:
        model = InspectionProgram
        fields = '__all__'

class InspectionForm(ModelForm):
    class Meta:
        model = InspectionTask
        fields = '__all__'
        exclude = ('inspection_program', )

    def __init__(self, *args, **kwargs):
        super(InspectionForm, self).__init__(*args, **kwargs)
        self.fields['target'].widget.attrs['class'] = 'select2 m-b'

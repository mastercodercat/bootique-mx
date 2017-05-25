from django import forms
from django.forms import ModelForm

from inspection.models import *


class InspectionProgramForm(ModelForm):
    class Meta:
        model = InspectionProgram
        fields = '__all__'

class AddTaskForm(forms.Form):
    inspection_task = forms.ModelChoiceField(
        queryset=InspectionTask.objects.all(),
        label='Inspection Task',
        empty_label='(Not assigned)',
        required=True
    )

    class Meta:
        fields = ('inspection_task',)

    def __init__(self, *args, **kwargs):
        inspection_tasks = kwargs.pop('inspection_tasks')
        super(AddTaskForm, self).__init__(*args, **kwargs)
        self.fields['inspection_task'].queryset = inspection_tasks

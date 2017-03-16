from django import forms
from home.models import InspectionProgram


class AssignInspectionProgramForm(forms.Form):
    inspection_program = forms.ModelChoiceField(
        queryset=InspectionProgram.objects.all(),
        label='Inspection Program',
        empty_label='(Not assigned)',
        required=True
    )

    class Meta:
        fields = ('inspection_program',)

    def __init__(self, *args, **kwargs):
        super(AssignInspectionProgramForm, self).__init__(*args, **kwargs)
        self.fields['inspection_program'].widget.attrs['class'] = 'select2 m-b'

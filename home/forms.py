from django import forms

from inspection.models import InspectionProgram


class AssignInspectionProgramForm(forms.Form):
    inspection_program = forms.ModelChoiceField(
        queryset=InspectionProgram.objects.all(),
        label='Inspection Program',
        empty_label='(Not assigned)',
        required=True
    )

    class Meta:
        fields = ('inspection_program',)

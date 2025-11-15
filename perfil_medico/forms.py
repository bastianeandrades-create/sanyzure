from django import forms
from .models import MedicalProfile, Medication, LabTest, Allergy, ChronicCondition

class MedicalProfileForm(forms.ModelForm):
    class Meta:
        model = MedicalProfile
        fields = ['date_of_birth', 'gender', 'phone', 'emergency_contact', 'address', 'preferred_channel', 'preferred_time']

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'dosage', 'frequency', 'start_date', 'end_date', 'notes']

class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['test_name', 'last_date', 'next_scheduled_date', 'result_summary']

class AllergyForm(forms.ModelForm):
    class Meta:
        model = Allergy
        fields = ['name', 'notes']

class ConditionForm(forms.ModelForm):
    class Meta:
        model = ChronicCondition
        fields = ['name', 'notes']

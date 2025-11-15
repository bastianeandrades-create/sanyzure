from django.contrib import admin
from .models import MedicalProfile, Medication, LabTest, Allergy, ChronicCondition

admin.site.register(MedicalProfile)
admin.site.register(Medication)
admin.site.register(LabTest)
admin.site.register(Allergy)
admin.site.register(ChronicCondition)

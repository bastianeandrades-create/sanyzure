from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

CHANNEL_CHOICES = [
    ('push', 'Push'),
    ('sms', 'SMS'),
    ('email', 'Email'),
]

class MedicalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medical_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)

    # preferences
    preferred_channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='push')
    preferred_time = models.TimeField(null=True, blank=True)  # ej. 08:00 para recordatorios diarios

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil medico: {self.user.username}"

class Allergy(models.Model):
    profile = models.ForeignKey(MedicalProfile, on_delete=models.CASCADE, related_name='allergies')
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

class ChronicCondition(models.Model):
    profile = models.ForeignKey(MedicalProfile, on_delete=models.CASCADE, related_name='conditions')
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

class Medication(models.Model):
    profile = models.ForeignKey(MedicalProfile, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=200, blank=True)
    frequency = models.CharField(max_length=100, blank=True)  # e.g. "2 veces al día"
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.profile.user.username})"

class LabTest(models.Model):
    profile = models.ForeignKey(MedicalProfile, on_delete=models.CASCADE, related_name='labtests')
    test_name = models.CharField(max_length=200)
    last_date = models.DateField(null=True, blank=True)
    next_scheduled_date = models.DateField(null=True, blank=True)
    result_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


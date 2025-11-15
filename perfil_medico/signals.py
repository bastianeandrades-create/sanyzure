from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import MedicalProfile

@receiver(post_save, sender=User)
def create_or_update_medical_profile(sender, instance, created, **kwargs):
    if created:
        MedicalProfile.objects.create(user=instance)
    else:
        # opcional: actualizar timestamp
        instance.medical_profile.save()

from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError

class CustomUser(AbstractUser):
    phone_number = PhoneNumberField(
        blank=True, 
        null=True, 
        help_text="Format: +233201234567. Required for SMS OTP."
    )
    is_staff_member = models.BooleanField(default=False) 

    @property
    def phone_number_for_sms(self):
        if self.phone_number:
            return str(self.phone_number)
        return None

    def __str__(self):
        return self.username

# --- THE FIXED AUTO-CREATE STAFF LOGIC ---
@receiver(post_save, sender=CustomUser)
def create_or_update_staff_profile(sender, instance, created, **kwargs):
    from programs.models import StaffProfile 
    
    # Only create a StaffProfile if the user is actually staff/admin
    if instance.is_staff or instance.is_superuser or instance.is_staff_member:
        if created:
            StaffProfile.objects.get_or_create(user=instance)
        else:
            profile = getattr(instance, 'staff_profile', None)
            if profile:
                profile.save()
            else:
                StaffProfile.objects.get_or_create(user=instance)

# --- THE FIXED AUTO-CREATE STUDENT LOGIC ---
@receiver(post_save, sender=CustomUser)
def create_or_update_student_profile(sender, instance, created, **kwargs):
    from programs.models import StudentProfile 
    
    # ONLY create a StudentProfile if the user is NOT staff
    if not (instance.is_staff or instance.is_superuser or instance.is_staff_member):
        try:
            if created:
                StudentProfile.objects.get_or_create(user=instance)
            else:
                profile = getattr(instance, 'student_profile', None)
                if profile:
                    profile.save()
                else:
                    StudentProfile.objects.get_or_create(user=instance)
        except IntegrityError:
            # This prevents the crash if a student_id conflict occurs
            pass
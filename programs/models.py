from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings 

# --- EXISTING MODELS (UNTOUCHED: Category, Program, CourseRegistration, GoverningCouncil) ---

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Program(models.Model):
    LEVEL_CHOICES = [
        ('undergraduate', 'Qualifications for Professionals'),
        ('postgraduate', 'Postgraduate'),
        ('professional', 'Professional'),
    ]

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='programs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True) 
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='postgraduate')
    
    external_url = models.URLField(
        max_length=500, 
        blank=True, 
        null=True, 
        help_text="Enter the unique external URL for this programme (e.g., https://ugc.edu.gh/your-link)"
    )

    affiliation = models.CharField(
        max_length=200, 
        default="University of the West of Scotland",
        blank=True, 
        null=True
    )
    
    summary = models.TextField(help_text="A brief overview for the search results page.")
    description = models.TextField(help_text="Full course details, requirements, and curriculum.")
    duration = models.CharField(max_length=50, default="12 Months")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.external_url:
            return self.external_url
        return reverse('programs:program_detail', kwargs={'slug': self.slug})

class CourseRegistration(models.Model):
    REG_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('resit', 'Resit / Re-take'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    registration_type = models.CharField(max_length=20, choices=REG_TYPE_CHOICES, default='regular')
    study_month = models.CharField(max_length=20, help_text="The month selected for study start.")
    payment_proof = models.FileField(upload_to='registrations/payments/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Course Registration"
        verbose_name_plural = "Course Registrations"

    def __str__(self):
        return f"{self.full_name} - {self.program.title}"

class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    is_abs_portal_staff = models.BooleanField(default=True, help_text="Designates whether this user can access the custom ABS Staff Dashboard.")

    def __str__(self):
        return f"Staff: {self.user.username}"

class GoverningCouncil(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to='council/')
    bio = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Governing Council Member"
        verbose_name_plural = "Governing Council Members"

    def __str__(self):
        return self.name

# --- UPDATED STUDY ROOM SECTION ---

class StudyRoom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    floor = models.IntegerField(default=1)
    capacity = models.IntegerField(default=4)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    """Links a Django User to a Student identity. This is the source of truth for the ID."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    
    # FIX: Added null=True and blank=True. 
    # This prevents the UNIQUE constraint crash when signals create empty profiles.
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_active_student = models.BooleanField(default=True)

    def __str__(self):
        # Handle cases where student_id might be None
        sid = self.student_id if self.student_id else "No ID"
        return f"Student: {self.user.username} ({sid})"

class RoomReservation(models.Model):
    """The permanent log of who used which room."""
    TIME_SLOTS = [
        ('09:00-11:00', '09:00 - 11:00'),
        ('11:00-13:00', '11:00 - 13:00'),
        ('14:00-16:00', '14:00 - 16:00'),
        ('16:00-18:00', '16:00 - 18:00'),
    ]

    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='reservations')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='room_reservations'
    )
    
    student_name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    date = models.DateField()
    time_slot = models.CharField(max_length=50) # Increased length to handle formatted time slots
    reserved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.room.name} ({self.date})"
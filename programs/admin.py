import re
from datetime import datetime
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Category, Program, StaffProfile, GoverningCouncil, CourseRegistration, StudyRoom, RoomReservation, StudentProfile

User = get_user_model()

# --- 1. USER + STUDENT PROFILE INTEGRATION ---

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile Information'
    extra = 0 
    max_num = 1

class UserAdmin(BaseUserAdmin):
    inlines = (StudentProfileInline,)
    list_display = ('username', 'get_student_id', 'email', 'is_staff', 'is_active')
    
    def get_student_id(self, instance):
        return instance.student_profile.student_id if hasattr(instance, 'student_profile') else "-"
    get_student_id.short_description = 'Student ID'

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)

# --- 2. STUDENT PROFILE REGISTRATION ---

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'phone_number', 'is_active_student')
    search_fields = ('user__username', 'student_id', 'phone_number')
    list_filter = ('is_active_student',)

# --- 3. EXISTING ADMIN CONFIGURATIONS ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'duration', 'is_active')
    list_filter = ('category', 'is_active', 'level')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'is_abs_portal_staff')
    list_filter = ('is_abs_portal_staff',)
    search_fields = ('user__username', 'employee_id')
    list_editable = ('is_abs_portal_staff',)

@admin.register(GoverningCouncil)
class GoverningCouncilAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'role')

@admin.register(CourseRegistration)
class CourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'program', 'registration_type', 'submitted_at')
    list_filter = ('program', 'registration_type', 'submitted_at')
    search_fields = ('full_name', 'email', 'phone_number')
    readonly_fields = ('submitted_at',)

# --- 4. STUDY ROOM & RESERVATION UPDATES (FIXED FOR DATE + AM/PM) ---

@admin.register(StudyRoom)
class StudyRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'floor', 'capacity', 'is_available')
    list_filter = ('floor', 'is_available')
    list_editable = ('is_available',)
    search_fields = ('name',)

@admin.register(RoomReservation)
class RoomReservationAdmin(admin.ModelAdmin):
    list_display = (
        'room', 
        'student_name', 
        'get_arrival',      # Now shows Date + AM/PM
        'get_departure',    # Now shows Date + AM/PM
        'student_id', 
        'date',
        'reserved_at',
    )
    list_filter = ('date', 'room__floor', 'reserved_at')
    search_fields = ('student_name', 'student_id', 'email', 'phone_number')
    readonly_fields = ('reserved_at',)
    
    def _format_datetime_combined(self, obj_date, time_str):
        """Helper to combine the model date with the parsed time slot into a pretty format"""
        if not time_str: return "-"
        time_str = time_str.strip()
        
        # Handle cases where time_str might already contain a date (cleaning)
        if " " in time_str and ":" in time_str:
            time_str = time_str.split(" ")[-1]
        
        try:
            # Parse the time string (HH:MM)
            parsed_time = datetime.strptime(time_str[:5], "%H:%M").time()
            # Combine with the actual reservation date field
            combined = datetime.combine(obj_date, parsed_time)
            # Return format: "Feb. 16, 2026, 09:00 AM"
            return combined.strftime("%b. %d, %Y, %I:%M %p")
        except:
            # Fallback if parsing fails
            return f"{obj_date} {time_str}"

    def get_arrival(self, obj):
        if not obj.time_slot: return "-"
        # Split by " TO " (from views) or "-" (from models)
        if " TO " in obj.time_slot:
            raw_arrival = obj.time_slot.split(" TO ")[0]
        elif "-" in obj.time_slot:
            raw_arrival = obj.time_slot.split("-")[0]
        else:
            raw_arrival = obj.time_slot
            
        return self._format_datetime_combined(obj.date, raw_arrival)
    get_arrival.short_description = 'Arrival'

    def get_departure(self, obj):
        if not obj.time_slot: return "-"
        raw_dep = None
        if " TO " in obj.time_slot:
            raw_dep = obj.time_slot.split(" TO ")[1]
        elif "-" in obj.time_slot:
            parts = obj.time_slot.split("-")
            if len(parts) > 1:
                raw_dep = parts[1]
        
        if raw_dep:
            return self._format_datetime_combined(obj.date, raw_dep)
        return "-"
    get_departure.short_description = 'Departure'

    fieldsets = (
        ('Reservation Detail', {
            'fields': ('room', 'date', 'time_slot')
        }),
        ('Student Record', {
            'description': 'These details are captured at the time of booking.',
            'fields': ('user', 'student_name', 'student_id', 'email', 'phone_number')
        }),
        ('System Log', {
            'fields': ('reserved_at',),
            'classes': ('collapse',)
        }),
    )
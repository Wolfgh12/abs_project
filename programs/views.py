from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Program, Category, GoverningCouncil, CourseRegistration, StudyRoom, RoomReservation, StudentProfile
from .forms import ProgramForm 
from datetime import date 

# STANDARD AUTH IMPORTS
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse
from functools import wraps
from django.contrib.auth.decorators import login_required

# --- 1. LOCKDOWN REDIRECT LOGIC ---

def role_based_redirect(user):
    """ Helper to send logged-in users to their correct portal """
    if user.is_superuser:
        return redirect('admin:index')
    if user.is_staff:
        # IRONCLAD: Staff always land on the Logs Table
        return redirect('programs:staff_room_bookings')
    if hasattr(user, 'student_profile'):
        return redirect('programs:study_room_reservation')
    
    return redirect('programs:program_list')

def redirect_if_authenticated(view_func):
    """ Decorator to prevent logged-in users from seeing public pages """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return role_based_redirect(request.user)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- 2. AUTHENTICATION VIEWS ---

class ABSLoginView(LoginView):
    template_name = 'programs/student_login.html'
    
    def get_success_url(self):
        user = self.request.user
        
        # --- IRONCLAD LOGIC STARTS HERE ---
        
        # 1. PRIORITY ONE: Staff/Superusers ALWAYS go to their specific portal logs
        if user.is_superuser:
            return reverse('admin:index')
        if user.is_staff:
            return reverse('programs:staff_room_bookings')

        # 2. PRIORITY TWO: Check for 'next' parameter (only for students now)
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        
        # 3. PRIORITY THREE: Default landing for students
        if hasattr(user, 'student_profile'):
            return reverse('programs:study_room_reservation')
            
        return reverse('programs:program_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return role_based_redirect(request.user)
        return super().dispatch(request, *args, **kwargs)

def student_login(request):
    """ Bridge function to the Class Based View """
    return ABSLoginView.as_view()(request)

def student_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('programs:program_list')

# --- 3. STAFF DECORATORS & PORTALS ---

def abs_staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # We maintain the 'next' here so they return to where they were AFTER they pass the ironclad check
            return redirect(f"{reverse('programs:student_login')}?next={request.path}")
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Staff access required.")
        return role_based_redirect(request.user)
    return _wrapped_view

@abs_staff_required
def staff_room_portal(request):
    """ Entry point: Always redirects to the bookings table. """
    return redirect('programs:staff_room_bookings')

# --- 4. STAFF DASHBOARD & PROGRAM MANAGEMENT ---

@abs_staff_required
def staff_dashboard(request):
    if request.user.is_superuser:
        return redirect('admin:index')
    all_programs = Program.objects.all().order_by('-id')
    return render(request, 'programs/dashboard.html', {'programs': all_programs})

@abs_staff_required
def add_program(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Programme added successfully!")
            return redirect('programs:staff_dashboard')
    else:
        form = ProgramForm()
    return render(request, 'programs/program_form.html', {'form': form, 'title': 'Add New Programme'})

@abs_staff_required
def edit_program(request, slug):
    program = get_object_or_404(Program, slug=slug) 
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, f"{program.title} updated successfully!")
            return redirect('programs:staff_dashboard')
    else:
        form = ProgramForm(instance=program)
    return render(request, 'programs/program_form.html', {'form': form, 'title': f'Edit {program.title}'})

# --- 5. ROOM RESERVATION LOGS (THE TABLE) ---

@abs_staff_required
def staff_room_bookings(request):
    bookings = RoomReservation.objects.all().order_by('-reserved_at')
    return render(request, 'programs/staff_bookings.html', {'bookings': bookings})

@abs_staff_required
def clear_all_bookings(request):
    if request.method == 'POST':
        count = RoomReservation.objects.count()
        RoomReservation.objects.all().delete()
        messages.success(request, f"System Purge Successful: {count} logs cleared.")
    return redirect('programs:staff_room_bookings')

@abs_staff_required
def delete_single_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(RoomReservation, id=booking_id)
        name = booking.student_name
        booking.delete()
        messages.success(request, f"Log for {name} deleted.")
    return redirect('programs:staff_room_bookings')

# --- 6. FRONTEND ROOM GRID (THE DASHBOARD) ---

@abs_staff_required
def staff_room_dashboard(request):
    rooms = StudyRoom.objects.all().order_by('name')
    active_bookings = RoomReservation.objects.filter(date=date.today())
    context = {
        'rooms': rooms,
        'active_bookings': active_bookings,
        'occupied_count': rooms.filter(is_available=False).count(),
        'available_count': rooms.filter(is_available=True).count(),
    }
    return render(request, 'programs/staff_room_dashboard.html', context)

@abs_staff_required
def release_room(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    room.is_available = True
    room.save()
    messages.info(request, f"{room.name} has been released.")
    return redirect('programs:staff_room_dashboard')

@abs_staff_required
def toggle_room_status(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    room.is_available = not room.is_available
    room.save()
    status = "Available" if room.is_available else "Occupied"
    messages.success(request, f"{room.name} is now {status}.")
    return redirect('programs:staff_room_dashboard')

# --- 7. PUBLIC VIEWS (Omitted for brevity, kept same as your provided code) ---

@redirect_if_authenticated
def program_list(request):
    programs = Program.objects.filter(is_active=True).order_by('title')
    categories = Category.objects.all()
    return render(request, 'programs/list.html', {'programs': programs, 'categories': categories})

# [Other Public Views remain identical...]
@redirect_if_authenticated
def program_detail(request, slug):
    program = get_object_or_404(Program, slug=slug, is_active=True)
    return render(request, 'programs/detail.html', {'program': program})

@redirect_if_authenticated
def admission(request): return render(request, 'programs/admission.html')

@redirect_if_authenticated
def president_message(request): return render(request, 'programs/president.html')

@redirect_if_authenticated
def about_abs(request): return render(request, 'programs/abs.html')

@redirect_if_authenticated
def governing_council(request):
    members = GoverningCouncil.objects.all()
    return render(request, 'programs/gc.html', {'members': members})

@redirect_if_authenticated
def accreditation(request): return render(request, 'programs/accreditation.html')

@redirect_if_authenticated
def contact(request): return render(request, 'programs/contact.html')

@redirect_if_authenticated
def registry(request): return render(request, 'programs/registry.html')

# --- 8. STUDENT SERVICES & REGISTRATION ---

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('programs:student_login')}?next={request.path}") 
        if not hasattr(request.user, 'student_profile'):
            messages.error(request, "Access denied.")
            return role_based_redirect(request.user)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@student_required
def study_room_reservation(request):
    rooms = StudyRoom.objects.all().order_by('name')
    student_profile = request.user.student_profile
    
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        arrival = request.POST.get('arrival_datetime')
        departure = request.POST.get('departure_datetime')
        
        arrival_time = arrival.split('T')[1] if arrival and 'T' in arrival else "N/A"
        departure_time = departure.split('T')[1] if departure and 'T' in departure else "N/A"
        custom_slot = f"{arrival_time} TO {departure_time}"
        reservation_date = arrival.split('T')[0] if arrival else date.today()

        try:
            room_obj = StudyRoom.objects.get(name=room_name)
            if room_obj.is_available:
                RoomReservation.objects.create(
                    room=room_obj,
                    user=request.user,
                    student_name=request.user.get_full_name() or request.user.username,
                    student_id=student_profile.student_id or "-",
                    email=request.user.email or "-",
                    phone_number=student_profile.phone_number or "Not Provided",
                    date=reservation_date,
                    time_slot=custom_slot
                )
                room_obj.is_available = False
                room_obj.save()
                messages.success(request, f"Reservation confirmed for {room_name}!")
                return redirect('programs:room_reservation_grid')
        except Exception as e:
            messages.error(request, f"Booking Error: {e}")

    return render(request, 'programs/rr.html', {'rooms': rooms, 'student': student_profile})

@student_required
def room_reservation_grid(request):
    return study_room_reservation(request)

@redirect_if_authenticated
def course_registration_view(request):
    programs = Program.objects.filter(is_active=True)
    return render(request, 'programs/course_registration.html', {'programs': programs})

@redirect_if_authenticated
def registration_success(request):
    return render(request, 'programs/success.html')

def student_request_view(request):
    return render(request, 'student_request.html')
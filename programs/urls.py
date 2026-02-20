from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

# This namespace is critical for reverse('programs:staff_dashboard') to work
app_name = 'programs'

urlpatterns = [
    # --- PUBLIC STATIC PATHS ---
    path('', views.program_list, name='program_list'),
    path('admission/', views.admission, name='admission'), 
    path('message-from-the-president/', views.president_message, name='president_message'),
    path('about-accra-business-school/', views.about_abs, name='about_abs'),
    path('governing-council/', views.governing_council, name='governing_council'),
    path('accreditation/', views.accreditation, name='accreditation'),
    path('contact/', views.contact, name='contact'),

    # --- AUTHENTICATION (STUDENT & STAFF) ---
    path('student/login/', views.student_login, name='student_login'),
    # Fixed: Explicitly redirects student logout to the homepage
    path('student/logout/', LogoutView.as_view(next_page='home'), name='student_logout'),
    
    # NEW: Specific path for staff to logout and return home
    path('staff/logout/', LogoutView.as_view(next_page='home'), name='staff_logout'),

    # --- STUDENT SERVICES ---
    path('student-request/', views.student_request_view, name='student_request'),
    path('study-room-reservation/', views.study_room_reservation, name='study_room_reservation'),
    path('study-room-grid/', views.room_reservation_grid, name='room_reservation_grid'),

    # --- REGISTRATION FLOW ---
    path('course-registration/', views.course_registration_view, name='course_registration'),
    path('course-registration/success/', views.registration_success, name='registration_success'),

    # --- STAFF DASHBOARD SECTION ---
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/add-program/', views.add_program, name='add_program'),
    path('dashboard/edit/<slug:slug>/', views.edit_program, name='edit_program'),
    
    # The landing page that your 'Staff Login / Dashboard' link points to
    path('staff/room-control/', views.staff_room_portal, name='staff_room_portal'),
    
    # Advanced Frontend Room Dashboard (Visual grid)
    path('dashboard/rooms/', views.staff_room_dashboard, name='staff_room_dashboard'),
    
    # Logic to release a room
    path('dashboard/rooms/release/<int:room_id>/', views.release_room, name='release_room'),

    # --- THE UPDATE: TOGGLE ROOM STATUS ---
    path('dashboard/rooms/toggle/<int:room_id>/', views.toggle_room_status, name='toggle_room_status'),

    # Table view for student IDs, emails, etc. (This is where the logs live)
    path('dashboard/room-bookings/', views.staff_room_bookings, name='staff_room_bookings'),
    
    # --- THE PURGE: DELETE ALL BOOKING LOGS ---
    path('dashboard/room-bookings/purge/', views.clear_all_bookings, name='clear_all_bookings'),
    
    # --- NEW: DELETE SINGLE BOOKING LOG ---
    path('dashboard/room-bookings/delete/<int:booking_id>/', views.delete_single_booking, name='delete_single_booking'),
    
    # --- DYNAMIC SLUG PATH ---
    path('<slug:slug>/', views.program_detail, name='program_detail'),
]
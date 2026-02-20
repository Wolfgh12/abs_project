from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from core import views as core_views
from programs.views import ABSLoginView, registry, course_registration_view, registration_success
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- SHARED AUTHENTICATION ---
    path('account/login/', ABSLoginView.as_view(), name='login'),
    
    # FIXED: This specifically handles the global logout and forces it to 'home'
    path('account/logout/', LogoutView.as_view(next_page='home'), name='logout'),
    
    # --- PUBLIC & APP VIEWS ---
    path('', core_views.home, name='home'),
    path('programs/', include('programs.urls', namespace='programs')),
    path('registry/', registry, name='registry'), 
    
    # --- COURSE & ROOM RESERVATION ---
    path('course-registration/', course_registration_view, name='course_registration'),
    path('room-reservation/', core_views.room_reservation, name='room_reservation'), 
    
    # --- SUCCESS PAGE ---
    path('course-registration/success/', registration_success, name='registration_success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.error_404'
handler403 = 'core.views.error_403'
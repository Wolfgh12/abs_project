from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden

def home(request):
    return render(request, 'core/index.html')

def student_request_view(request):
    return render(request, 'student_request.html')

def room_reservation(request):
    return render(request, 'rr.html')

def error_404(request, exception):
    """Custom 404 error page."""
    try:
        return render(request, '404.html', status=404)
    except:
        return render(request, 'core/index.html', status=404) # Fallback to index

def error_403(request, exception=None):
    """
    Custom 403 error page. 
    Fixed: Added a try/except block to prevent TemplateDoesNotExist crash.
    """
    try:
        return render(request, '403.html', status=403)
    except:
        return HttpResponseForbidden(
            "<h1>403 Forbidden</h1>"
            "<p>Access Denied: You do not have permission to view the User list.</p>"
            "<a href='/admin/'>Return to Admin Dashboard</a>"
        )
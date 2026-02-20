from django import forms
from .models import Program, RoomReservation, StudyRoom

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['category', 'title', 'level', 'affiliation', 'duration', 'description', 'is_active']
        
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gold outline-none'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gold outline-none',
                'placeholder': 'e.g. Master of Business Administration'
            }),
            'level': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gold outline-none'
            }),
            'affiliation': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gold outline-none',
                'placeholder': 'e.g. University of the West of Scotland'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gold outline-none',
                'placeholder': 'e.g. 12 Months'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gold outline-none', 
                'rows': 5,
                'placeholder': 'Enter full programme details...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 accent-gold cursor-pointer'
            }),
        }

# --- UPDATED: FORM FOR FRONTEND ROOM RESERVATIONS ---

class RoomReservationForm(forms.ModelForm):
    # Updated these fields to match the arrival/departure naming in rr.html
    arrival_datetime = forms.CharField(required=False)
    departure_datetime = forms.CharField(required=False)

    class Meta:
        model = RoomReservation
        fields = ['room', 'student_name', 'student_id', 'email', 'phone_number', 'date', 'time_slot']
        
        widgets = {
            'room': forms.Select(attrs={'class': 'hidden'}), 
            'student_name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded focus:border-gold outline-none text-sm',
                'placeholder': 'Full Name'
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded focus:border-gold outline-none text-sm',
                'placeholder': 'ABS-XXXXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded focus:border-gold outline-none text-sm',
                'placeholder': 'student@abs.edu.gh'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded focus:border-gold outline-none text-sm',
                'placeholder': '02XXXXXXXX'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded focus:border-gold outline-none text-sm',
                'type': 'date'
            }),
            'time_slot': forms.HiddenInput(), # Remains hidden as we combine arrival/departure
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Get the new arrival/departure data
        arrival = self.cleaned_data.get('arrival_datetime')
        departure = self.cleaned_data.get('departure_datetime')
        
        # Format for the database record
        if arrival and departure:
            # Replaces the 'T' from the HTML input with a space for readability
            clean_arrival = arrival.replace('T', ' ')
            clean_departure = departure.replace('T', ' ')
            instance.time_slot = f"{clean_arrival} TO {clean_departure}"
            
            # Auto-populate the date field from the arrival date
            instance.date = arrival.split('T')[0]
            
        if commit:
            instance.save()
        return instance

# --- NEW: FORM FOR STAFF TO QUICK-UPDATE ROOM STATUS ---

class RoomStatusForm(forms.ModelForm):
    class Meta:
        model = StudyRoom
        fields = ['is_available']
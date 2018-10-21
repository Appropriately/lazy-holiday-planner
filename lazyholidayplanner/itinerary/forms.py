from django import forms
from .models import Visit, Trip
from datetime import datetime, timezone


class TripAddForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        arrival_time = cleaned_data['arrival_time']
        leaving_time = cleaned_data['leaving_time']
        if not (arrival_time < leaving_time):
            raise forms.ValidationError(
                'The leaving time must be after the arrival time')
        now = datetime.now(timezone.utc)
        if arrival_time < now:
            raise forms.ValidationError('Arrival time must be later than now')
        if leaving_time < now:
            raise forms.ValidationError('Leaving time must be later than now')
        return cleaned_data

    class Meta:
        model = Visit
        fields = ['arrival_time', 'leaving_time', 'location', 'trip']
        widgets = {
            'arrival_time': forms.DateTimeInput(
                attrs={'placeholder': 'mm/dd/yyyy hh:MM'}),
            'leaving_time': forms.DateTimeInput(
                attrs={'placeholder': 'mm/dd/yyyy hh:MM'}),
            'trip': forms.HiddenInput(),
        }

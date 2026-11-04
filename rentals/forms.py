from django import forms
from django.utils import timezone

from accounts.models import CustomerProfile
from catalog.models import MovieCopy
from .models import Rental


class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ["customer", "movie_copy", "due_date"]
        widgets = {
            "due_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["customer"].queryset = (
            CustomerProfile.objects.all()
        )

        self.fields["movie_copy"].queryset = (
            MovieCopy.objects.filter(
                status=MovieCopy.AvailabilityStatus.AVAILABLE
            )
        )

    def clean_due_date(self):
        due_date = self.cleaned_data["due_date"]

        if due_date < timezone.localdate():
            raise forms.ValidationError(
                "The due date cannot be in the past."
            )

        return due_date

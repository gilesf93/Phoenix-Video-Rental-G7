from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CustomerRegistrationForm(UserCreationForm):
    """Registration form with required, unique customer email validation."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        """Prevent multiple accounts from using the same email address."""
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email
    
from .models import CustomerProfile


class StaffCustomerForm(forms.ModelForm):
    """Form for staff to create and edit customer records."""

    phone = forms.CharField(
        max_length=20,
        required=False,
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            profile = CustomerProfile.objects.filter(
                user=self.instance
            ).first()

            if profile:
                self.fields["phone"].initial = profile.phone

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        existing = User.objects.filter(email__iexact=email)

        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        if not user.pk:
            user.set_unusable_password()

        if commit:
            user.save()

            CustomerProfile.objects.update_or_create(
                user=user,
                defaults={
                    "phone": self.cleaned_data.get("phone", "")
                },
            )

        return user


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Doctor, Patient, Appointment


class DoctorLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )


class PatientLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )


class DoctorForm(forms.ModelForm):
    # Optional account fields to create a linked User when creating a doctor
    username = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Doctor
        fields = [
            "name",
            "specialty",
            "phone",
            "email",
            "username",
            "password1",
            "password2",
        ]

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if username:
            # ensure username is unique
            if User.objects.filter(username=username).exists():
                self.add_error("username", "Username already taken.")
            # if username provided, require passwords and match
            if not p1 or not p2:
                self.add_error(
                    "password1", "Password is required when creating an account."
                )
            elif p1 != p2:
                self.add_error("password2", "Passwords do not match.")

        return cleaned

    def save(self, commit=True):
        # Create Doctor instance first
        doctor = super().save(commit=False)
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password1")
        if username:
            user = User.objects.create_user(username=username)
            user.set_password(password)
            user.save()
            doctor.user = user
        if commit:
            doctor.save()
        return doctor


class UnifiedLoginForm(AuthenticationForm):
    ROLE_CHOICES = (
        ("patient", "Patient"),
        ("doctor", "Doctor"),
        ("receptionist", "Receptionist"),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES, widget=forms.Select(attrs={"class": "form-control"})
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )


class PatientForm(forms.ModelForm):
    admitted_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = Patient
        fields = [
            "name",
            "age",
            "gender",
            "address",
            "phone",
            "admitted_date",
            "doctor",
        ]

    # Optional fields for creating a linked User account
    username = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if username:
            if User.objects.filter(username=username).exists():
                self.add_error("username", "Username already taken.")
            if not p1 or not p2:
                self.add_error(
                    "password1", "Password is required when creating an account."
                )
            elif p1 != p2:
                self.add_error("password2", "Passwords do not match.")

        return cleaned

    def save(self, commit=True):
        patient = super().save(commit=False)
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password1")
        if username:
            user = User.objects.create_user(username=username)
            user.set_password(password)
            user.save()
            patient.user = user
        if commit:
            patient.save()
        return patient


class AppointmentRequestForm(forms.ModelForm):
    requested_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        help_text="Select preferred date and time for your appointment",
    )

    class Meta:
        model = Appointment
        fields = ["doctor", "requested_date", "symptoms"]
        widgets = {
            "symptoms": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe your symptoms or reason for visit...",
                }
            ),
        }


class AppointmentApprovalForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["status", "receptionist_notes"]
        widgets = {
            "receptionist_notes": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Add notes for the doctor..."}
            ),
        }

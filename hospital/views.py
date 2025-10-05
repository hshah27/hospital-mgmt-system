from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Doctor, Patient, Appointment
from .forms import (
    DoctorForm,
    PatientForm,
    DoctorLoginForm,
    PatientLoginForm,
    AppointmentRequestForm,
    AppointmentApprovalForm,
)


def About(request):
    return render(request, "about.html")


def Home(request):
    doctors_count = Doctor.objects.count()
    patients_count = Patient.objects.count()
    context = {"doctors_count": doctors_count, "patients_count": patients_count}
    return render(request, "home.html", context)


# Authentication Views
def doctor_login(request):
    if request.method == "POST":
        form = DoctorLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if user is associated with a doctor
                try:
                    doctor = Doctor.objects.get(user=user)
                    login(request, user)
                    messages.success(request, f"Welcome back, Dr. {doctor.name}!")
                    return redirect("doctor_dashboard")
                except Doctor.DoesNotExist:
                    messages.error(request, "You are not registered as a doctor.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = DoctorLoginForm()

    return render(request, "doctor_login.html", {"form": form})


def patient_login(request):
    if request.method == "POST":
        form = PatientLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if user is associated with a patient
                try:
                    patient = Patient.objects.get(user=user)
                    login(request, user)
                    messages.success(request, f"Welcome back, {patient.name}!")
                    return redirect("patient_dashboard")
                except Patient.DoesNotExist:
                    messages.error(request, "You are not registered as a patient.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = PatientLoginForm()

    return render(request, "patient_login.html", {"form": form})


def unified_login(request):
    """Unified login for patient, doctor, receptionist"""
    from .forms import UnifiedLoginForm

    if request.method == "POST":
        form = UnifiedLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            role = form.cleaned_data.get("role")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Role-based checks
                if role == "doctor":
                    if Doctor.objects.filter(user=user).exists():
                        login(request, user)
                        messages.success(request, f"Welcome back, Dr. {user.username}!")
                        return redirect("doctor_dashboard")
                    else:
                        messages.error(request, "You are not registered as a doctor.")
                elif role == "patient":
                    if Patient.objects.filter(user=user).exists():
                        login(request, user)
                        messages.success(request, f"Welcome back, {user.username}!")
                        return redirect("patient_dashboard")
                    else:
                        messages.error(request, "You are not registered as a patient.")
                elif role == "receptionist":
                    # Receptionist requires staff flag for now
                    if user.is_staff:
                        login(request, user)
                        messages.success(request, "Welcome, Receptionist!")
                        return redirect("receptionist_dashboard")
                    else:
                        messages.error(
                            request, "Receptionist access requires staff privileges."
                        )
                else:
                    messages.error(request, "Invalid role selected.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UnifiedLoginForm()

    return render(request, "login.html", {"form": form})


@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        patients = Patient.objects.filter(doctor=doctor)
        context = {
            "doctor": doctor,
            "patients": patients,
            "patient_count": patients.count(),
        }
        return render(request, "doctor_dashboard.html", context)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect("doctor_login")


@login_required
def patient_dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
        # Get patient's appointments
        appointments = (
            Appointment.objects.filter(patient=patient)
            .select_related("doctor")
            .order_by("-created_at")
        )

        context = {
            "patient": patient,
            "appointments": appointments,
        }
        return render(request, "patient_dashboard.html", context)
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect("patient_login")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")


# Existing views
def doctor_list(request):
    doctors = Doctor.objects.all().order_by("name")
    return render(request, "doctor_list.html", {"doctors": doctors})


def doctor_create(request):
    if request.method == "POST":
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("doctor_list")
    else:
        form = DoctorForm()
    return render(request, "doctor_form.html", {"form": form})


def patient_list(request):
    patients = Patient.objects.select_related("doctor").all().order_by("name")
    return render(request, "patient_list.html", {"patients": patients})


def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("patient_list")
    else:
        form = PatientForm()
    return render(request, "patient_form.html", {"form": form})


# Appointment Views
@login_required
def appointment_request(request):
    """Patient requests a new appointment"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect("patient_login")

    if request.method == "POST":
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            messages.success(
                request,
                "Your appointment request has been submitted and is pending approval.",
            )
            return redirect("patient_dashboard")
    else:
        form = AppointmentRequestForm()

    return render(request, "appointment_request.html", {"form": form})


@login_required
def receptionist_dashboard(request):
    """Receptionist manages appointment requests"""
    # For now, using admin check - in production, you'd have a receptionist role
    if not request.user.is_staff:
        messages.error(request, "Access denied. Receptionist privileges required.")
        return redirect("home")

    pending_appointments = Appointment.objects.filter(status="pending").select_related(
        "patient", "doctor"
    )
    approved_appointments = Appointment.objects.filter(
        status="approved"
    ).select_related("patient", "doctor")

    context = {
        "pending_appointments": pending_appointments,
        "approved_appointments": approved_appointments,
    }
    return render(request, "receptionist_dashboard.html", context)


@login_required
def approve_appointment(request, appointment_id):
    """Receptionist approves an appointment"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("home")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        form = AppointmentApprovalForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            status = form.cleaned_data["status"]
            if status == "approved":
                messages.success(
                    request,
                    f"Appointment for {appointment.patient.name} has been approved.",
                )
            elif status == "rejected":
                messages.success(
                    request,
                    f"Appointment for {appointment.patient.name} has been rejected.",
                )
            return redirect("receptionist_dashboard")
    else:
        form = AppointmentApprovalForm(instance=appointment)

    return render(
        request, "appointment_approval.html", {"form": form, "appointment": appointment}
    )


@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        patients = Patient.objects.filter(doctor=doctor)
        # Get approved appointments for this doctor
        approved_appointments = (
            Appointment.objects.filter(doctor=doctor, status="approved")
            .select_related("patient")
            .order_by("requested_date")
        )

        context = {
            "doctor": doctor,
            "patients": patients,
            "patient_count": patients.count(),
            "approved_appointments": approved_appointments,
            "appointment_count": approved_appointments.count(),
        }
        return render(request, "doctor_dashboard.html", context)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect("doctor_login")

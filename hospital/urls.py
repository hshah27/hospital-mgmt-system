from django.urls import path
from hospital.views import (
    About,
    Home,
    doctor_list,
    doctor_create,
    patient_list,
    patient_create,
    doctor_login,
    patient_login,
    unified_login,
    doctor_dashboard,
    patient_dashboard,
    logout_view,
    appointment_request,
    receptionist_dashboard,
    approve_appointment,
)

urlpatterns = [
    path("", Home, name="home"),
    path("about/", About, name="about"),
    # Authentication
    path("login/", unified_login, name="login"),
    path("doctor/dashboard/", doctor_dashboard, name="doctor_dashboard"),
    path("patient/dashboard/", patient_dashboard, name="patient_dashboard"),
    path("logout/", logout_view, name="logout"),
    # Appointments
    path("appointment/request/", appointment_request, name="appointment_request"),
    path(
        "receptionist/dashboard/", receptionist_dashboard, name="receptionist_dashboard"
    ),
    path(
        "appointment/<int:appointment_id>/approve/",
        approve_appointment,
        name="approve_appointment",
    ),
    # Doctor
    path("doctors/", doctor_list, name="doctor_list"),
    path("doctors/new/", doctor_create, name="doctor_create"),
    # Patient
    path("patients/", patient_list, name="patient_list"),
    path("patients/new/", patient_create, name="patient_create"),
]

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hospital.models import Doctor, Patient


class Command(BaseCommand):
    help = "Create sample users and profiles for testing the login system"

    def handle(self, *args, **options):
        # Create a sample doctor user
        doctor_user, created = User.objects.get_or_create(
            username="doctor1",
            defaults={
                "email": "doctor1@hospital.com",
                "first_name": "John",
                "last_name": "Smith",
            },
        )
        if created:
            doctor_user.set_password("password123")
            doctor_user.save()
            self.stdout.write(self.style.SUCCESS("Created doctor user: doctor1"))

        # Create doctor profile
        doctor, created = Doctor.objects.get_or_create(
            user=doctor_user,
            defaults={
                "name": "Dr. John Smith",
                "specialty": "Cardiology",
                "phone": "+1-555-0123",
                "email": "doctor1@hospital.com",
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS("Created doctor profile: Dr. John Smith")
            )

        # Create a sample patient user
        patient_user, created = User.objects.get_or_create(
            username="patient1",
            defaults={
                "email": "patient1@email.com",
                "first_name": "Jane",
                "last_name": "Doe",
            },
        )
        if created:
            patient_user.set_password("password123")
            patient_user.save()
            self.stdout.write(self.style.SUCCESS("Created patient user: patient1"))

        # Create patient profile
        patient, created = Patient.objects.get_or_create(
            user=patient_user,
            defaults={
                "name": "Jane Doe",
                "age": 35,
                "gender": "F",
                "phone": "+1-555-0456",
                "address": "123 Main St, Anytown",
                "doctor": doctor,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created patient profile: Jane Doe"))

        self.stdout.write(
            self.style.SUCCESS(
                "\nSample users created successfully!\n"
                "Doctor login: username=doctor1, password=password123\n"
                "Patient login: username=patient1, password=password123"
            )
        )

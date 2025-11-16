from django.test import TestCase, override_settings
from users.forms import CustomUserCreationForm, AdminRegistrationForm
from users.models import CustomUser

class RegistrationFormsTests(TestCase):
    def setUp(self):
        # Create an existing user to test duplicate email
        self.existing = CustomUser.objects.create_user(
            username='existing', email='existing@example.com', password='testpass'
        )

    def test_contact_number_validation_rejects_short(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'position': '',
            'contact_number': '0912345678',  # 10 digits
            'date_of_birth': '1990-01-01',
            'password1': 'ComplexPwd123!',
            'password2': 'ComplexPwd123!',
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('contact_number', form.errors)

    def test_contact_number_validation_accepts_11(self):
        data = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'position': '',
            'contact_number': '09123456789',  # 11 digits
            'date_of_birth': '1990-01-01',
            'password1': 'ComplexPwd123!',
            'password2': 'ComplexPwd123!',
        }
        form = CustomUserCreationForm(data=data)
        # form might still be invalid due to other validations (e.g., position) but contact should not be the error
        self.assertNotIn('contact_number', form.errors)

    def test_duplicate_email_gets_rejected(self):
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # duplicate
            'first_name': 'New',
            'last_name': 'User',
            'position': '',
            'contact_number': '09123456789',
            'date_of_birth': '1990-01-01',
            'password1': 'ComplexPwd123!',
            'password2': 'ComplexPwd123!',
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], "This email address is already registered.")

    def test_duplicate_email_case_insensitive(self):
        data = {
            'username': 'newuser2',
            'email': 'EXISTING@EXAMPLE.COM',  # different case
            'first_name': 'New',
            'last_name': 'User',
            'position': '',
            'contact_number': '09123456789',
            'date_of_birth': '1990-01-01',
            'password1': 'ComplexPwd123!',
            'password2': 'ComplexPwd123!',
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], "This email address is already registered.")

    @override_settings(ADMIN_REGISTRATION_KEY='test-key-123')
    def test_admin_duplicate_email_rejected(self):
        data = {
            'username': 'adminnew',
            'email': 'existing@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'position': '',
            'contact_number': '09123456789',
            'date_of_birth': '1985-05-05',
            'password1': 'ComplexPwd123!',
            'password2': 'ComplexPwd123!',
            'registration_key': 'test-key-123',
        }
        form = AdminRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], "This email address is already registered.")

    @override_settings(ADMIN_REGISTRATION_KEY='test-key-123')
    def test_admin_registration_rejects_bad_key(self):
        data = {
            'username': 'adminuser',
            'email': 'adminuser@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'position': '',
            'contact_number': '09123456789',
            'date_of_birth': '1985-05-05',
            'password1': 'ComplexPwd123!',
            'password2': 'ComplexPwd123!',
            'registration_key': 'wrong-key'
        }
        form = AdminRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('registration_key', form.errors)

    @override_settings(ADMIN_REGISTRATION_KEY='test-key-123')
    def test_admin_registration_accepts_correct_key(self):
        data = {
            'username': 'adminuser2',
            'email': 'admin2@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'position': '',
            'contact_number': '09123456789',
            'date_of_birth': '1985-05-05',
            'password1': 'ComplexPwd123!',
            'password2': 'ComplexPwd123!',
            'registration_key': 'test-key-123',
        }
        form = AdminRegistrationForm(data=data)
        # If other fields are required they may produce errors, but the registration_key should not be invalid
        self.assertNotIn('registration_key', form.errors)

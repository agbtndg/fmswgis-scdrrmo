from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import AssessmentRecord, ReportRecord, CertificateRecord, FloodRecordActivity
from users.models import CustomUser, UserLog


class ActivitySortTests(TestCase):
	def setUp(self):
		self.client = Client()
		# Create a regular user
		self.user = CustomUser.objects.create_user(username='tester', password='pass1234')

		# Create two assessments with distinct timestamps
		now = timezone.now()
		older = now - timedelta(days=1)
		newer = now

		self.assess_old = AssessmentRecord.objects.create(
			user=self.user, barangay='Old Barangay', latitude=0.0, longitude=0.0,
			flood_risk_code='LF', flood_risk_description='Low', timestamp=older
		)

		self.assess_new = AssessmentRecord.objects.create(
			user=self.user, barangay='New Barangay', latitude=0.0, longitude=0.0,
			flood_risk_code='LF', flood_risk_description='Low', timestamp=newer
		)

		# Create certificates and logs
		self.cert_old = CertificateRecord.objects.create(
			user=self.user, establishment_name='Old Cert', owner_name='Owner', location='Loc',
			barangay='A', latitude=0, longitude=0, flood_susceptibility='Low', zone_status='Safe',
			issue_date='01 Jan 2020', timestamp=older
		)
		self.cert_new = CertificateRecord.objects.create(
			user=self.user, establishment_name='New Cert', owner_name='Owner 2', location='Loc',
			barangay='B', latitude=0, longitude=0, flood_susceptibility='Low', zone_status='Safe',
			issue_date='02 Jan 2020', timestamp=newer
		)

		# Create user log entries
		self.log_old = UserLog.objects.create(user=self.user, action='login', timestamp=older)
		self.log_new = UserLog.objects.create(user=self.user, action='logout', timestamp=newer)

	def test_my_activity_oldest(self):
		# Login and request my_activity with oldest sort selection
		self.client.login(username='tester', password='pass1234')
		resp = self.client.get(reverse('my_activity') + '?sort_order=oldest')
		# Assessments should be ordered oldest first
		assessments = resp.context['assessments']
		self.assertEqual(list(assessments)[:2], [self.assess_old, self.assess_new])

		# Certificates should also be oldest first
		certs = resp.context['certificates']
		self.assertEqual(list(certs)[:2], [self.cert_old, self.cert_new])

		# Logs oldest first
		logs = resp.context['user_logs']
		self.assertEqual(list(logs)[:2], [self.log_old, self.log_new])

	def test_my_activity_recent(self):
		self.client.login(username='tester', password='pass1234')
		resp = self.client.get(reverse('my_activity') + '?sort_order=recent')
		assessments = resp.context['assessments']
		self.assertEqual(list(assessments)[:2], [self.assess_new, self.assess_old])

	def test_all_activities_oldest(self):
		# create staff
		staff = CustomUser.objects.create_user(username='staff', password='pass', is_staff=True)
		self.client.login(username='staff', password='pass')

		resp = self.client.get(reverse('all_activities') + '?sort=oldest')
		# Ensure ordering on assessments uses timestamp
		assessments = resp.context['assessments']
		if assessments.count() >= 2:
			self.assertEqual(list(assessments)[:2], [self.assess_old, self.assess_new])


from django.test import TestCase
from django.urls import reverse
from management.models import *
import datetime
from django.contrib.messages import get_messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType




class AvailableTimeTests(TestCase):
    def setUp(self):
        self.specialize_heart = Specialization.objects.create(title="قلب")
        self.specialize_ortopedia = Specialization.objects.create(title="ارتوپدی")
        self.specialize_eye = Specialization.objects.create(title="چشم")

        self.doctor_heart = Doctor.objects.create(
            first_name="علی", last_name="رضایی", specializations=self.specialize_heart,
            phone="09636365236", clinic_address="تهران", license_number="12365",
            biography="دکتر قلب مملکت", is_active=True, visit_cost=150000
            )
        self.doctor_ortopedia = Doctor.objects.create(
            first_name="مهدی", last_name="حسینی", specializations=self.specialize_ortopedia,
            phone="09644365236", clinic_address="تهران", license_number="55258",
            biography="دکتر ارتوپد مملکت", is_active=False, visit_cost=100000
            )
        self.doctor_eye = Doctor.objects.create(
            first_name="یوسف", last_name="زمانی", specializations=self.specialize_eye,
            phone="09644365214", clinic_address="تهران", license_number="14252",
            biography="دکتر چشم مملکت", is_active=True, visit_cost=100000
            )


        admin = User.objects.create(username="admin", is_staff=True)
        admin.set_password("admin")
        admin.save()
        content_type = ContentType.objects.get_for_model(AvailableTime)
        permission = Permission.objects.get(codename='delete_availabletime', content_type=content_type)
        admin.user_permissions.add(permission)
        self.admin = admin

        user_1 = User(username="Reza",first_name="رضا",last_name="حسنی",email="reza@gmail.com")
        user_1.set_password("12345")
        user_1.save()
        self.user_1 = user_1
        user_2 = User(username="Hassan",first_name="حسن",last_name="رمضانی",email="hassan@gmail.com")
        user_2.set_password("5464")
        user_2.save()
        self.user_2 = user_2

        self.patient_1 = Patient.objects.create(user=user_1, phone="09542555555",balance=200000)
        self.patient_2 = Patient.objects.create(user=user_2, phone="09534555555")

        self.time_patient1_1 = AvailableTime.objects.create(
            doctor=self.doctor_heart, patient=self.patient_1, date=datetime.date(2024,9,18),
            start_time=datetime.time(10,30), end_time=datetime.time(11,30)
        )
        self.time_patient1_2 = AvailableTime.objects.create(
            doctor=self.doctor_heart, patient=self.patient_1, date=datetime.date(2024,9,19),
            start_time=datetime.time(10,30), end_time=datetime.time(11,30)
        )
        self.time_patient2 = AvailableTime.objects.create(
            doctor=self.doctor_ortopedia, patient=self.patient_2, date=datetime.date(2024,9,25),
            start_time=datetime.time(8,30), end_time=datetime.time(10,00)
        )
        self.time_empty = AvailableTime.objects.create(
            doctor=self.doctor_eye, date=datetime.date(2024,9,20),
            start_time=datetime.time(8,30), end_time=datetime.time(10,00)
        )



#   View Tests
    def test_availabletime_ok_reservation(self):
        self.client.login(username="Reza", password="12345")

        response = self.client.post(reverse('patient_reservation', args=[self.time_empty.id]))
        self.time_empty.refresh_from_db()
        self.patient_1.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.time_empty.patient, self.patient_1)
        self.assertEqual(self.patient_1.balance, 100000) # 200000(balance) - 100000(visit_cost)


    def test_availabletime_fail_reservation(self):
        self.client.login(username="Hassan", password="5464")
        
        response = self.client.post(reverse('patient_reservation', args=[self.time_empty.id]))
        self.time_empty.refresh_from_db()
        self.patient_2.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.time_empty.patient)
        self.assertEqual(self.patient_2.balance, 0)


    def test_availabletime_view_delete_reserve_time_1(self):
        self.client.login(username="Reza", password="12345")
        response = self.client.post(reverse('patient_delete_reserve_time', args=[self.time_patient1_2.id, 1]))

        self.time_patient1_2.refresh_from_db()
        self.patient_1.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('patient_reserved_times')) 
        self.assertIsNone(self.time_patient1_2.patient)
        self.assertEqual(self.patient_1.balance, 350000)


    def test_availabletime_view_delete_reserve_time_2(self):
        self.client.login(username="Reza", password="12345")
        response = self.client.post(reverse('patient_delete_reserve_time', args=[self.time_patient1_2.id, 2]))

        self.time_patient1_2.refresh_from_db()
        self.patient_1.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('availabletime_doctor', args=[self.time_patient1_2.doctor.id]))
        self.assertIsNone(self.time_patient1_2.patient)
        self.assertEqual(self.patient_1.balance, 350000)


    def test_availabletime_view_patient(self):
        self.client.login(username="Reza", password="12345")

        doctor_heart = Doctor.objects.get(license_number="12365")
        response = self.client.get(reverse('availabletime_doctor',args=[doctor_heart.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'av_time/availabletime_doctor.html')
        self.assertContains(response, f'زمان‌های موجود دکتر')
        self.assertContains(response, f'{doctor_heart.first_name} {doctor_heart.last_name}')
        self.assertContains(response, f'حذف')
        self.assertContains(response, f'رزرو')
        self.assertNotContains(response, f'اضافه کردن زمان جدید')
        self.assertNotContains(response, f'زمانی برای نمایش وجود ندارد.')


    def test_availabletime_view_admin(self):
        self.client.login(username="admin", password="admin")

        doctor_ortopedia = Doctor.objects.get(license_number="55258")
        response = self.client.get(reverse('availabletime_doctor',args=[doctor_ortopedia.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'av_time/availabletime_doctor.html')
        self.assertContains(response, f'زمان‌های موجود دکتر')
        self.assertContains(response, f'{doctor_ortopedia.first_name} {doctor_ortopedia.last_name}')
        self.assertContains(response, f'اضافه کردن زمان جدید')
        self.assertContains(response, f'حذف')
        self.assertNotContains(response, f'رزرو')
        self.assertNotContains(response, f'زمانی برای نمایش وجود ندارد.')


    def test_availabletime_view_no_times(self):
        self.client.login(username="admin", password="admin")
        doctor_ortopedia = Doctor.objects.get(license_number="55258")
        AvailableTime.objects.get(doctor=doctor_ortopedia).delete()
        response = self.client.get(reverse('availabletime_doctor',args=[doctor_ortopedia.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'av_time/availabletime_doctor.html')
        self.assertContains(response, f'زمان‌های موجود دکتر')
        self.assertContains(response, f'{doctor_ortopedia.first_name} {doctor_ortopedia.last_name}')
        self.assertNotContains(response, f'رزرو')
        self.assertContains(response, f'اضافه کردن زمان جدید')
        self.assertContains(response, f'زمانی برای نمایش وجود ندارد.')


    def test_delete_available_time(self):
        self.client.login(username='admin', password='admin')

        time_1 = AvailableTime.objects.get(doctor__license_number="55258", patient__user__username="Hassan")
        response = self.client.post(reverse('delete_availabletime', args=[time_1.id]))

        self.assertEqual(AvailableTime.objects.filter(patient__user__username="Hassan").count(), 0)
        self.assertRedirects(response, reverse('availabletime_doctor', args=[time_1.doctor.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'نوبت خالی برای دکتر {time_1.doctor.first_name} {time_1.doctor.last_name} حذف شد.')


    def test_delete_available_time_without_permission(self):
        self.client.login(username='Reza', password='12345')

        time_1 = AvailableTime.objects.get(doctor__license_number="55258", patient__user__username="Hassan")
        response = self.client.post(reverse('delete_availabletime', args=[time_1.id]))

        self.assertEqual(response.status_code, 403)


    def test_availabletime_view_not_login(self):
        doctor_ortopedia = Doctor.objects.get(license_number="55258")
        response = self.client.get(reverse('availabletime_doctor',args=[doctor_ortopedia.id]))

        self.assertRedirects(response, f'/login/?next=/availabletime_doctor/{doctor_ortopedia.id}/')


#   Model Tests
    def test_str(self):
        time_1 = AvailableTime.objects.filter(doctor__first_name="علی",patient__user__username="Reza").first()
        time_2 = AvailableTime.objects.filter(doctor__first_name="مهدی",patient__user__username="Hassan").first()

        self.assertEqual(time_1.__str__(), "علی رضایی")
        self.assertEqual(time_1.doctor.__str__(), "علی رضایی")
        self.assertNotEqual(time_1.doctor.specializations.__str__(), "ارتوپدی")
        self.assertEqual(time_2.__str__(), "مهدی حسینی")
        self.assertEqual(time_2.doctor.__str__(), "مهدی حسینی")
        self.assertNotEqual(time_2.doctor.specializations.__str__(), "قلب")


    def test_doctor(self):
        time_1 = AvailableTime.objects.get(doctor__license_number="12365", date=datetime.date(2024,9,18))
        time_2 = AvailableTime.objects.get(doctor__license_number="55258")

        self.assertEqual(time_1.doctor.first_name,"علی")
        self.assertNotEqual(time_1.doctor.last_name,"حسنی")
        self.assertTrue(time_1.doctor.is_active)
        self.assertEqual(time_2.doctor.first_name,"مهدی")
        self.assertNotEqual(time_2.doctor.last_name,"حسنی")
        self.assertFalse(time_2.doctor.is_active)


    def test_patient(self):
        time_1 = AvailableTime.objects.get(doctor__license_number="12365", date=datetime.date(2024,9,18))
        time_2 = AvailableTime.objects.get(doctor__license_number="55258")

        self.assertEqual(time_1.patient.user.first_name,"رضا")
        self.assertNotEqual(time_1.patient.user.last_name,"رضایی")
        self.assertEqual(time_2.patient.user.first_name,"حسن")
        self.assertNotEqual(time_2.patient.user.last_name,"صادقی")


    def test_date(self):
        time_1 = AvailableTime.objects.get(doctor__license_number="12365", patient__user__username="Reza", date=datetime.date(2024,9,18))
        time_2 = AvailableTime.objects.get(doctor__license_number="55258", patient__user__username="Hassan")

        self.assertEqual(time_1.date, datetime.date(2024,9,18))
        self.assertNotEqual(time_1.date, datetime.date(2024,10,15))
        self.assertEqual(time_2.date, datetime.date(2024,9,25))
        self.assertNotEqual(time_2.date, datetime.date(2024,10,9))


    def test_times(self):
        time_1 = AvailableTime.objects.get(doctor__license_number="12365", patient__user__username="Reza", date=datetime.date(2024,9,18))
        time_2 = AvailableTime.objects.get(doctor__license_number="55258", patient__user__username="Hassan")

        self.assertEqual(time_1.start_time, datetime.time(10,30))
        self.assertNotEqual(time_1.end_time, datetime.time(10,30))
        self.assertEqual(time_2.start_time, datetime.time(8,30))
        self.assertNotEqual(time_2.end_time, datetime.time(12,30))


    def test_specialize(self):
        time_1 = AvailableTime.objects.get(doctor__license_number="12365", patient__user__username="Reza", date=datetime.date(2024,9,18))
        time_2 = AvailableTime.objects.get(doctor__license_number="55258", patient__user__username="Hassan")

        self.assertEqual(time_1.doctor.specializations.title, "قلب")
        self.assertNotEqual(time_1.doctor.specializations.title, "ارتوپدی")
        self.assertEqual(time_2.doctor.specializations.title, "ارتوپدی")
        self.assertNotEqual(time_2.doctor.specializations.title, "مامایی")


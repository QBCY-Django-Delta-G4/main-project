from django.urls import path
from management.views.av_time_view import *
from management.views.doctor_view import *
from management.views.patient_view import *
from management.views.login_view import *


urlpatterns = [
    path('create_patient/', create_patient, name='create_patient'),
    path('createdoctor/', create_doctor, name='createdoctor'),
    path('viewdoctor/', view_doctor, name='viewdoctor'),
    path('createspecialize/', create_specialize, name='createspecialize'),
    path('delete_doctor/<int:id>/', delete_doctor, name='delete_doctor'),
    path('detail_doctor/<int:id>/', detail_doctor, name='detail_doctor'),
    path('edit_doctor/<int:id>/', edit_doctor, name='edit_doctor'),
    path('availabletime_doctor/<int:id>/', availabletime_doctor, name='availabletime_doctor'),
    path('create_availabletime/<int:id>/', create_availabletime, name='create_availabletime'),
    path('edit_availabletime/<int:id>/', edit_availabletime, name='edit_availabletime'),
    path('delete_availabletime/<int:id>/', delete_availabletime, name='delete_availabletime'),
    path('patient_add_balance/', patient_add_balance, name='patient_add_balance'),
    path('patient_reservation/<int:id>/', patient_reservation, name='patient_reservation'),
    path('patient_reserved_times/', patient_reserved_times, name='patient_reserved_times'),
    path('patient_delete_reserve_time/<int:id>/<int:r>/', patient_delete_reserve_time, name='patient_delete_reserve_time'),
    path('login/', patient_login, name="login" ),
    path('logout/', patient_logout, name="logout" ),
    path('', home, name="home"),
    path('forgot_password/', forgot_password_view, name="forgot_password"),
    path('reset_password/', reset_password_view, name="reset_password"),
    path('patient_profile', patient_profile, name='patient_profile'),
    path('delete-comment/<int:doctor_id>/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('edit_patient_profile', edit_patient_profile,name='edit_patient_profile'),
    path('change_password/', change_password, name='change_password'),
    

]

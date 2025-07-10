from django.urls import path
from api.views import auth, students, students_register, leads, trainers, batch, counselors, study_material

urlpatterns = [
    path('show-languages', students_register.show_languages, name="show_languages"),
    path('show-level-and-hour', students_register.show_levelandhour, name="show_levelandhour"),
    path('otp-sender', students_register.otp_sender, name='otp_sender'),
    path('student-account-verify', students_register.student_account_verify, name='student_account_verify'),
    path('student-details-choices', students_register.student_details, name='student-details-choices'),
    path('student-counselors', students_register.student_counselor, name='student-counselors'),
    
    
    path("get-token", auth.get_token, name="get-token"),
    path('login', auth.user_login, name='login'),
    path('reset-password-link', auth.reset_password_link, name='reset_password_link'),
    path('change-password', auth.change_password, name='change_password'),
    path('create-new-password', auth.create_new_password, name='create-new-password'),
    path('check-password-token', auth.check_password_token, name='check-password-token'),
    
    
    
    # Leads
    path('get-all-leads', leads.get_all_leads, name='get-all-leads'),
    path('get-leads-status', leads.get_leads_status, name='get-leads-status'),
    path('lead-profile', leads.lead_profile, name='lead-profile'),
    path('import-lead', leads.import_lead, name='import-lead'),
    path('create-single-lead', leads.create_single_lead, name='create-single-lead'),
    path('change-lead-status', leads.change_lead_status, name='change-lead-status'),
    path('update-lead-details', leads.update_lead_details, name='update-lead-details'),
    
    
    # Students
    path('get-all-student-details', students.get_all_student_details, name='get-all-student-details'),
    path('student-details', students.student_details, name='student-details'),
    path('student-profile', students.student_profile, name='student-profile'),
    path('student-status-update', students.student_status_update, name='student-status-update'),
    
    # Trainers
    path('create-trainer', trainers.create_trainer, name='create-trainer'),
    path('get-trainers', trainers.get_trainers, name='get-trainers'),
    path('trainer-profile', trainers.trainer_profile, name='trainer-profile'),
    
    
    
    # Batches
    path('get-students-and-trainers', batch.get_students_and_trainers, name='get-students-and-trainers'),
    path('get-batch', batch.get_batch, name='get-batch'),
    path('create-batch', batch.create_batch, name='create-batch'),
    path('batch-profile', batch.batch_profile, name='batch-profile'),
    path('batch-profile-change-trainer', batch.batch_profile_change_trainer, name='batch-profile-change-trainer'),
    path('batch-profile-remove-student', batch.batch_profile_remove_student, name='batch-profile-remove-student'),
    path('batch-profile-add-student', batch.batch_profile_add_student, name='batch-profile-add-student'),
    path('batch-google-meet-link-update', batch.batch_google_meet_link_update, name='batch-google-meet-link-update'),
    path('batch-complited-update', batch.batch_complited_update, name='batch-complited-update'),
    path('start-class', batch.start_class, name='start-class'),
    path('end-class', batch.end_class, name='end-class'),
    
    # Counselors
    path('all-counselors', counselors.all_counselors, name='all-counselors'),
    path('create-single-counselors', counselors.create_counselors, name='create-single-counselors'),
    
    # StudyMaterial
    path('get-study-material', study_material.get_study_material, name='get-study-material'),
    path('create-study-material', study_material.create_study_material, name='create-study-material'),
]
from django.urls import path
from api.views import auth, languages

urlpatterns = [
    path('show_languages', languages.show_languages, name="show_languages"),
    path('show_levelandhour', languages.show_levelandhour, name="show_levelandhour"),
    path('student_register', auth.students_register, name='student_register'),
    path('student_account_verify', auth.student_account_verify, name='student_account_verify'),
    path('student_account_verify', auth.student_account_verify, name='student_account_verify'),
    
    
    path('login', auth.user_login, name='login'),
]
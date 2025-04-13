from django.contrib import admin
from .models import CustomUser, OTP, UserToken, Calendar, Message, ChatRoom, Language, LevelsAndHour, StudentDetails

admin.site.register(CustomUser)
admin.site.register(OTP)
admin.site.register(UserToken)
admin.site.register(Calendar)
admin.site.register(Message)
admin.site.register(ChatRoom)
admin.site.register(Language)
admin.site.register(LevelsAndHour)
admin.site.register(StudentDetails)

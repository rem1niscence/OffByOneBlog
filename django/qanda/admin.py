from django.contrib import admin
from qanda.models import Answer, Profile, Question, Tag

# Register your models here.
admin.site.register(Question)
admin.site.register(Tag)
admin.site.register(Answer)
admin.site.register(Profile)

from django.contrib import admin
from qanda.models import Question, Tag, Answer


# Register your models here.
admin.site.register(Question)
admin.site.register(Tag)
admin.site.register(Answer)

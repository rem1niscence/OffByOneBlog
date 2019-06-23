from django.contrib import admin
from qanda.models import Question, Tag, QuestionVote


# Register your models here.
admin.site.register(Question)
admin.site.register(Tag)
admin.site.register(QuestionVote)

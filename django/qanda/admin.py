from django.contrib import admin
from qanda.models import (Answer, Profile, Question,
                          Tag, QuestionVote, QuestionSubscription)

# Register your models here.
admin.site.register(Question)
admin.site.register(Tag)
admin.site.register(Answer)
admin.site.register(Profile)
admin.site.register(QuestionVote)
admin.site.register(QuestionSubscription)

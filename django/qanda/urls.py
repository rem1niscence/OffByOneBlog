from django.urls import path
from qanda import views

app_name = 'qanda'
urlpatterns = [
    path('ask/', views.CreateQuestion.as_view(), name='ask-question'),
    path('question/<int:question_id>/vote/',
         views.QuestionVoteCreate.as_view(), name='question-vote-create'),
    path('question/<int:pk>/<str:title>/',
         views.QuestionDetail.as_view(), name='question-detail'),
    path('question/<int:question_id>/vote/<int:pk>/',
         views.QuestionVoteUpdate.as_view(), name='question-vote-update'),
]

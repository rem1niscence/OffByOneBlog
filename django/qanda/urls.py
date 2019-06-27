from django.urls import path
from qanda import views

app_name = 'qanda'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('ask/', views.CreateQuestion.as_view(), name='ask-question'),
    path('question/<int:question_id>/vote/',
         views.QuestionVoteCreate.as_view(), name='question-vote-create'),
    path('question/<int:question_id>/vote/<int:pk>/',
         views.QuestionVoteUpdate.as_view(), name='question-vote-update'),
    path('question/<int:question_id>/answer/',
         views.AnswerCreate.as_view(), name='answer-create'),
    path('question/<int:pk>/<str:title>/',
         views.QuestionDetail.as_view(), name='question-detail'),
    path('answer/<int:answer_id>/vote/',
         views.AnswerVoteCreate.as_view(), name='answer-vote-create'),
    path('answer/<int:answer_id>/vote/<int:pk>/',
         views.AnswerVoteUpdate.as_view(), name='answer-vote-update'),
    path('answer/<int:pk>/', views.UpdateAnswerAcceptanceView.as_view(),
         name='update-accepted-answer')
]

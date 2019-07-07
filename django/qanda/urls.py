from django.urls import path, re_path
from qanda import views

app_name = 'qanda'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('ask/', views.CreateQuestion.as_view(), name='ask_question'),
    path('question/<int:question_id>/vote/',
         views.QuestionVoteCreate.as_view(), name='question_vote_create'),
    path('question/<int:question_id>/vote/<int:pk>/',
         views.QuestionVoteUpdate.as_view(), name='question_vote_update'),
    path('question/<int:question_id>/answer/',
         views.AnswerCreate.as_view(), name='answer-create'),
    path('question/<int:pk>/<str:title>/',
         views.QuestionDetail.as_view(), name='question_detail'),
    path('answer/<int:answer_id>/vote/',
         views.AnswerVoteCreate.as_view(), name='answer_vote_create'),
    path('answer/<int:answer_id>/vote/<int:pk>/',
         views.AnswerVoteUpdate.as_view(), name='answer_vote_update'),
    path('answer/<int:pk>/', views.UpdateAnswerAcceptanceView.as_view(),
         name='update_accepted_answer'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            views.activate, name='activate'),
    path('users/<str:username>/',
         views.UserDetail.as_view(), name='user-detail'),
    path('q/search', views.SearchView.as_view(), name='question_search'),
]

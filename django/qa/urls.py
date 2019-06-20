from django.urls import path
from qa import views

app_name = 'qa'
urlpatterns = [
    path('', views.TestView.as_view(), name='test'),
]

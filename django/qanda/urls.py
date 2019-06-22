from django.urls import path
from qanda import views

app_name = 'qanda'
urlpatterns = [
    path('ask', views.TestView.as_view(), name='test'),
]

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from qanda.forms import CustomAuhthenticationForm
from qanda.views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',
         views.LoginView.as_view(form_class=CustomAuhthenticationForm),
         name='login'),
    path('register/', SignUpView.as_view(), name='register'),
    path('', include('qanda.urls')),
]

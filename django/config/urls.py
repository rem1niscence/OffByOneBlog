from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from qanda.forms import CustomAuhthenticationForm
from qanda.views import SignUpView
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(form_class=CustomAuhthenticationForm),
         name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register/', SignUpView.as_view(), name='register'),
    path('', include('qanda.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns

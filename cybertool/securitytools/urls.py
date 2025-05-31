from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('port-scan/', login_required(views.port_scan), name='port_scan'),
    path('password-strength/', login_required(views.password_strength), name='password_strength'),
    path('hash-generator/', login_required(views.hash_generator), name='hash_generator'),
    path('url-scanner/', login_required(views.url_scanner), name='url_scanner'),
    path('scan-history/', login_required(views.scan_history), name='scan_history'),
]
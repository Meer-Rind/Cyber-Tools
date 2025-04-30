from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from securitytools.views import RegisterView, dashboard  # Import dashboard view directly

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='home'),  # This will redirect properly based on auth status
    path('securitytools/', include('securitytools.urls')),
    
    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='securitytools/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # Password reset URLs (optional)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
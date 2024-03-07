from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('api/', include('base.api.urls')),


    path('password_reset/', PasswordResetView.as_view(template_name='base/password_reset_form.html'), name='password_reset'),

    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='base/password_reset_done.html'), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='base/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', 
    
    PasswordResetCompleteView.as_view(template_name='base/password_reset_complete.html'), name='password_reset_complete'),

    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
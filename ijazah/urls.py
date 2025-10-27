from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [   
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('app/', include('app.urls')),
]

# handler404 = 'sseapp.views.handler404'
# handler500 = 'sseapp.views.handler500'
# handler403 = 'sseapp.views.handler403'
# handler400 = 'sseapp.views.handler400'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
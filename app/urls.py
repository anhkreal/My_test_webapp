from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.get_home, name = "home"),
    path('login/', views.dangNhap, name = "login"),
    path('logout/', views.logoutPage, name = "logout"),
    path('register/', views.dangKi, name = "register"),
    path('get-timeline-data/', views.get_timeline_data, name='get_timeline_data'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('snapshot/', views.show_snapshot, name = "snapshot"),
]

if settings.DEBUG:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
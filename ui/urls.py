from django.urls import path, include

from ui import views

urlpatterns = [
    path("", views.index),
    path('accounts/', include('django.contrib.auth.urls')),
]

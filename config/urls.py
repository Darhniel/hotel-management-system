"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import HotelTokenView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/auth/login/", HotelTokenView.as_view()),
    path("api/v1/auth/refresh/", TokenRefreshView.as_view()),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/rooms/", include("apps.rooms.urls")),
    path("api/v1/bookings/", include("apps.bookings.urls")),
    path("api/v1/dashboard/", include("apps.dashboard.urls")),
    path("api/v1/invites/", include("apps.invites.urls")),
    path("api/v1/", include("apps.hotels.urls")),
]

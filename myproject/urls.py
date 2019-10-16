from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from api.views import CustomView

urlpatterns = [
		path('admin/', admin.site.urls),
		path('', include('api.urls')),
	]

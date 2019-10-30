from django.conf.urls import url
from rest_framework import routers
from api.views import CustomView
from . import views

router = routers.DefaultRouter()

urlpatterns = [
    url('', CustomView.as_view()),
]

urlpatterns += router.urls

from django.urls import include, path
from rest_framework import routers
from quickstart import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"file-process", views.FileProcessViewSet, basename="file_process")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/navigation/", views.navigation),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

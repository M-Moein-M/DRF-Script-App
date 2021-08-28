from rest_framework.routers import DefaultRouter
from scripts.views import ScriptViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'scripts', ScriptViewSet, basename='scripts')

urlpatterns = [
    path('', include(router.urls)),
]

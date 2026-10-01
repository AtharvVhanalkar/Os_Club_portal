from rest_framework.routers import DefaultRouter

from .views import EventViewSet

router = DefaultRouter()
router.register("sessions", EventViewSet, basename="session")

urlpatterns = router.urls

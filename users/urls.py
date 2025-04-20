from rest_framework.routers import SimpleRouter
from .views import UserViewSet

router = SimpleRouter()
router.register(r"", UserViewSet)

urlpatterns = router.urls

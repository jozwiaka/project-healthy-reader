from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet, QuoteViewSet, TagViewSet

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")
router.register(r"authors", AuthorViewSet, basename="author")
router.register(r"quotes", QuoteViewSet, basename="quote")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = router.urls

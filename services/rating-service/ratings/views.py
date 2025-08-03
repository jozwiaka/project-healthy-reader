from rest_framework import viewsets
from .models import Rating
from .serializers import RatingSerializer

class RatingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ratings to be viewed.
    """
    queryset = Rating.objects.all().order_by("id")
    serializer_class = RatingSerializer

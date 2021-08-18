from rest_framework import generics
from scripts.serializers import ScriptSerializer
from snippets.models import Script


class ScriptList(generics.ListCreateAPIView):
    """Listing and creating script objects"""

    queryset = Script.objects.all().order_by('id')
    serializer_class = ScriptSerializer
    pagination_class = None

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(owner=self.request.user)

from rest_framework import generics
from rest_framework import mixins
from scripts.serializers import ScriptSerializer
from snippets.models import Script


class ScriptList(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 generics.GenericAPIView):
    """Listing and creating script objects"""

    queryset = Script.objects.all().order_by('id')
    serializer_class = ScriptSerializer
    pagination_class = None

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(owner=self.request.user)

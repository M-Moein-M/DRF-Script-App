from rest_framework import generics
from rest_framework import mixins
from scripts.serializers import ScriptSerializer, ScriptDetailSerializer
from snippets.models import Script


class ScriptList(generics.ListCreateAPIView):
    """Listing and creating script objects"""

    queryset = Script.objects.all().order_by('id')
    serializer_class = ScriptSerializer
    pagination_class = None

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(owner=self.request.user)


class ScriptDetail(mixins.UpdateModelMixin,
                   generics.RetrieveDestroyAPIView,
                   generics.GenericAPIView):
    """Handling Script details view(method PUT not allowed)"""

    queryset = Script.objects.all()
    serializer_class = ScriptSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ScriptDetailSerializer
        else:
            return ScriptSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

from rest_framework import viewsets
from scripts.serializers import ScriptSerializer, ScriptDetailSerializer
from snippets.models import Script

from rest_framework import permissions
from snippets.permissions import IsOwnerOrReadOnly


class ScriptViewSet(viewsets.ModelViewSet):
    queryset = Script.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
    pagination_class = None

    def get_serializer_class(self):
        if self.detail and self.request.method == 'GET':
            return ScriptDetailSerializer
        else:
            return ScriptSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(owner=self.request.user)

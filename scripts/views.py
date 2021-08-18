from rest_framework import generics
from scripts.serializers import ScriptSerializer
from snippets.models import Script
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class ScriptList(generics.ListCreateAPIView):
    """Listing and creating script objects"""

    queryset = Script.objects.all().order_by('id')
    serializer_class = ScriptSerializer
    pagination_class = None

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(owner=self.request.user)


class ScriptDetail(APIView):
    """Handling Script details view"""

    def get_object(self, pk):
        return get_object_or_404(Script, id=pk)

    def get(self, request, pk):
        script = self.get_object(pk)
        serializer = ScriptSerializer(script)
        return Response(status=status.HTTP_200_OK,
                        data=serializer.data)

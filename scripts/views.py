from rest_framework.views import APIView
from scripts.serializers import ScriptSerializer
from rest_framework.response import Response
from rest_framework import status


class ScriptList(APIView):
    def get(self, request):
        pass

    def post(self, request):
        serializer = ScriptSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(owner=request.user)
            return Response(data=ScriptSerializer(instance).data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

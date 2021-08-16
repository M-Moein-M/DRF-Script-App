from rest_framework.views import APIView
from scripts.serializers import ScriptSerializer
from rest_framework.response import Response
from rest_framework import status
from snippets.models import Script


class ScriptList(APIView):
    def get(self, request):
        script_list = Script.objects.all().order_by('id')
        serializer = ScriptSerializer(script_list, many=True)
        return Response(data=serializer.data)

    def post(self, request):
        serializer = ScriptSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(owner=request.user)
            return Response(data=ScriptSerializer(instance).data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

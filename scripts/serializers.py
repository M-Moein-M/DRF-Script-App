from rest_framework import serializers
from snippets.models import Script


class ScriptSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    owner = serializers.ReadOnlyField(source='owner.username')
    snippets = serializers.CharField(max_length=1023, default='')
    id = serializers.ReadOnlyField(required=False)

    def create(self, validated_data):
        instance = Script.objects.create(**validated_data)
        return instance

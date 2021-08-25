from rest_framework import serializers
from snippets.models import Script, Snippet


def validate_snippets_field(value):
    """snippets field must be a comma separated string of existing snippet id"""
    try:
        id_set = {int(s_id.strip())
                  for s_id in value.split(',') if s_id.strip()}
        existing_ids = set(Snippet.objects.values_list('id', flat=True))
        common_ids = id_set & existing_ids
        if common_ids == id_set:
            return
        else:
            msg = 'Invalid snippets id.'
            raise serializers.ValidationError(msg)
    except ValueError:
        msg = 'Cannot convert id to int.'
        raise serializers.ValidationError(msg)


class ScriptSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    owner = serializers.ReadOnlyField(source='owner.username')
    snippets = serializers.CharField(max_length=1023,
                                     default='',
                                     validators=[validate_snippets_field])
    id = serializers.ReadOnlyField(required=False)

    def create(self, validated_data):
        instance = Script.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.snippets = validated_data.get('snippets', instance.snippets)
        instance.save()
        return instance

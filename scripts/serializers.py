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


class ScriptDetailSerializer(ScriptSerializer):
    """Handle representation of script objects with snippets code included"""

    def expand_snippets(self, snippets):
        id_list = [int(s_id.strip())
                   for s_id in snippets.split(',') if s_id.strip()]
        snippets_objects = Snippet.objects.filter(id__in=id_list)
        ret = {snippet_id: snippets_objects.get(id=snippet_id).code
               for snippet_id in id_list}
        return ret

    def to_representation(self, instance):
        super_serializer = ScriptSerializer(instance)
        ret = dict(super_serializer.data)
        if super_serializer.data['snippets']:
            ret.update({
                'snippets_expanded':
                    self.expand_snippets(super_serializer.data['snippets'])
            })

        return ret

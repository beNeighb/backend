from rest_framework import serializers
from apps.users.models import Profile


class RequirableBooleanField(serializers.BooleanField):
    """
    Making BooleanField respect required=True.
    """

    default_empty_html = serializers.empty


class ProfileSerializer(serializers.ModelSerializer):
    age_above_18 = RequirableBooleanField(required=True)
    agreed_with_conditions = RequirableBooleanField(required=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'name',
            'age_above_18',
            'agreed_with_conditions',
            'gender',
            'speaking_languages',
            'services',
        ]

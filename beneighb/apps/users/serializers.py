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
            'city',
        ]


class ShortProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id',
            'name',
            'speaking_languages',
            'services',
        ]


class ProfileWithFcmTokenSerializer(serializers.ModelSerializer):
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
            'fcm_token',
        ]

    def validate(self, data):
        if 'fcm_token' not in data:
            raise serializers.ValidationError(
                {'fcm_token': 'This field is required.'}
            )

        fcm_token = data['fcm_token']
        if fcm_token in ['', None]:
            raise serializers.ValidationError(
                {'fcm_token': 'This field is required.'}
            )
        return data

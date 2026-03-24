from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'mobile', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            mobile=validated_data['mobile'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(mobile=data['mobile'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid mobile or password")

        if not user.check_password(data['password']):
            raise serializers.ValidationError("Invalid mobile or password")

        return user
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import ClientProfile, CollecteurProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name", "phone_number", "role")
        read_only_fields = ("id",)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password", "first_name", "last_name", "phone_number", "role")
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CollecteurProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CollecteurProfile
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = "__all__"
        read_only_fields = ("id", "created_at")


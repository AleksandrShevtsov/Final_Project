from rest_framework import serializers
from users.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'last_login',
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'is_landlord', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RegisterUserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password', 're_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        # Валидация полей
        if not re.match('^[a-zA-Z0-9_]*$', data.get('username')):
            raise serializers.ValidationError("Username must be alphanumeric or include _")
        if not re.match('^[a-zA-Z]*$', data.get('first_name')):
            raise serializers.ValidationError("First name must contain only alphabet symbols")
        if not re.match('^[a-zA-Z]*$', data.get('last_name')):
            raise serializers.ValidationError("Last name must contain only alphabet symbols")

        if data.get('password') != data.get('re_password'):
            raise serializers.ValidationError("Passwords do not match")

        try:
            validate_password(data.get("password"))
        except ValidationError as err:
            raise serializers.ValidationError({"password": err.messages})

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('re_password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user
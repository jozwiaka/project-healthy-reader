from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'location', 'age']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'location': {'required': False, 'allow_null': True, 'allow_blank': True},
            'age': {'required': False, 'allow_null': True},
        }

    # serializer.save() -> (automatically run) serializer.create()
    def create(self, validated_data):
        password = validated_data.pop('password')
        
        # without unpacking
        # user = User.objects.create(username=validated_data["username"], email=validated_data["email"])
        
        # with unpacking (**)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
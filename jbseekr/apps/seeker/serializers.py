from rest_framework import serializers
from .models import (Company, Position, Opinion)

class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        #fields = ('pk', 'name', 'email', 'document', 'phone', 'registrationDate')

class PositionQuerySerializer(serializers.Serializer):
    role = serializers.CharField(default="Python", required=False)
    location = serializers.CharField(default="Madrid", required=False)
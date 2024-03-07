# our serializers are gonna be classes that take a certain model or object and turn it to a json object or js object, then we can return it in our views

from rest_framework.serializers import ModelSerializer
from base.models import Room

class RoomSerializer(ModelSerializer):
     class Meta:
          model = Room
          fields = '__all__'
from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer

@api_view(['GET', 'PUT', 'POST'])
def getRoutes(reqeuest):
     routes = [
          'GET /api',
          'GET /api/rooms', # gives a json array of all rooms in 0ur database
          'GET /api/rooms/:id' # get a specific room
     ]
     return Response(routes) # safe means we can  use more than python dictionary inside this response.

@api_view(['GET'])
def getRooms(request):
     rooms = Room.objects.all()
     serializer = RoomSerializer(rooms, many=True) # many means are there going to be multiple objects that we are going to serialize or just one. in this case many = True
     return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
     room = Room.objects.get(id=pk)
     serializer = RoomSerializer(room, many=False) # many means are there going to be multiple objects that we are going to serialize or just one. in this case many = False. so this will return a single object
     return Response(serializer.data)
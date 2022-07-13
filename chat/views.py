from django.db.models.query_utils import Q
from chat.serializers import ChatMessageSerializer, ChatRoomSerializer,ChatRoomWithMembersSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from userdetails.models import UserDetail
import socketio
from .models import ChatMessage, ChatRoom, ChatMember

sio = socketio.Server(async_mode='eventlet',  cors_allowed_origins="*", logger=True, engineio_logger=True)
ids = {}

@sio.event
def connect(sid, environ):
      user_token = environ.get('HTTP_AUTHORIZATION')
      if user_token is None:
            return False
      else:
            try:
                  user_id = Token.objects.get(key=user_token).user_id
                  ids[sid] = user_id
            except:
                  return False
      if ids[sid]:
            return True
      else:
            return False

@sio.event
def get_rooms(sid, data):
      user_id = data['user_id']
      if ids[sid]:
            try:
                  user = UserDetail.objects.get(id=user_id)
                  start_index = data['start_index']
                  limit = data['limit']
                  search = data['search']
                  if user.user_role.code=="ADM":
                        rooms = ChatRoom.objects.filter(Q(with_admin=True)).filter(
                              Q(room_members__user__user__first_name__icontains = search) | 
                              Q(room_members__user__user__last_name__icontains = search)).distinct(
                                    ).order_by('-last_message_date')[start_index:limit+start_index]
                  else:
                        rooms = ChatRoom.objects.filter(Q(room_members__user_id=user_id)).filter(
                              Q(room_members__user__user__first_name__icontains = search) | 
                              Q(room_members__user__user__last_name__icontains = search)
                              ).distinct().order_by('-last_message_date')[start_index:limit+start_index]
                  sio.emit('rooms', ChatRoomWithMembersSerializer(rooms, many=True,context = {"user_id":user_id}).data,to=sid)
            except:
                  return False
      else:
            return False



@sio.event
def disconnect(sid):
      if sid in ids:
            del ids[sid]

@sio.event
def get_room_messages(sid,data):
    start_index = data['start_index']
    messages = ChatMessage.objects.filter(room_id=data['room_id']).order_by('-id')
    for unseen_message in messages.filter(is_seen=False).exclude(sender_id=data['user_id']):
        unseen_message.is_seen=True
        unseen_message.save()
    sio.emit('messages', ChatMessageSerializer(messages[start_index:start_index+12],many=True).data,to=sid)

@sio.event
def send_message_to_room(sid, message):
      text = message['message']
      room_id = message['room']
      if message['replier_is_admin'] == "true" or message['replier_is_admin']==1 or message['replier_is_admin']=="1":
            replier_is_admin = True
      else:
            replier_is_admin = False
      file_url = message['file_url']
      file_type = message['file_type']
      created_message = ChatMessage(replier_is_admin=replier_is_admin,
                  room_id =int(room_id),
                  sender_id =message['sender'],
                  text =text,
                  is_seen=False,
                  file_url =file_url,
                  file_type =file_type)
      try:
            created_message.parent_message_id = message['parent_message']
      except:
            pass
      created_message.save()
      values = list(ids.values())
      keys = list(ids.keys())
      for room_member in ChatMember.objects.filter(room_id=room_id):
            for index,user_id in enumerate(values):
                  if user_id == room_member.user.user_id:
                        user_sid = keys[index]
                        sio.emit('receive',
                              {'message': ChatMessageSerializer(created_message).data},
                              to=user_sid)

@sio.event
def remove_message_from_room(sid, message):
      room_id = message['room']
      messages = []
      for message_id in message['messages']:
            mess = ChatMessage.objects.get(id=message_id)
            mess.is_deleted = True
            mess.save()
            messages.append(mess)
      values = list(ids.values())
      keys = list(ids.keys())
      for room_member in ChatMember.objects.filter(room_id=room_id):
            for index,user_id in enumerate(values):
                  if user_id == room_member.user.user_id:
                        user_sid = keys[index]
                        sio.emit('deleted',
                              {'message': ChatMessageSerializer(messages,many=True).data},
                              to=user_sid)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_room_for_admin(request,pk):
      try:
            existing_room = ChatRoom.objects.get(room_members__user_id=pk, with_admin=True)
            return Response(ChatRoomSerializer(existing_room).data,status=200)
      except:
            room = ChatRoom(with_admin=True)
            room.save()
            ChatMember(user_id=pk,room=room).save()
            for admin in UserDetail.objects.filter(user_role__code="ADM"):
                  ChatMember(user_id=admin.id,room=room).save()
            return Response(ChatRoomSerializer(room).data,status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_room_for_user(request):
      user_id = request.data['user_id']
      is_with_admin = request.data['is_with_admin']
      if is_with_admin:
            
            try:
                  existing_room = ChatRoom.objects.get(room_members__user__user_id= request.user.user_details.id, 
                                                            with_admin=True)
                  return Response(ChatRoomSerializer(existing_room).data,status=200)
            except:
                  room = ChatRoom(with_admin=True)
                  room.save()

                  ChatMember(user_id= request.user.user_details.id,room=room).save()
                  for admin in UserDetail.objects.filter(user_role__code="ADM"):
                        ChatMember(user_id=admin.user_id,room=room).save()
                  return Response(ChatRoomSerializer(room).data,status=200)
      else:
            room = ChatRoom.objects.filter(room_members__user_id= request.user.user_details.id).filter(
                                                    room_members__user_id=user_id).filter(
                                                        with_admin=False)
            if len(room)>0:
                for r in room[0:1]:
                    return Response(ChatRoomSerializer(r).data,status=200)
            else:
                  new_room = ChatRoom(with_admin=False)
                  new_room.save()
                  ChatMember(user_id= request.user.user_details.id,room=new_room).save()
                  ChatMember(user_id=user_id,room=new_room).save()
                  return Response(ChatRoomSerializer(new_room).data,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unseen_message_count_user(request):
      messages = ChatMessage.objects.filter(room__room_members__user_id = request.user.user_details.id).filter(
            is_seen=False).exclude(sender_id= request.user.user_details.id)
      counts = [room.room for room in messages]
      count = set(counts)
      return Response({"unseen_message_room_count":len(count)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_message_seen(request,pk):
      try:
            message = ChatMessage.objects.get(id=pk)
            message.is_seen=True
            message.save()     
            return Response({"message":"OK"},status=200)
      except:
            return Response({"message":"Something went wrong"},status=400)

@api_view(['POST'])
def test(request):
      user_id = 276
      user = UserDetail.objects.get(user_id=user_id)
      start_index = request.data['start_index']
      limit = request.data['limit']
      search = request.data['search']

      rooms = ChatRoom.objects.filter(Q(room_members__user_id=user_id)).filter(
            Q(room_members__user__user__first_name__icontains = search) | 
            Q(room_members__user__user__last_name__icontains = search)
            ).order_by('-last_message_date')[start_index:limit+start_index]
      return Response(ChatRoomWithMembersSerializer(rooms, many=True,
                                                    context = {"user_id":user_id}).data)


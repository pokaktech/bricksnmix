# import json
# from channels.generic.websocket import WebsocketConsumer
# from .models import *
# from asgiref.sync import async_to_sync
# import time
# from datetime import datetime
# import pytz



# connected_clients_ip = set()
# configured_clients = set()
# conf_node_client_mapping = {}
# new_node_client_mapping = {}
# zoo =set()




# class ConnectionConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_group_name = 'test'
        
#         print(f"Client {self.channel_name} is attempting to connect.")

#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#         self.accept()
#         self.send(text_data=json.dumps({"message": "success"}))
#         zoo.add(self)
#         # connected_clients_ip.add(self)
#     def disconnect(self, code):
#         global conf_node_client_mapping # Access the global variable
#         global new_node_client_mapping
#         # ... Rest of your code
#         if id(self) in conf_node_client_mapping:
#             del conf_node_client_mapping[id(self)]
#         try:
#             connected_clients_ip.remove(self)
#             del new_node_client_mapping[id(self)]
#         except:
#             pass
#         print(id(self), "Disconnected...")
#         try:
#             configured_clients.remove(id(self))
#         except:
#             print("No Configured Clients...")
#         return super().disconnect(code)

#     def receive(self, text_data):
#         global conf_node_client_mapping
#         global new_node_client_mapping
#         try:
#             text_data_json = json.loads(text_data)
#             print(text_data_json)
#             command = text_data_json.get('command', None)
#             print("command:", command)
#             try:
#                 node_id =text_data_json.get('node_id', None)
#                 node_configured_to = text_data_json.get('info', None).get('configured_to', None)
#                 if command == "handshake" and node_configured_to == "":
#                     connected_clients_ip.add(self)
#                     if id(self) not in new_node_client_mapping:
#                         new_node_client_mapping[id(self)] = [node_id]
#                     else:
#                         new_node_client_mapping[id(self)].append(node_id)
#                     # self.send(text_data=json.dumps({'command': "handshake_response", 'gateway_id': gateway_serial}))
#                     # conf_node_client_mapping[node_id] = id(self)
#                     # print("Handshake with node success...")
#                 elif command == "config" and node_configured_to == gateway_serial:
#                     configured_clients.add(id(self))
#                     if id(self) not in conf_node_client_mapping:
#                         conf_node_client_mapping[id(self)] = [node_id]
#                     else:
#                         conf_node_client_mapping[id(self)].append(node_id)
#                     node_name = text_data_json.get('info', None).get('name')
#                     node_fw_version = text_data_json.get('info', None).get('fw_version')
#                     node_type = text_data_json.get('info', None).get('type')
#                     node_serial_num = text_data_json.get('info', None).get('serial_num')
#                     node_model = text_data_json.get('info', None).get('model')
#                     if node_configured_to == gateway_serial:
#                         try:
#                             node = Node.objects.get(node_id=node_id)
#                             print("Node already exists")
#                         except Node.DoesNotExist:
#                             desired_time_zone = 'Asia/Kolkata'
#                             local_timezone = pytz.timezone(desired_time_zone)
#                             current_date_time = datetime.now(local_timezone)
#                             formatted_date_time = current_date_time.strftime("%d-%m-%Y %H:%M:%S")
#                             gateway = Gateway.objects.get(gateway_id=gateway_serial)
#                             gateway.last_config = formatted_date_time
#                             gateway.save()
#                             node = Node.objects.create(node_id=node_id, gateway=gateway)
#                             print("New Node added.")
      
#                             #Adding Node Info
#                             NodeInfo.objects.create(node=node, name=node_name, fw_version=node_fw_version, type=node_type,      serial_num=node_serial_num, model=node_model)
#                             print("New node_info added.")
      
#                         for dev in text_data_json.get('devices', None):
#                             try:
#                                 device = Device.objects.get(device_id=dev.get('device_id'))
#                                 device.value = dev.get('value')
#                                 print("Device already exists")
#                             except Device.DoesNotExist:
#                                 Device.objects.create(node=node, name=dev.get('name'), device_id=dev.get('device_id'), type=dev.get     ('type'), ui_type=dev.get('ui_type'))
#                                 print("New device added.")

#             except:
#                 try:
#                     app_id = text_data_json.get('app_id', None)
#                 except:
#                     node_id =text_data_json.get('node_id', None)
#                 if command == 'state' and node_id != None: # for storing the values
#                     devices_data = text_data_json.get('devices', [])
#                     print("-------Recieved Response from node------------", command)
                    
#                     try:
#                         node = Node.objects.get(node_id=node_id)  # Get the specific node
#                         devices_for_node = Device.objects.filter(node=node)  # Get devices associated with the node
                        
#                         for device_data in devices_data:
#                             device_id = device_data.get('device_id')
#                             value = device_data.get('value')
#                             name = device_data.get('name')
                
#                             # Find the device associated with the node using its device_id
#                             device = devices_for_node.filter(device_id=device_id).first()
                            
#                             if device:
#                                 device.value = value
#                                 device.name = name
#                                 device.save()
#                         gateways = Gateway.objects.all()

#                         config_data = []
#                         for gateway in gateways:
#                             gateway_info = {
#                                 "command": "app_state",
#                                 "gateway_id": gateway.gateway_id,
#                                 "last_config": gateway.last_config,
#                                 "nodes": []
#                             }

#                             nodes = Node.objects.filter(gateway=gateway)
#                             for node in nodes:
#                                 node_data = {
#                                     "node_id": node.node_id,
#                                     "devices": []
#                                 }

#                                 devices = Device.objects.filter(node=node)
#                                 for device in devices:
#                                     device_data = {
#                                         "name": device.name,
#                                         "device_id": device.device_id,
#                                         "value": device.value,
#                                     }
#                                     node_data["devices"].append(device_data)

#                                 gateway_info["nodes"].append(node_data)

#                             config_data.append(gateway_info)
#                         print("Job", config_data)
#                         async_to_sync(self.channel_layer.group_send)(
#                         self.room_group_name,
#                         {
#                             'type':'chat_message',
#                             'message':config_data
#                         }
#                     )
#                     except Node.DoesNotExist:
#                         print("Node does not exist")
#                         pass
#                 elif command == "update": # for broadcasting the message
                    
#                     nodes = text_data_json.get('nodes', [])
#                     if nodes:
#                         node_id = nodes[0].get('node_id', None)
#                     else:
#                         print("No nodes found in the JSON.")
#                     print("Node ID---------------:", node_id)
#                     for key, node_ids in conf_node_client_mapping.items():
#                         # Check if the node_id is in the list of node_ids for the current key
#                         if node_id in node_ids:
#                             print(f"Key corresponding to Node ID {node_id}: {key}")
#                             client_id = key
#                             break  # Stop the loop if the node_id is found
#                     print("cli:----", client_id)
#                     # self.send_message(client_id, message)
                

#                     message = text_data_json
#                     # for (client) in zoo:
#                     #     print(configured_clients)
#                     #     if id(client) == client_id:
#                     #         print("okkkkkkkkk")
#                     #         client.send(text_data=json.dumps(message))
#                     #         break
                    
#                     async_to_sync(self.channel_layer.group_send)(
#                         self.room_group_name,
#                         {
#                             'type':'chat_message',
#                             'message':message
#                         }
#                     )
#                     # client_id.send(text_data=json.dumps(message))
#                     # for client in configured_clients:
                    
#                         # break
#                 elif app_id == "flutter_app" and command == "state":
#                     gateways = Gateway.objects.all()

#                     config_data = []
#                     for gateway in gateways:
#                         gateway_info = {
#                             "command": "app_state",
#                             "gateway_id": gateway.gateway_id,
#                             "last_config": gateway.last_config,
#                             "nodes": []
#                         }
                 
#                         nodes = Node.objects.filter(gateway=gateway)
#                         for node in nodes:
#                             node_data = {
#                                 "node_id": node.node_id,
#                                 "devices": []
#                             }
                 
#                             devices = Device.objects.filter(node=node)
#                             for device in devices:
#                                 device_data = {
#                                     "name": device.name,
#                                     "device_id": device.device_id,
#                                     "value": device.value,
#                                 }
#                                 node_data["devices"].append(device_data)
                 
#                             gateway_info["nodes"].append(node_data)
                 
#                         config_data.append(gateway_info)
#                     print("Job", config_data)
#                     self.send(text_data=json.dumps(config_data))
                    
#         except:
#             print("Not a json...")

#     def chat_message(self, event):
#         message = event['message']

#         self.send(text_data=json.dumps(message))
        
    
        
                

# # class UpdateList(WebsocketConsumer):
# #     def connect(self):
# #         self.accept()
# #         self.clientlist()

# #     def clientlist(self):
# #         connected_clients_info = [{'client_id': id(client)} for client in connected_clients_ip]
# #         configured_clients_info = [{"configured_clients": conf_client} for conf_client in configured_clients]
# #         conf_node_client_mapping_info = [{"node_id": node_id, "client_id": client_id} for client_id, node_ids in conf_node_client_mapping.items() for node_id in node_ids]
# #         new_node_client_mapping_info = [{"node_id": node_id, "client_id": client_id} for client_id, node_ids in new_node_client_mapping.items() for node_id in node_ids]
# #         self.send(text_data=json.dumps({'connected_clients': connected_clients_info, 'configured_clients': configured_clients_info, 'conf_node_client_mapping': conf_node_client_mapping_info, 'new_node_client_mapping': new_node_client_mapping_info}))
# #     def receive(self, text_data=None, bytes_data=None):
# #     # Extract selected client from the received data
# #         received_data = json.loads(text_data)
# #         selected_client = received_data.get('client_info', None)
# #         print("Selected_client:", selected_client)
# #         if selected_client:
# #             configured_clients.add(selected_client)
# #             message = {'command': "handshake_response", 'gateway_id': gateway_serial}
# #             print("Handshake with node success...")
# #             self.send_message(selected_client, message)
# #             ip_to_remove = []
# #             for client in connected_clients_ip:
# #                 if id(client) == selected_client:
# #                     ip_to_remove.append(client)
# #             connected_clients_ip.remove(ip_to_remove[0])
                
# #             print(f'Client {selected_client} configured.')
# #         else:
# #             print("No client selected!")

# #     def send_message(self, client_id, message):

# #         for client in connected_clients_ip:
# #             print(client)
# #             if id(client) == client_id:
# #                 client.send(text_data=json.dumps(message))
# #                 break
#                   # Stop the loop once the message is sent to the desired client



import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'notifications'
        # Join notifications group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave notifications group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # This method would handle incoming WebSocket data if needed
        text_data_json = json.loads(text_data)
        print(text_data_json)
        pass

    # Custom method to send notifications to the WebSocket
    async def send_notification(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

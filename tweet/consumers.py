import json
from channels.consumer import SyncConsumer
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from rest_framework.renderers import JSONRenderer

from .models import Tweet, Clients
from .api.serializers import TweetSerializer, TestSerializer
from django.dispatch import receiver
from django.db.models.signals import post_save
from .views import tweet_list
from .utils import get_serialized_tweet, get_one_tweet, get_query_tweets
import sys
from channels.db import database_sync_to_async
from time import sleep
import threading
import asyncio


# class Timer:
#     def __init__(self, timeout, callback):
#         self._timeout = timeout
#         self._callback = callback
#         self._task = asyncio.ensure_future(self._job())
#
#     async def _job(self):
#         await asyncio.sleep(self._timeout)
#         await self._callback()
#
#     def cancel(self):
#         self._task.cancel()
#
#
#
# class FeedConsumer(AsyncWebsocketConsumer):
#
#     async def connect(self):  # HANDSHAKING
#         print("시작함:", self.channel_name)
#         print(self.scope['client'])
#         await self.accept()  # CONNECT made
#
#     async def disconnect(self, close_code):
#         self.channel_name = None
#         try:
#             await self.timer.cancel()
#         except:
#             print("HANDSHAKING 후 connect에서 accept 되지 못하면 disconnect로 넘어오므로 timer는 존재하지 않음")
#
#     async def receive(self, text_data):
#         await self.retreive_first_tweets()  # 웹소켓이 연결되어 초기 트윗 전송
#         await self.keep_sending_tweets()  # 웹소켓이 연결되면 연결된 동안 최신 트윗 계속 내보내도록 하기
#
#     async def retreive_first_tweets(self):
#         serialized_tweets_data = get_serialized_tweet()
#         self.top_tweet_id = serialized_tweets_data[0]['tweetid']
#         await self.send(json.dumps(get_serialized_tweet()))
#
#     async def keep_sending_tweets(self):
#         print(self.channel_name,"실시간 가동중")
#         serialized_tweets_data = get_query_tweets(self.top_tweet_id)  # 여기서 인수로 top_id 넣고 SELECT WHERE id>top_id
#
#         if serialized_tweets_data:
#             self.top_tweet_id = serialized_tweets_data[0]['tweetid']
#             await self.send(json.dumps(serialized_tweets_data))
#         else:
#             print("해당 토픽에 새로 생성된 트윗이 없다")
#
#
#         if self.channel_name is not None:
#             self.timer = Timer(3, self.keep_sending_tweets)
#             # self.timer.start()
#             # await asyncio.sleep(1.5)
#         else:
#             print("채널 삭제 확인")



class FeedConsumer(WebsocketConsumer):

    def connect(self):  # HANDSHAKING
        print("시작함:", self.channel_name)
        print(self.scope['client'])
        self.accept()  # CONNECT made

    def disconnect(self, close_code):
        ''' disconnect 되면 채널 이름을 삭제해서 timer 종료되도록 함.'''
        self.channel_name = None
        try:
            self.timer.cancel()
        except:
            print("HANDSHAKING 후 connect에서 accept 되지 못하면 disconnect로 넘어오므로 timer는 존재하지 않음")

    def receive(self, text_data):
        ''' 웹소켓 연결 성공 후, 프론트에서 연결 성공 메세지 수령'''
        self.retreive_first_tweets()  # 웹소켓이 연결되어 초기 트윗 전송
        self.keep_sending_tweets()  # 웹소켓이 연결되면 연결된 동안 최신 트윗 계속 내보내도록 하기

    def retreive_first_tweets(self):
        ''' 초기 트윗 가져오는 함수를 실행하고 가장 최신 트윗의 id를 저장한다'''
        serialized_tweets_data = get_serialized_tweet()
        self.top_tweet_id = serialized_tweets_data[0]['tweetid']
        self.send(json.dumps(get_serialized_tweet()))

    def keep_sending_tweets(self):
        """ 여기서 최신 트윗 인수로 넣어서 그 이후의 트윗 가져오기. 3초마다 실행 """
        serialized_tweets_data = get_query_tweets(self.top_tweet_id)  # 여기서 인수로 top_id 넣고 SELECT WHERE id>top_id

        """ 새롭게 생성된 트윗이 없다면 전송하지 않고 있는 경우에만 전송 """
        if serialized_tweets_data:
            ''' 웹소켓이 닫히더라도 timer가 돌고 있는 경우 이게 한번 더 실행됨'''
            '''새로 생성되어 조회된 트윗이 있으면 가장 처음 트윗의 id 저장하고 전송함'''
            self.top_tweet_id = serialized_tweets_data[0]['tweetid']
            self.send(json.dumps(serialized_tweets_data))
        else:
            print(self.channel_name, "해당 토픽에 새로 생성된 트윗이 없다")

        if self.channel_name is not None:
            self.timer = threading.Timer(3, self.keep_sending_tweets)
            self.timer.start()
        else:
            print("채널 삭제 확인")
#
#
#
#
#
#
#
#






# class FeedConsumer(WebsocketConsumer):
#     """특정 토픽으로 요청이 들어오면 컨슈머에 해당 토픽의 이름을 저장하고 해당하는 그룹에 컨슈머를 추가시킴."""
#     def connect(self):
#         self.keyword_name = self.scope['url_route']['kwargs']['keyword']
#         self.keyword_group_name = f'keyword_{self.keyword_name}'
#         self.new_offset = 0
#         # keyword 그룹에 현재 channel을 추가시킨다.
#         async_to_sync(self.channel_layer.group_add)(
#             self.keyword_group_name,
#             self.channel_name
#         )
#         self.accept()
#
#
#     def disconnect(self, close_code):
#         self.timer.cancel()
#         async_to_sync(self.channel_layer.group_discard)(
#             self.keyword_group_name,
#             self.channel_name
#         )
#
#
#     def receive(self, text_data):
#         print("receive 들어옴")
#         text = json.loads(text_data)
#         print("text찍어보기", text)
#         """ 특정 키워드의 요청이 들어오면 해당하는 트윗 데이터 시간 순서로 n개 내보내기"""
#         serialized_tweets_data = get_serialized_tweet()
#         """ 해당 키워드의 그룹에 속한 consumer에게 tweet 전송하기 """
#         self.count = 0
#
#         self.say_hi()
#
#
#         # await self.channel_layer.send(
#         #     self.channel_name, {
#         #         "type": "send.tweets",
#         #         "tweets": json.dumps(serialized_tweets_data)
#         #     })
#
#
#     def say_hi(self):
#         print("아임인")
#         serialized_tweets_data = get_serialized_tweet()
#         async_to_sync(self.channel_layer.send)(
#             self.channel_name, {
#                 "type": "send.tweets",
#                 "tweets": json.dumps(serialized_tweets_data)
#             })
#         self.timer = threading.Timer(2, self.say_hi)
#         self.timer.start()
#
#
#
#     def send_tweets(self, event):
#         print("여기도착", event)
#         tweets = json.loads(event["tweets"])
#         self.send(json.dumps(tweets))

# class FeedConsumer(AsyncWebsocketConsumer):
#     """특정 토픽으로 요청이 들어오면 컨슈머에 해당 토픽의 이름을 저장하고 해당하는 그룹에 컨슈머를 추가시킴."""
#     async def connect(self):
#         self.keyword_name = self.scope['url_route']['kwargs']['keyword']
#         self.keyword_group_name = f'keyword_{self.keyword_name}'
#         self.new_offset = 0
#         print(self.keyword_group_name)
#         # keyword 그룹에 현재 channel을 추가시킨다.
#         await self.channel_layer.group_add(
#             self.keyword_group_name,
#             self.channel_name
#         )
#         await self.accept()
#
#
#     async def disconnect(self, close_code):
#         self.timer.cancel()
#         await self.channel_layer.group_discard(
#             self.keyword_group_name,
#             self.channel_name
#         )
#
#
#     async def receive(self, text_data):
#         print("receive 들어옴")
#         text = json.loads(text_data)
#         print("text찍어보기", text)
#         """ 특정 키워드의 요청이 들어오면 해당하는 트윗 데이터 시간 순서로 n개 내보내기"""
#         serialized_tweets_data = get_serialized_tweet()
#         """ 해당 키워드의 그룹에 속한 consumer에게 tweet 전송하기 """
#         self.count = 0
#
#         self.say_hi()
#
#
#         # await self.channel_layer.send(
#         #     self.channel_name, {
#         #         "type": "send.tweets",
#         #         "tweets": json.dumps(serialized_tweets_data)
#         #     })
#
#
#     async def say_hi(self):
#         print("아임인")
#         serialized_tweets_data = get_serialized_tweet()
#         await self.channel_layer.send(
#             self.channel_name, {
#                 "type": "send.tweets",
#                 "tweets": json.dumps(serialized_tweets_data)
#             })
#         self.timer = threading.Timer(2, self.say_hi)
#         self.timer.start()
#
#
#
#     async def send_tweets(self, event):
#         print("여기도착", event)
#         tweets = json.loads(event["tweets"])
#         await self.send(json.dumps(tweets))


#
# class FeedConsumer(WebsocketConsumer):
#     """특정 토픽으로 요청이 들어오면 컨슈머에 해당 토픽의 이름을 저장하고 해당하는 그룹에 컨슈머를 추가시킴."""
#     def connect(self):
#         self.keyword_name = self.scope['url_route']['kwargs']['keyword']
#         self.keyword_group_name = f'keyword_{self.keyword_name}'
#         self.new_offset = 0
#         print(self.keyword_group_name)
#         # keyword 그룹에 현재 channel을 추가시킨다.
#         async_to_sync(self.channel_layer.group_add)(
#             self.keyword_group_name,
#             self.channel_name
#         )
#         self.accept()
#
#
#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.keyword_group_name,
#             self.channel_name
#         )
#
#
#     def receive(self, text_data):
#         text = json.loads(text_data)
#         """ 특정 키워드의 요청이 들어오면 해당하는 트윗 데이터 시간 순서로 n개 내보내기"""
#         serialized_tweets_data = get_serialized_tweet()
#
#         """ 해당 키워드의 그룹에 속한 consumer에게 tweet 전송하기 """
#         async_to_sync(self.channel_layer.send)(
#             self.channel_name, {
#                 "type": "send.tweets",
#                 "tweets": json.dumps(serialized_tweets_data)
#             })
#
#     def send_tweets(self, event):
#         tweets = json.loads(event["tweets"])
#         self.send(json.dumps(tweets))
#
#

import json
from channels.consumer import SyncConsumer
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from .models import Tweet, Clients
from .api.serializers import TweetSerializer, TestSerializer
from django.dispatch import receiver
from django.db.models.signals import post_save
from .views import tweet_list
from .utils import get_serialized_tweet
import sys
from channels.db import database_sync_to_async



@receiver(post_save, sender=Tweet)
def retrieve_realtime_tweet(sender, instance, created, **kwargs):
    """DB에 새로운 트윗이 추가가 되면 실시간으로 해당 토픽에 해당하는 그룹에 속한 컨슈머로 트윗을 전송한다"""
    if created:
        serializedTweet = TweetSerializer(instance)

        channel_layer = get_channel_layer()
        """해당 토픽에 해당하는 그룹으로 트윗 보내기"""
        async_to_sync(channel_layer.group_send)(
            f'keyword_{instance.keyword}', {
                "type": "send.tweet",
                "tweet": json.dumps(serializedTweet.data),
            }
        )


class FeedConsumer(WebsocketConsumer):
    """특정 토픽으로 요청이 들어오면 컨슈머에 해당 토픽의 이름을 저장하고 해당하는 그룹에 컨슈머를 추가시킴."""
    def connect(self):
        self.keyword_name = self.scope['url_route']['kwargs']['keyword']
        self.keyword_group_name = f'keyword_{self.keyword_name}'
        self.new_offset = 0
        print(self.keyword_group_name)
        # keyword 그룹에 현재 channel을 추가시킨다.
        async_to_sync(self.channel_layer.group_add)(
            self.keyword_group_name,
            self.channel_name
        )

        self.accept()








    def disconnect(self, close_code):
        """ 접속을 종료하면 해당 토픽에 해당하는 그룹에서 채널을 제거함 """
        async_to_sync(self.channel_layer.group_discard)(
            self.keyword_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        text = json.loads(text_data)
        self.limit = int(text['limit'])
        self.offset = int(text['offset'])*self.limit
        """ 특정 키워드의 요청이 들어오면 해당하는 트윗 데이터 시간 순서로 n개 내보내기"""
        tweets = Tweet.retrieve_recent_tweets(Tweet, self.keyword_name, self.offset+self.new_offset, self.limit)

        serializedTweets = TweetSerializer(tweets, many=True)
        print("10개 트윗 크기", sys.getsizeof(tweets))

        # all_tweet = Tweet.retrieve_all_tweets(Tweet)
        # print("전체 트윗 크기",sys.getsizeof(all_tweet))
        # print(all_tweet)
        #
        # single_tweet = Tweet.retrieve_first_tweet(Tweet)
        # print("하나 트윗 크기", sys.getsizeof(single_tweet))
        # print(single_tweet)

        """ 해당 키워드의 그룹에 속한 consumer에게 tweet 전송하기 """
        async_to_sync(self.channel_layer.send)(
            self.channel_name, {
                "type": "send.tweets",
                "tweets": json.dumps(serializedTweets.data)
            })


    def send_tweets(self, event):
        tweets = json.loads(event["tweets"])
        self.send(json.dumps(tweets))

    def send_tweet(self, event):
        ''' 실시간 트윗을 묶음으로 가져오면 조회된 횟수만큼 offset 증가시키기'''
        self.new_offset += 1
        tweet = json.loads(event["tweet"])
        self.send(json.dumps(tweet))





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
#         tweets = await database_sync_to_async(Tweet.retrieve_all_tweets)(Tweet)
#         serializedTweets = await sync_to_async(TweetSerializer)(tweets, many=True)
#         # jsontweet = await sync_to_async(json.dumps)(serializedTweets.data)
#         # await self.channel_layer.send(
#         #     self.channel_name, {
#         #         "type": "send.tweets",
#         #         "tweets": jsontweet
#         #     })
#
#         await self.accept()
#
#
#     async def disconnect(self, close_code):
#         """ 접속을 종료하면 해당 토픽에 해당하는 그룹에서 채널을 제거함 """
#         self.channel_layer.group_discard(
#             self.keyword_group_name,
#             self.channel_name
#         )
#
#     async def dumptweet(self, tweets):
#         return json.dumps(tweets)
#
#     async def serialize_tweet(self, tweets):
#         return TweetSerializer(tweets)
#
#     async def get_data(self, serial_tweet):
#         return serial_tweet.data
#
#     async def receive(self, text_data):
#         text = json.loads(text_data)
#         self.limit = int(text['limit'])
#         self.offset = int(text['offset'])*self.limit
#         """ 특정 키워드의 요청이 들어오면 해당하는 트윗 데이터 시간 순서로 n개 내보내기"""
#         tweets = await database_sync_to_async(Tweet.retrieve_recent_tweets)(Tweet, self.keyword_name, self.offset+self.new_offset, self.limit)
#         await sync_to_async(print)(tweets)
#         serializedTweets = await self.serialize_tweet(tweets)
#         # serializedTweets = await sync_to_async(TweetSerializer)(tweets, many=True)
#         # print("10개 트윗 크기",sys.getsizeof(tweets))
#         await sync_to_async(print)("serialized 형태", serializedTweets)
#         serialized_data = await self.get_data(serializedTweets)
#         await sync_to_async(print)(serialized_data)
#         jsontweets = await self.dumptweet(serialized_data)
#         await sync_to_async(print)("jsoon형태", jsontweets)
#         """ 해당 키워드의 그룹에 속한 consumer에게 tweet 전송하기 """
#         await self.channel_layer.send(
#             self.channel_name, {
#                 "type": "send.tweets",
#                 "tweets": json.dumps(serializedTweets.data)
#             })
#
#
#     async def send_tweets(self, event):
#         tweets = json.loads(event["tweets"])
#         await self.send(json.dumps(tweets))
#
#     async def send_tweet(self, event):
#         ''' 실시간 트윗을 묶음으로 가져오면 조회된 횟수만큼 offset 증가시키기'''
#         self.new_offset += 1
#         tweet = json.loads(event["tweet"])
#         await self.send(json.dumps(tweet))
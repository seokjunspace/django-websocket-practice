import json
from channels.consumer import SyncConsumer
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from .models import Tweet, Clients
from .api.serializers import TweetSerializer
from django.dispatch import receiver
from django.db.models.signals import post_save


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
        """ 특정 키워드의 요청이 들어오면 해당하는 트윗 데이터 시간 순서로 n개 내보내기"""
        tweets = Tweet.retrieve_recent_10_tweets(Tweet, self.keyword_name)
        serializedTweets = TweetSerializer(tweets, many=True)

        """ 해당 키워드의 그룹에 속한 consumer에게 tweet 전송하기 """
        async_to_sync(self.channel_layer.send)(
            self.channel_name, {
                "type": "send.tweet",
                "tweet": json.dumps(serializedTweets.data)
            })

    def send_tweet(self, event):
        tweets = json.loads(event["tweet"])
        self.send(json.dumps(tweets))

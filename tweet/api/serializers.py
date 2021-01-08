from rest_framework import serializers
from tweet.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = '__all__'


class TestSerializer(serializers.Serializer):
    ''' 여기서 정의된 변수명은 카산드라 DB에 저장된 변수명의 소문자변환형과 같아야 한다. '''
    tweetid = serializers.IntegerField()
    message = serializers.CharField()
    topic = serializers.CharField()

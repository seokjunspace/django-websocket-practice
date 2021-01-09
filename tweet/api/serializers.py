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


# # relation상태의 정보로 넘어오면 다음과 같이 설정하기
# class UserSerializer(serializers.Serializer):
#     userid = serializers.CharField()
#     otherinfo = serializers.CharField()
#
#
# class TweetSerializer(serializers.Serializer):
#     ''' 더 아래 정의되어있어야 하는듯, many-to-one일때는 이처럼 many=True로 하고 one-to-one이면 그냥 두기 '''
#     message = serializers.CharField()
#     user = UserSerializer(many=True)

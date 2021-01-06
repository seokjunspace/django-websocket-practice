from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from tweet.api.serializers import TweetSerializer
from tweet.models import Tweet


def index(request):
    return render(request, 'tweet/index.html')


def room(request, room_name):
    return render(request, 'tweet/room.html', {
        'room_name': room_name
    })


# @api_view(['GET', ])
def tweet_list():
    # if request.method == 'GET':
        tweet = Tweet.objects.all()
        serializer = TweetSerializer(tweet, many=True)
        # data = {'tweet': serializer.data}
        return serializer.data

from cassandra.cluster import Cluster
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from tweet.api.serializers import TweetSerializer, TestSerializer
from tweet.models import Tweet
from .utils import get_serialized_tweet, get_raw_tweets
from rest_framework.pagination import PageNumberPagination

def index(request):
    return render(request, 'tweet/index.html')


def room(request, room_name):
    return render(request, 'tweet/room.html', {
        'room_name': room_name
    })

@api_view(['GET', ])
def test_list(request):
    tweets = get_serialized_tweet()
    # print(tweets)

    return Response(tweets, status=status.HTTP_200_OK)


# @api_view(['GET', ])
def tweet_list():
    # if request.method == 'GET':
    tweet = Tweet.objects.all()
    serializer = TweetSerializer(tweet, many=True)
    # data = {'tweet': serializer.data}
    return serializer.data


# class tweetView(generics.ListAPIView):
#     '''pagination인데 queryset에 이미 serialized된것 넣어도 되는듯 ,params 요청, results에 정보'''
#     ''' 이렇게 하면 get_serialized_tweet()이 실행이 안됨.. 그냥 최초 실행 결과가 그대로 저장되어 있음'''
#     ''' 새로 생기는 값이 반영이 안됨. 서버 새로 돌려야 반영.'''
#     ''' ORM써서 하면 반영 제대로 되는데... '''
#     ''' class view에서는 내부 실행이 안됨.'''
#     ''' 장고 처음 실행할 때 여기 내부에 함수들이 실행되는거 보니 실행할때 한번 반영된게 유지되는듯'''
#     ''' 이 방법으로는 페이지네이션 안 될듯 하다'''
#     queryset = get_serialized_tweet() # 장고가 처음 구동될 때 이거 딱 한번 실행됨.
#     # queryset = get_raw_tweets()
#     serializer_class = TestSerializer
#     # print("크기찍어보기:",queryset)
#     pagination_class = PageNumberPagination
#
#     '''이거는 정상적으로 작동'''
#     # queryset = Tweet.objects.all()
#     # serializer_class = TweetSerializer
#     # print("크기찍어보기:", queryset)
#     # pagination_class = PageNumberPagination


# @api_view(['GET',])
# def tweet_function_view(request):
#     ''' paginator 사용하면 매번 다 가져와야 해서 부하가 너무 심하지 않을까?'''
#     ''' Serialization이 부하가 심한건가? 하지만 조회한 결과를 모델 객체로 가져올수가..'''
#     ''' Serialization이 부하가 심한것 아닌것으로 판명 개수 많아도 0.0초 이하로 걸림. '''
#
#     cluster = Cluster()
#     connection = cluster.connect('feed')
#
#
#     paginator = PageNumberPagination()
#     tweets = get_raw_tweets()
#     print("function내부", tweets)
#     temp_serializer = TestSerializer(instance=tweets, many=True)
#     print(temp_serializer)
#
#     result_page = paginator.paginate_queryset(temp_serializer, request)
#     serializer = TestSerializer(result_page, many=True)
#     return paginator.get_paginated_response(serializer.data)
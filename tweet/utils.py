from cassandra.cluster import Cluster
from .api.serializers import TestSerializer
import sys
import time


def logging_time(original_fn):
    def wrapper_fn(*args, **kwargs):
        start_time = time.time()
        result = original_fn(*args, **kwargs)
        end_time = time.time()
        print("WorkingTime[{}]: {} sec".format(original_fn.__name__, end_time-start_time))
        return result
    return wrapper_fn

@logging_time
def get_serialized_tweet():
    '''
        DB에서 과거 트윗을 조회하여 내보내주는 역할.
        여기서 serialization을 하여 준다. 여기서 connect하고 닫혀서 그런지
        카산드라 객체를 리턴하면 다른 파일에서는 그거를 사용하지 못하는듯.
    '''
    start_time = time.time()
    cluster = Cluster(['127.0.0.1'])
    end_time = time.time()
    print("ClusterCreationTime: {} sec".format(end_time - start_time))

    start_time = time.time()
    connection = cluster.connect('feed')
    end_time = time.time()
    print("ConnectionTime: {} sec".format(end_time - start_time))


    start_time = time.time()
    tweets = connection.execute('SELECT * FROM tweet;')
    end_time = time.time()
    print("WorkingDBTimeForLargeTweets: {} sec".format(end_time - start_time))

    size_of_tweets = sys.getsizeof(tweets)
    print("size of tweet is ", size_of_tweets)
    '''이방식으로 serialization 정상적으로 작동함 '''
    ''' 웃긴게 many=True가 아니면 변수명 제대로 안맞음'''
    start_time = time.time()
    serializer = TestSerializer(instance=tweets, many=True)
    end_time = time.time()
    print("WorkingSerializationTime: {} sec".format(end_time - start_time))
    print("size of serializer is ", sys.getsizeof(serializer.data))
    print("count of serializer is ", len(serializer.data)) #이것으로 tweet 개수 파악 가능.
    return serializer.data

@logging_time
def get_raw_tweets():

    cluster = Cluster()
    start_time = time.time()
    connection = cluster.connect('feed')
    end_time = time.time()
    print("ConnectiongDBTime: {} sec".format(end_time - start_time))

    start_time = time.time()
    tweets = connection.execute('SELECT * FROM tweet WHERE TweetID<5 ALLOW FILTERING;')
    end_time = time.time()
    print("WorkingDBTimeForSmallTweets: {} sec".format(end_time - start_time))

    return tweets


    # serialize의 부하를 확인하기 위해 여기서 선택된 개수만 serialize해볼까.
    # model_tweets = Tweet(tweets)

    # start_time = time.time()
    # serializer = TestSerializer(instance=tweets, many=True)
    # end_time = time.time()
    # print("WorkingSerializationTime: {} sec".format(end_time - start_time))
    #
    # return serializer.data
from cassandra.cluster import Cluster
from .api.serializers import TestSerializer
import sys


def get_serialized_tweet():
    '''
        DB에서 과거 트윗을 조회하여 내보내주는 역할.
        여기서 serialization을 하여 준다. 여기서 connect하고 닫혀서 그런지
        카산드라 객체를 리턴하면 다른 파일에서는 그거를 사용하지 못하는듯.
    '''
    cluster = Cluster()
    connection = cluster.connect('feed')
    tweets = connection.execute('SELECT * FROM tweet;')
    print(tweets)
    size_of_tweets = sys.getsizeof(tweets)
    print("size of tweet is ", size_of_tweets)
    '''이방식으로 serialization 정상적으로 작동함 '''
    serializer = TestSerializer(instance=tweets, many=True)
    print("size of serializer is ", sys.getsizeof(serializer.data))
    print("count of serializer is ", len(serializer.data)) #이것으로 tweet 개수 파악 가능.
    return serializer.data



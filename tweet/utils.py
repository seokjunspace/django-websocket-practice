from cassandra.cluster import Cluster
from .api.serializers import TestSerializer


def get_serialized_tweet():
    '''
        DB에서 과거 트윗을 조회하여 내보내주는 역할.
        여기서 serialization을 하여 준다. 여기서 connect하고 닫혀서 그런지
        카산드라 객체를 리턴하면 다른 파일에서는 그거를 사용하지 못하는듯.
    '''
    cluster = Cluster()
    connection = cluster.connect('feed')
    tweets = connection.execute('SELECT * FROM tweet;')
    # print(tweets)
    '''이방식으로 serialization 정상적으로 작동함 '''
    # for tweet in tweets:
    #     serializer = TestSerializer(tweet)
    #     print(serializer.data)
    # serializer = TestSerializer(tweets)
    serializer = TestSerializer(tweets, many=True)
    return serializer.data



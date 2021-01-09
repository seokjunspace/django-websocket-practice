from django.db import models


class Tweet(models.Model):
    message = models.CharField(max_length=120, null=True)
    keyword = models.CharField(max_length=120, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.id)

    def retrieve_recent_tweets(self, keyword, offset, limit):
        return Tweet.objects.order_by('-created_at').filter(keyword=keyword)[offset:offset+limit]

    def retrieve_all_tweets(self):
        return Tweet.objects.all()

    def retrieve_first_tweet(self):
        return Tweet.objects.get(id=1)

class Clients(models.Model):
    channel_name = models.CharField(max_length=32, null=False)

    def __str__(self):
        return self.channel_name

import requests
import numpy
from matplotlib import pyplot as plt
from dotenv import dotenv_values
from datetime import datetime, timedelta
config = dotenv_values(".env")
MIN_REACH = 50

"""
    Tweet characteristics to consider:
        -- is a url present?
        -- Media (Pictures and Video)
        -- Text length (> 140 or <= 140)
        -- Location of user
        -- number of hashtags
        -- # of @'s/mentions
    See https://www.tandfonline.com/doi/full/10.1080/23311975.2018.1564168
    for engagment formula

"""
def getPostsPastYear(user_id, bearer_token):    
    dtformat = '%Y-%m-%dT%H:%M:%SZ'
    max_results = 100
    start_time = datetime.utcnow() - timedelta(days=365)
    url = "https://api.twitter.com/2/users/{}/tweets?max_results={}&start_time={}".format(
        user_id, max_results, start_time.strftime(dtformat)
    )
    response = requests.get(url, headers={"Authorization": "Bearer " + bearer_token})
    response = response.json()
    return response["data"]

def get_engagement_score(tweet,user, bearer_token):
    """ -- Note that reach is simplified to a user's followers
        -- Impressions are not considered as number of views, 
           but the reach of any hashtags are considered
    """
    metrics = tweet["public_metrics"]
    diffusion = metrics["retweet_count"] + metrics["quote_count"] # Number of retweets and shares
    interaction = metrics["reply_count"] # Number of replies/comments
    approval = metrics["like_count"] # Number of likes
    reach = calculateReachPast7Days(user, bearer_token) 
    return (3 * diffusion + 2 * interaction + 1.5 * approval) * reach/1000

def calculateReachPast7Days(user, bearer_token):
    # Reach = number of followers
    return user["public_metrics"]["followers_count"]
    # Alternatively, reach = followers + magnitude of recent activity
    #return user["public_metrics"]["followers_count"] * len(getPostsPastYear(user["id"], bearer_token))

def plotTweetsByScoreIm(tweets, bearer_token):
    # Plot tweets by engagement score (require minimum engagement score to reduce volume) 
    tweets_with_images_scores = []
    tweets_wo_images_scores = []
    iter = 0
    plt.scatter([i for i in range(1,len(tweets_with_images_scores)+1)], tweets_with_images_scores, label = "Media Present")
    plt.scatter([i for i in range(1,len(tweets_wo_images_scores)+1)], tweets_wo_images_scores, label = "Media Absent")
    plt.ylabel("Tweet Engagement Score")
    plt.title("Tweet Engagement Score by Media Presence")
    plt.legend()
    plt.show()
    pass

def hasMedia(tweet, media_keys_by_id):
    return len(media_keys_by_id[tweet["id"]]) > 0

def hasPhoto(tweet, media, media_keys_by_id):
    id = tweet["id"]
    media_keys = media_keys_by_id[id]
    for i in media_keys:
        if media[i]["type"] == "photo":
            return True
    return False

def hasVideo(tweet, media, media_keys_by_id):
    id = tweet["id"]
    media_keys = media_keys_by_id[id]
    for i in media_keys:
        if media[i]["type"] == "video":
            return True
    return False

def hasAnimatedGif(tweet, media, media_keys_by_id):
    id = tweet["id"]
    media_keys = media_keys_by_id[id]
    for i in media_keys:
        if media[i]["type"] == "animated_gif":
            return True
    return False

def photoCount(tweet, media, media_keys_by_id):
    id = tweet["id"]
    media_keys = media_keys_by_id[id]
    count = 0
    for i in media_keys:
        if media[i]["type"] == "photo":
            count+=1
    return count

def gifCount(tweet, media, media_keys_by_id):
    id = tweet["id"]
    media_keys = media_keys_by_id[id]
    count = 0
    for i in media_keys:
        if media[i]["type"] == "animated_gif":
            count+=1
    return count

def videoCount(tweet, media, media_keys_by_id):
    id = tweet["id"]
    media_keys = media_keys_by_id[id]
    count = 0
    for i in media_keys:
        if media[i]["type"] == "video":
            count+=1
    return count

def saveTweetIds(tweets, bearer_token):
    id_file = open("ids.txt", "a")
    media_file = open("byMedia/media.txt", "a")
    nomedia_file = open("byMedia/nomedia.txt", "a")
    iter = 1
    for i in tweets["data"]:
        score = get_engagement_score(i,tweets["users"][i["author_id"]], bearer_token)
        id_file.write(i["id"] +  ' ' + str(score)+ "\n")
        if hasMedia(i,tweets["media_keys_by_id"]):
           media_file.write(i["id"] +  ' ' + str(score)+ "\n")
        else:
           nomedia_file.write(i["id"] +  ' ' + str(score)+ "\n")
        iter+=1


def filterTweets(response):
    previous_tweet_ids = set([line.strip().split()[0] for line in open("ids.txt")])
    tweets = {"data":[], "media": {}, "users": {}}
    media_keys_by_id = {i["id"]:[] for i in response["data"]}
    # Get previous tweets 
    for i in response["data"]:
       if i["id"] not in previous_tweet_ids and "referenced_tweets" not in i.keys():
        # New tweets that are not retweets or a reply 
        previous_tweet_ids.add(i["id"])
        if "attachments" in i.keys():
                if "media_keys" in i["attachments"].keys():
                    for j in i["attachments"]["media_keys"]:
                        media_keys_by_id[i["id"]].append(j)
        tweets["data"].append(i)
        if "media" in response["includes"]:
         for j in response["includes"]["media"]:
            tweets["media"][j["media_key"]] = j
        if "users" in response["includes"]:
            for j in response["includes"]["users"]:
                tweets["users"][j["id"]] = j
    tweets["media_keys_by_id"] = media_keys_by_id
    return tweets

def getAllTweets(filename, bearer_token):
    ids = [line.strip() for line in open(filename)]
    tweet_fields = "tweet.fields=public_metrics,referenced_tweets,entities,author_id,created_at"
    expansions="expansions=attachments.media_keys,author_id"
    user_fields = "user.fields=public_metrics"
    media_fields="media.fields=media_key,url,preview_image_url,public_metrics"
    tweets = {"data":[], "media": {}}
    media_keys_by_id = {i:[] for i in ids}
    for i in range(0,len(ids),100):
        print("Getting tweets {} to {}".format(i, i+100))
        query_ids = ",".join(ids[i:i+100])
        url ="https://api.twitter.com/2/tweets?ids={}&{}&{}&{}&{}".format(query_ids, tweet_fields, media_fields, expansions,user_fields)
        response = requests.get(url, headers={"Authorization": "Bearer " + bearer_token})
        response = response.json()
        for j in response["data"]:
            if "attachments" in j.keys():
                if "media_keys" in j["attachments"].keys():
                    for k in j["attachments"]["media_keys"]:
                        media_keys_by_id[j["id"]].append(k)
        tweets["data"].extend(response["data"])
        for j in response["includes"]["media"]:
                tweets["media"][j["media_key"]] = j
    tweets["media_keys_by_id"] = media_keys_by_id
    return tweets

def getTweetsv2(bearer_token):   
    query = open("query.txt", "r").readlines()[0].strip()
    tweet_fields = "tweet.fields=public_metrics,referenced_tweets,entities,author_id"
    expansions="expansions=attachments.media_keys,author_id"
    user_fields = "user.fields=public_metrics"
    media_fields="media.fields=media_key,url,preview_image_url,public_metrics"
    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&{}&{}&{}&max_results=100".format(
        query, tweet_fields, media_fields, expansions,user_fields
    )
    response = requests.get(url, headers={"Authorization": "Bearer " + bearer_token})
    return response.json()

if __name__ == "__main__":
    """v1.1
    #Setup Twitter API via Tweepy v1.1
    auth = tweepy.AppAuthHandler(config["TWITTER_API_KEY"], config["TWITTER_KEY_SECRET"])
    api = tweepy.API(auth)
    #Get popular anti-vax posts concerning Covid, government, politics, and propaganda    
    tweets = getPopularTweets(api)
    #Find what type of tweets are the most popular (i.e. videos, photos, just text)
    """
#    client = tweepy.Client(
#    consumer_key=config["TWITTER_API_KEY"],
#    consumer_secret=config["TWITTER_KEY_SECRET"],
#    access_token=config["TWITTER_ACCESS_TOKEN"],
#    access_token_secret=config["TWITTER_ACCESS_TOKEN_SECRET"]
#    )     
    bearer_token = config["TWITTER_BEARER_TOKEN"]
    tweets = getAllTweets("ids.txt", bearer_token)
    plotTweetsByScoreIm(tweets["data"],bearer_token)

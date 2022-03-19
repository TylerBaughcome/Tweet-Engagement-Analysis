from getpass import getuser
import sys
import curl
from dotenv import dotenv_values
from os.path import exists
from os import makedirs
from datetime import datetime, timedelta
import plot
import json
import stats
MIN_SCORE = 0
MARGIN = 15

config = dotenv_values(".env")
def getUsername(user_id, bearer_token):
    url = "https://api.twitter.com/2/users/{}".format(user_id)
    return curl.curl(url, bearer_token)["data"]["username"]

def getUserId(username, bearer_token):
    url = "https://api.twitter.com/2/users/by/username/{}".format(username)
    id =  curl.curl(url, bearer_token)["data"]["id"]
    return id


def getUserTweets(user_id, bearer_token, start_time = datetime.utcnow() - timedelta(days = 365.25*10) ):
    dtformat = '%Y-%m-%dT%H:%M:%SZ'
    max_results = 100
    tweet_fields = "tweet.fields=public_metrics,referenced_tweets,entities,author_id,created_at"
    expansions="expansions=attachments.media_keys,author_id"
    user_fields = "user.fields=public_metrics,username"
    media_fields="media.fields=media_key,url,preview_image_url,public_metrics"
    exclude = "exclude=retweets,replies"
    url = "https://api.twitter.com/2/users/{}/tweets?max_results={}&start_time={}&{}&{}&{}&{}&{}".format(
        user_id, max_results, start_time.strftime(dtformat), tweet_fields, expansions, user_fields, media_fields, exclude
    )
    data = curl.curl(url, bearer_token)
    return data
def getMaxUserTweets(user_id, bearer_token):
    allIds = set()
    dtformat = '%Y-%m-%dT%H:%M:%SZ'
    max_results = 100
    tweet_fields = "tweet.fields=public_metrics,referenced_tweets,entities,author_id,created_at"
    expansions="expansions=attachments.media_keys,author_id"
    user_fields = "user.fields=public_metrics,username"
    media_fields="media.fields=media_key,url,preview_image_url,public_metrics"
    pagination_token = ""
    exclude = "exclude=retweets,replies"
    tweets = {"data":[], "media": {}, "users": {}, "media_keys_by_id":{}}
    pagination_tokens = set()
    last_token_reached = False
    while not last_token_reached: 
        url = "https://api.twitter.com/2/users/{}/tweets?max_results={}&{}&{}&{}&{}&{}{}".format(
            user_id, max_results, tweet_fields, expansions, user_fields, media_fields, exclude,\
                "&pagination_token=" + pagination_token if len(pagination_token) > 0 else ""
        )
        inter_data = curl.curl(url, bearer_token)
        if("data" in inter_data):
            inter_data = stats.formatResponse(inter_data)
            for j in inter_data["data"]:
                if j["id"] not in allIds:
                    tweets["data"].append(j)
                    for k in inter_data["media"]:
                        tweets["media"][k] = inter_data["media"][k]
                    for k in inter_data["users"]:
                        tweets["users"][k] = inter_data["users"][k]
                    for k in inter_data["media_keys_by_id"]:
                        tweets["media_keys_by_id"][k] = inter_data["media_keys_by_id"][k]
                    allIds.add(j["id"])
        pagination_token = inter_data["pagination_token"]
        if(pagination_token in pagination_tokens):
            last_token_reached = True
        pagination_tokens.add(pagination_token)
    return tweets
def rateUserTweets(user_id, bearer_token):
    tweets = getMaxUserTweets(user_id, bearer_token)
    scores = {tweet["id"] : stats.get_engagement_score(tweet, tweets["users"][tweet["author_id"]],bearer_token) for tweet in tweets["data"]}
    return {"user": user_id, "scores": scores}

def saveUserTweetsById(username,user_id, bearer_token):
    prev_scores = {}
    if exists("byUser/{0}/{0}.txt".format(username)):
        prev_scores = {line.strip().split()[0] : float(line.strip().split()[1]) for line in open("byUser/{0}/{0}.txt".format(username))}
    else:
        makedirs("byUser/{0}".format(username))
    fp = open("byUser/{0}/{0}.txt".format(username), "w")
    scores = rateUserTweets(user_id, bearer_token)["scores"]
    for i in prev_scores:
        if i not in scores:
            scores[i] = prev_scores[i]
    for i in scores:
        fp.write(str(i) + ' ' + str(scores[i]) + "\n")
    fp.close()

def getUserTweetsById(username, bearer_token):
    if not exists("byUser/{0}/{0}.txt".format(username)):
        raise FileNotFoundError("byUser/{0}/{0}.txt".format(username))
    return stats.getAllTweets("byUser/{0}/{0}.txt".format(username), bearer_token)
        


def getUserTweetsFromFile(username):
    if exists("byUser/{0}/result.txt".format(username)):
        return json.loads(open("byUser/{0}/result.txt".format(username)).read())
    else:
        raise FileNotFoundError("getUserTweetsFromFile failed: file byUser/{0}/result.txt not found".format(username))

def getPostsPastYear(user_id, bearer_token):    
    dtformat = '%Y-%m-%dT%H:%M:%SZ'
    max_results = 100
    start_time = datetime.utcnow() - timedelta(days=365)
    url = "https://api.twitter.com/2/users/{}/tweets?max_results={}&start_time={}".format(
        user_id, max_results, start_time.strftime(dtformat)
    )
    data = curl.curl(url, bearer_token)
    return data

def plotUserTweetsByMedia(tweets, username,MIN_SCORE, bearer_token):
    plot.plotTweetsByMedia(tweets, MIN_SCORE, bearer_token, title = "Tweets by Media Presence from {}".format(username))

def plotUserTweetsByUri(tweets, username,MIN_SCORE, bearer_token):
    plot.plotTweetsByUri(tweets, MIN_SCORE, bearer_token, title = "Tweets by URI Presence from {0}".format(username))

def plotUserTweetsByGT140(tweets, username,MIN_SCORE, bearer_token):
    plot.plotTweetsByGT140(tweets, MIN_SCORE, bearer_token, title = "Tweets partitioned by 140 Characters from {}".format(username)) 

def plotUserTweetsByLength(tweets, username,MIN_SCORE, bearer_token):
    plot.plotTweetsByLength(tweets, MIN_SCORE, bearer_token, title = "Tweets By Text Length from {}".format(username))

def plotUserTweetsByJustText(tweets, username, MIN_SCORE, bearer_token):
    plot.plotTweetsByJustText(tweets, MIN_SCORE, bearer_token, title = "Tweets with Just Text from {}".format(username))

def plotUserTweetsWithin140Len(tweets, username, MIN_SCORE, margin, bearer_token):
    plot.plotTweetsWithin140Len(tweets, MIN_SCORE,bearer_token, margin, title = "Tweets within 140 $\pm$ {} Characters from {}".format(margin, username))



if __name__ == "__main__":
    username = sys.argv[1]
    bearer = config["TWITTER_BEARER_TOKEN"]
    user_id = getUserId(username, bearer)

    # Get and Save New Tweets
    #saveUserTweetsById(username, user_id,bearer)
    #tweets = getUserTweetsById(username, bearer)
    #stats.saveTweets("byUser/{0}/result.txt".format(username), tweets)

    # Get Saved Tweets
    tweets = getUserTweetsFromFile(username)

    plotUserTweetsByMedia(tweets, username, MIN_SCORE, bearer)
    plotUserTweetsByUri(tweets, username, MIN_SCORE, bearer)
    plotUserTweetsByGT140(tweets, username, MIN_SCORE, bearer)
    plotUserTweetsByLength(tweets, username, MIN_SCORE, bearer)
    plotUserTweetsByJustText(tweets, username, MIN_SCORE, bearer)
    plotUserTweetsWithin140Len(tweets, username, MIN_SCORE, MARGIN, bearer)
from numpy import result_type
import curl
import tweepy
from os.path import exists
import requests
import subprocess
import user
import plot
import json
from dotenv import dotenv_values
config = dotenv_values(".env")
MIN_SCORE = 0
HIGH_SCORE = 1000

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
    return (3 * diffusion + 2 * interaction + 1.5 * approval) * reach / 1000000

def calculateReachPast7Days(user, bearer_token):
    # Reach = number of followers
    return user["public_metrics"]["followers_count"]
    # Alternatively, reach = followers + magnitude of recent activity
    #return user["public_metrics"]["followers_count"] * len(getPostsPastYear(user["id"], bearer_token)["data"])

def has140Length(tweet):
    return len(tweet["text"]) >= 140

def hasNonTwitterUri(tweet):
    if "entities" in tweet\
            and "urls" in tweet["entities"]:
        for i in tweet["entities"]["urls"]:
            if "expanded_url" in i:
                if "twitter.com" not in i["expanded_url"]:
                    return True
            elif "display_url" in i:
                if "twitter.com" not in i["display_url"]:
                    return True
            elif "url" in i:
                if "t.co" not in i["url"]:
                    return True

def hasMedia(tweet, media_keys_by_id):
    has_urls = "entities" in tweet\
                    and "urls" in tweet["entities"]
    if has_urls:
        urls = tweet["entities"]["urls"]
        for i in urls:
            if "images" in i and len(i["images"]) > 0:
                return True 
    return len(media_keys_by_id[tweet["id"]]) > 0

def hasPhoto(tweet, media, media_keys_by_id):
    has_urls = "entities" in tweet\
                    and "urls" in tweet["entities"]
    if has_urls:
        urls = tweet["entities"]["urls"]
        for i in urls:
            if "images" in i and len(i["images"]) > 0:
                return True
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
    count = 0
    has_urls = "entities" in tweet\
                    and "urls" in tweet["entities"]
    if has_urls:
        urls = tweet["entities"]["urls"]
        for i in urls:
            if "images" in i and len(i["images"]) > 0:
                count+=len(i["images"])
    id = tweet["id"]
    media_keys = media_keys_by_id[id]
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

def saveTweetIdsSpecial(tweets, bearer_token):
    saved_tweets = 0
    id_file = open("ids.txt", "a")
    for i in tweets["data"]:
        score = get_engagement_score(i,tweets["users"][i["author_id"]], bearer_token)
        if score > MIN_SCORE:
            id_file.write(i["id"] +  ' ' + str(score)+ "\n")
            if score > HIGH_SCORE:
               username = user.getUsername(i["author_id"], bearer_token)
               command = "python3 user.py {}".format(username)
               process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
               output, error = process.communicate() 
               print("Saved user {}: " +username)
            saved_tweets+=1
    return saved_tweets

def saveTweetIds(scores, filename):
    fp = open(filename, "w")
    for i in scores:
        fp.write(str(i) + str(scores[i]))
    fp.close()

        

def getTweet(id, bearer_token):
    tweet_fields = "tweet.fields=public_metrics,referenced_tweets,entities,author_id,created_at"
    expansions="expansions=attachments.media_keys,author_id"
    user_fields = "user.fields=public_metrics,username"
    media_fields="media.fields=media_key,url,preview_image_url,public_metrics"
    url = "https://api.twitter.com/2/tweets/{}?{}&{}&{}&{}".format(id, expansions, tweet_fields, user_fields, media_fields)
    response = curl.curl(url, bearer_token)
    return response

def getTweetsById(ids, bearer_token):
    tweet_fields = "tweet.fields=public_metrics,referenced_tweets,entities,author_id,created_at"
    expansions="expansions=attachments.media_keys,author_id"
    user_fields = "user.fields=public_metrics,username"
    media_fields="media.fields=media_key,url,preview_image_url,public_metrics"
    url = "https://api.twitter.com/2/tweets?ids={}&{}&{}&{}&{}".format(",".join(ids), expansions, tweet_fields, user_fields, media_fields)
    response = curl.curl(url, bearer_token)
    return response

def formatResponse(response):
    tweets = {"data":[], "media": {}, "users": {}, "media_keys_by_id": {}}
    if("data" not in response.keys()):
        return tweets
    media_keys_by_id = {i["id"]:[] for i in response["data"]}
    # Set pagination token
    tweets["pagination_token"] = response["meta"]["next_token"] if "meta" in response and "next_token" in response["meta"] else ""
    # Get previous tweets 
    for i in response["data"]:
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


def saveSubsetOfTweets(tweets, ids, bearer_token):
        tweet_fields = "tweet.fields=public_metrics,referenced_tweets,entities,author_id,created_at"
        expansions="expansions=attachments.media_keys,author_id"
        user_fields = "user.fields=public_metrics,username"
        media_fields="media.fields=media_key,url,preview_image_url,public_metrics"
        query_ids = ",".join(ids)
        url ="https://api.twitter.com/2/tweets?ids={}&{}&{}&{}&{}".format(query_ids, tweet_fields, media_fields, expansions,user_fields)
        response = curl.curl(url, bearer_token)
        new_tweets = formatResponse(response)
        tweets["data"].extend(new_tweets["data"])
        for i in new_tweets["media"]:
            tweets["media"][i] = new_tweets["media"][i]
        for i in new_tweets["users"]:
            tweets["users"][i] = new_tweets["users"][i]
        for i in new_tweets["media_keys_by_id"]:
            tweets["media_keys_by_id"][i] = new_tweets["media_keys_by_id"][i]

def getTweetsFromFile(filename):
    if exists(filename):
        return json.loads(open(filename).read())
    else:
        raise FileNotFoundError("getTweetsFromFile failed: file {} not found".format(filename))

def getAllTweets(filename, bearer_token):
    ids = [line.strip().split()[0] for line in open(filename)]
    tweets = {"data":[], "media": {}, "users": {}, "media_keys_by_id": {}}
    for i in range(0,len(ids),25):
        print("Getting tweets {} to {} out of {}".format(i, i+25, len(ids)))
        saveSubsetOfTweets(tweets, ids[i:i+25], bearer_token)
    # Get remaining tweets
    remaining_tweets = len(ids)%25
    if remaining_tweets > 0:
        print("Getting tweets {} to {} out of {}".format(len(ids)-remaining_tweets, len(ids), len(ids)))
        saveSubsetOfTweets(tweets, ids[len(ids)-remaining_tweets:], bearer_token) 
    # Update scores
    fp = open(filename, "w")
    for i in tweets["data"]:
        fp.write(i["id"] + ' ' + str(get_engagement_score(i,tweets["users"][i["author_id"]], bearer_token)) + "\n")
    fp.close()
    return tweets

def saveTweets(filename, tweets):
    fp = open(filename, "w")
    fp.write(json.dumps(tweets))
    fp.close()

def getTweetsv2(pagination_token, bearer_token):   
    query = open("query.txt", "r").readlines()[0].strip()
    tweet_fields = "tweet.fields=public_metrics,referenced_tweets,entities,author_id,created_at"
    expansions="expansions=attachments.media_keys,author_id"
    user_fields = "user.fields=public_metrics,username"
    media_fields="media.fields=media_key,url,preview_image_url,public_metrics"
    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&{}&{}&{}&max_results=100{}".format(
        query, tweet_fields, media_fields, expansions,user_fields, "&next_token=" + pagination_token if len(pagination_token) > 0 else ""
    )
    response = requests.get(url, headers={"Authorization": "Bearer {}".format(bearer_token)})
    return response.json()


def getPopularTweetIds():
    auth = tweepy.AppAuthHandler(config["TWITTER_API_KEY"], config["TWITTER_KEY_SECRET"])
    api = tweepy.API(auth)
    query = " ".join(open("query.txt", "r").readlines()[0].strip().split()[:29])
    return list(map(str, api.search_tweets(query, count=100, result_type="popular", include_entities=True).ids()))

if __name__ == "__main__":
    """v1.1
    """
    #Setup Twitter API via Tweepy v1.1
    #Get popular anti-vax posts concerning Covid, government, politics, and propaganda    
    v1tweets = getPopularTweetIds()

    """v2"""
    #Find what type of tweets are the most popular (i.e. videos, photos, just text)
    bearer_token = config["TWITTER_BEARER_TOKEN"]
    tweets = getAllTweets("ids.txt", bearer_token)
    saveTweets('result.txt',tweets)
    #tweets = getTweetsFromFile("result.txt")
    plot.plotTweetsByLength(tweets, MIN_SCORE, bearer_token)
    plot.plotTweetsByMedia(tweets, MIN_SCORE, bearer_token)
    plot.plotTweetsByUri(tweets, MIN_SCORE, bearer_token)
    plot.plotTweetsByJustText(tweets, MIN_SCORE, bearer_token)
    plot.plotTweetsByGT140(tweets, MIN_SCORE, bearer_token)
    plot.plotTweetsWithin140Len(tweets, MIN_SCORE,bearer_token, 15)


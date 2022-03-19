from matplotlib import pyplot as plt
import numpy as np
import stats
from datetime import datetime


def plotTweetsByJustText(tweets, min_score, bearer_token, title = "Tweet Engagement Score by Sole Text Presence"):
    # Sort entries by time

    # Identify media
    tweets_with_text = []
    tweets_wo_text = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_text = 0
    ave_score_no_text = 0
    for i in tweets["data"]:
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        date = datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if not stats.hasMedia(i, tweets["media_keys_by_id"]) and not stats.hasNonTwitterUri(i) and score > min_score:
            tweets_with_text.append((score, date))
            ave_score_text += score
        elif score > min_score:
            tweets_wo_text.append((score, date))
            ave_score_no_text += score
    ave_score_text/=len(tweets_with_text)
    ave_score_no_text/=len(tweets_wo_text)
    print("AVERAGE SCORE TWEETS WITH TEXT: " + str(ave_score_text))
    print("AVERAGE SCORE TWEETS WITHOUT TEXT: " + str(ave_score_no_text))
    max_score = max(max([i[0] for i in tweets_wo_text]), max([i[0] for i in tweets_with_text]))
    tweets_with_text = [(i[0]/max_score, i[1]) for i in tweets_with_text]
    tweets_wo_text = [(i[0]/max_score, i[1]) for i in tweets_wo_text]
    tweets_with_text = list(filter(lambda x: x[0] >= .1, tweets_with_text))
    tweets_wo_text = list(filter(lambda x: x[0] >= .1, tweets_wo_text))
    plt.scatter([i[1] for i in tweets_with_text], [i[0] for i in tweets_with_text], label = "Just Text")
    plt.scatter([i[1] for i in tweets_wo_text], [i[0] for i in tweets_wo_text], label = "Other Attributes Present(e.g. media)")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    plt.show()

def plotTweetsByMedia(tweets, min_score, bearer_token, title = "Tweet Engagement Score by Media Presence"):
    # Identify media
    tweets_with_images_scores = []
    tweets_wo_images_scores = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_media = 0
    ave_score_no_media = 0
    for i in tweets["data"]:
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        date = datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if stats.hasMedia(i, tweets["media_keys_by_id"]) and score > min_score:
            tweets_with_images_scores.append((score, date))
            ave_score_media += score
        elif score > min_score:
            tweets_wo_images_scores.append((score, date))
            ave_score_no_media += score
    ave_score_media/=len(tweets_with_images_scores)
    ave_score_no_media/=len(tweets_wo_images_scores)
    print("AVERAGE SCORE TWEETS WITH MEDIA: " + str(ave_score_media))
    print("AVERAGE SCORE TWEETS WITHOUT MEDIA: " + str(ave_score_no_media))
    max_score = max(max([i[0] for i in tweets_wo_images_scores]), max([i[0] for i in tweets_with_images_scores]))
    tweets_with_images_scores = [(i[0]/max_score, i[1]) for i in tweets_with_images_scores]
    tweets_wo_images_scores = [(i[0]/max_score, i[1]) for i in tweets_wo_images_scores]
    tweets_with_images_scores = list(filter(lambda x: x[0] >= .1, tweets_with_images_scores))
    tweets_wo_images_scores = list(filter(lambda x: x[0] >= .1, tweets_wo_images_scores))
    plt.scatter([i[1] for i in tweets_with_images_scores], [i[0] for i in tweets_with_images_scores], label = "Media Present")
    plt.scatter([i[1] for i in tweets_wo_images_scores], [i[0] for i in tweets_wo_images_scores], label = "Media Absent")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    plt.show()

def plotTweetsByUri(tweets, min_score, bearer_token, title = "Tweet Engagement Score by Uri Presence"):
    # Identify media
    tweets_with_uri = []
    tweets_wo_uri = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_uri = 0
    ave_score_no_uri = 0
    for i in tweets["data"]:
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        if stats.hasNonTwitterUri(i) and score > min_score:
            tweets_with_uri.append((stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token), datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')))
            ave_score_uri+=score
        elif score > min_score:
            tweets_wo_uri.append((stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token), datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')))
            ave_score_no_uri+=score
    ave_score_uri/=len(tweets_with_uri)
    ave_score_no_uri/=len(tweets_wo_uri)
    print("AVERAGE SCORE TWEETS WITH URI: " + str(ave_score_uri))
    print("AVERAGE SCORE TWEETS WITHOUT URI: " + str(ave_score_no_uri))
    max_score = max(max([i[0] for i in tweets_wo_uri]), max([i[0] for i in tweets_with_uri]))
    tweets_with_uri = [(i[0]/max_score, i[1]) for i in tweets_with_uri]
    tweets_wo_uri = [(i[0]/max_score, i[1]) for i in tweets_wo_uri]
    tweets_with_uri = list(filter(lambda x: x[0] >= .1, tweets_with_uri))
    tweets_wo_uri = list(filter(lambda x: x[0] >= .1, tweets_wo_uri))
    plt.scatter([i[1] for i in tweets_with_uri], [i[0] for i in tweets_with_uri], label = "Uri Present")
    plt.scatter([i[1] for i in tweets_wo_uri], [i[0] for i in tweets_wo_uri], label = "Uri Absent")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    plt.show()

def plotTweetsByGT140(tweets, min_score, bearer_token,  title = "Tweet Engagement Score by Longer and Shorter Text"):
    # Identify media
    tweets_with_140 = []
    tweets_wo_140 = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_140 = 0
    ave_score_no_140 = 0 
    for i in tweets["data"]:
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        date = datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if stats.has140Length(i) and score > min_score:
            tweets_with_140.append((score, date))
            ave_score_140+=score
        elif score > min_score:
            tweets_wo_140.append((score, date))
            ave_score_no_140+=score
    ave_score_140/=len(tweets_with_140)
    ave_score_no_140/=len(tweets_wo_140)
    max_score = max(max([i[0] for i in tweets_wo_140]), max([i[0] for i in tweets_with_140]))
    tweets_with_140 = [(i[0]/max_score, i[1]) for i in tweets_with_140]
    tweets_wo_140 = [(i[0]/max_score, i[1]) for i in tweets_wo_140]
    tweets_with_140 = list(filter(lambda x: x[0] >= .1, tweets_with_140))
    tweets_wo_140 = list(filter(lambda x: x[0] >= .1, tweets_wo_140))
    plt.scatter([i[1] for i in tweets_with_140], [i[0] for i in tweets_with_140], label = "Tweet Text Length $\geq$ 140")
    plt.scatter([i[1] for i in tweets_wo_140], [i[0] for i in tweets_wo_140], label = "Tweet Text Length < 140")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    plt.show()

def plotTweetsByLength(tweets, min_score, bearer_token, title = "Tweet Engagement Score by Text Length"):
    scores = []
    for i in tweets["data"]:
         score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
         if score > min_score:
            scores.append((score, len(i["text"])))
    scores.sort(key = lambda x: x[1])
    max_score = max(scores, key = lambda x: x[0])[0]
    scores = (list(map(lambda x: (x[0]/max_score,x[1]), scores)))
    scores = list(filter(lambda x: x[0] >= .1 , scores))
    x = [i[1] for i in scores]
    y = [i[0] for i in scores]
    plt.scatter(x,y)
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    plt.show()

def quadRegression(x,y, plot):
    #polynomial fit with degree = 2
    model = np.poly1d(np.polyfit(x, y, 2))
    #add fitted polynomial line to scatterplot
    polyline = np.linspace(0, max(x),  10)
    plot.plot(polyline, model(polyline))


def plotTweetsWithin140Len(tweets, min_score, bearer_token, margin, title = "Tweet Engagement Score by Sole Text Presence"):
    # Sort entries by time

    # Identify media
    tweets_with_text = []
    tweets_wo_text = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_text = 0
    ave_score_wo_text = 0
    for i in tweets["data"]:
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        date = datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if 140 - margin <= len(i["text"]) <= 140+margin and score > min_score:
            tweets_with_text.append((score, date))
            ave_score_text+=score
        elif score > min_score:
            tweets_wo_text.append((score, date))
            ave_score_wo_text
    ave_score_text/=len(tweets_with_text)
    ave_score_wo_text/=len(tweets_wo_text)
    print("Average Score with Text: " + str(ave_score_text))
    print("Average Score without Text: " + str(ave_score_wo_text))
    max_score = max(max([i[0] for i in tweets_wo_text]), max([i[0] for i in tweets_with_text]))
    tweets_with_text = [(i[0]/max_score, i[1]) for i in tweets_with_text]
    tweets_wo_text = [(i[0]/max_score, i[1]) for i in tweets_wo_text]
    tweets_with_text = list(filter(lambda x: x[0] >= .1, tweets_with_text))
    tweets_wo_text = list(filter(lambda x: x[0] >= .1, tweets_wo_text))
    plt.scatter([i[1] for i in tweets_with_text], [i[0] for i in tweets_with_text], label = "Tweets within 140 $\pm$ characters")
    plt.scatter([i[1] for i in tweets_wo_text], [i[0] for i in tweets_wo_text], label = "Tweets outside 140 $\pm$ characters")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    plt.show()

from matplotlib import pyplot as plt
import numpy as np
import stats
import csv
from datetime import datetime
UPPER_PERCENTILE = .05

def saveFig(plt, folder, dest):
    fig = plt.gcf()
    fig.set_size_inches((13, 9), forward=False)
    fig.savefig(folder + dest, dpi=500)

def saveTweetsToCSV(tweets, folder, dest, extra_field):
    fp = open("{}{}".format(folder, dest), "w")
    writer =  csv.writer(fp)
    header = ["id", "created_at", "score", extra_field]
    writer.writerow(header)
    for i in tweets["data"]:
        row = [i[j] for j in i.keys()]
        writer.writerow([i["id"], i["created_at"], i["score"], i[extra_field]])

def plotTweetsByJustText(tweets, min_score, bearer_token, title = "Tweet Engagement Score by Sole Text Presence",save_to = ""):
    # Sort entries by time

    # Identify media
    tweets_with_text = []
    tweets_wo_text = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_text = 0
    ave_score_no_text = 0
    needed_data = []
    for j in range(len(tweets["data"])):
        i = tweets["data"][j]
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        date = datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if not stats.hasMedia(i, tweets["media_keys_by_id"]) and not stats.hasNonTwitterUri(i) and score > min_score:
            tweets_with_text.append((score, date))
            ave_score_text += score
            tweets["data"][j]["just_text"] = True
        elif score > min_score:
            tweets_wo_text.append((score, date))
            tweets["data"][j]["just_text"] = False
            ave_score_no_text += score
        tweets["data"][j]["score"] = score
    ave_score_text/=len(tweets_with_text)
    ave_score_no_text/=len(tweets_wo_text)
    print("AVERAGE SCORE TWEETS WITH TEXT: " + str(ave_score_text))
    print("AVERAGE SCORE TWEETS WITHOUT TEXT: " + str(ave_score_no_text))
    max_score = max(max([i[0] for i in tweets_wo_text]), max([i[0] for i in tweets_with_text]))
    tweets_with_text = [(i[0]/max_score, i[1]) for i in tweets_with_text]
    tweets_wo_text = [(i[0]/max_score, i[1]) for i in tweets_wo_text]
    tweets_with_text = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_with_text))
    tweets_wo_text = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_wo_text))
    plt.scatter([i[1] for i in tweets_with_text], [i[0] for i in tweets_with_text], label = "Just Text")
    plt.scatter([i[1] for i in tweets_wo_text], [i[0] for i in tweets_wo_text], label = "Other Attributes Present(e.g. media)")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    if len(save_to) > 0:
        saveFig(plt, save_to, "justText.png")
        saveTweetsToCSV(tweets, save_to, "justText.csv", "just_text")
    else:
        plt.show()
    clearPlt()

def plotTweetsByMedia(tweets, min_score, bearer_token, title = "Tweet Engagement Score by Media Presence",save_to = ""):
    # Identify media
    tweets_with_images_scores = []
    tweets_wo_images_scores = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_media = 0
    ave_score_no_media = 0
    for j in range(len(tweets["data"])):
        i = tweets["data"][j]
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        tweets["data"][j]["score"] = score
        date = datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if stats.hasMedia(i, tweets["media_keys_by_id"]) and score > min_score:
            tweets_with_images_scores.append((score, date))
            ave_score_media += score
            tweets["data"][j]["media_present"] = True
        elif score > min_score:
            tweets_wo_images_scores.append((score, date))
            ave_score_no_media += score
            tweets["data"][j]["media_present"] = False
    ave_score_media/=len(tweets_with_images_scores)
    ave_score_no_media/=len(tweets_wo_images_scores)
    print("AVERAGE SCORE TWEETS WITH MEDIA: " + str(ave_score_media))
    print("AVERAGE SCORE TWEETS WITHOUT MEDIA: " + str(ave_score_no_media))
    max_score = max(max([i[0] for i in tweets_wo_images_scores]), max([i[0] for i in tweets_with_images_scores]))
    tweets_with_images_scores = [(i[0]/max_score, i[1]) for i in tweets_with_images_scores]
    tweets_wo_images_scores = [(i[0]/max_score, i[1]) for i in tweets_wo_images_scores]
    tweets_with_images_scores = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_with_images_scores))
    tweets_wo_images_scores = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_wo_images_scores))
    plt.scatter([i[1] for i in tweets_with_images_scores], [i[0] for i in tweets_with_images_scores], label = "Media Present")
    plt.scatter([i[1] for i in tweets_wo_images_scores], [i[0] for i in tweets_wo_images_scores], label = "Media Absent")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    if len(save_to) > 0:
        saveFig(plt, save_to, "byMedia.png")
        saveTweetsToCSV(tweets, save_to, "byMedia.csv", "media_present")
    else:
        plt.show()
    clearPlt()

def plotTweetsByUri(tweets, min_score, bearer_token, title = "Tweet Engagement Score by URL Presence", save_to = ""):
    # Identify media
    tweets_with_uri = []
    tweets_wo_uri = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_uri = 0
    ave_score_no_uri = 0
    for j in range(len(tweets["data"])):
        i = tweets["data"][j]
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        tweets["data"][j]["score"] = score
        if stats.hasNonTwitterUri(i) and score > min_score:
            tweets_with_uri.append((stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token), datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')))
            ave_score_uri+=score
            tweets["data"][j]["url_present"] = True
        elif score > min_score:
            tweets_wo_uri.append((stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token), datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')))
            ave_score_no_uri+=score
            tweets["data"][j]["url_present"] = False
    ave_score_uri/=len(tweets_with_uri)
    ave_score_no_uri/=len(tweets_wo_uri)
    print("AVERAGE SCORE TWEETS WITH URL: " + str(ave_score_uri))
    print("AVERAGE SCORE TWEETS WITHOUT URL: " + str(ave_score_no_uri))
    max_score = max(max([i[0] for i in tweets_wo_uri]), max([i[0] for i in tweets_with_uri]))
    tweets_with_uri = [(i[0]/max_score, i[1]) for i in tweets_with_uri]
    tweets_wo_uri = [(i[0]/max_score, i[1]) for i in tweets_wo_uri]
    tweets_with_uri = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_with_uri))
    tweets_wo_uri = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_wo_uri))
    plt.scatter([i[1] for i in tweets_with_uri], [i[0] for i in tweets_with_uri], label = "URL Present")
    plt.scatter([i[1] for i in tweets_wo_uri], [i[0] for i in tweets_wo_uri], label = "URL Absent")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    if len(save_to) > 0:
        saveFig(plt, save_to, "byUri.png")
        saveTweetsToCSV(tweets, save_to, "byUri.csv", "url_present")
    else:
        plt.show()
    clearPlt()

def plotTweetsByGT140(tweets, min_score, bearer_token,  title = "Tweet Engagement Score by Longer and Shorter Text",save_to = ""):
    # Identify media
    tweets_with_140 = []
    tweets_wo_140 = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_140 = 0
    ave_score_no_140 = 0 
    for j in range(len(tweets["data"])):
        i = tweets["data"][j]
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        tweets["data"][j]["score"] = score
        date = datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if stats.has140Length(i) and score > min_score:
            tweets_with_140.append((score, date))
            ave_score_140+=score
            tweets["data"][j]["length_gt_140"] = True
        elif score > min_score:
            tweets_wo_140.append((score, date))
            ave_score_no_140+=score
            tweets["data"][j]["length_gt_140"] = False
    ave_score_140/=len(tweets_with_140)
    ave_score_no_140/=len(tweets_wo_140)
    max_score = max(max([i[0] for i in tweets_wo_140]), max([i[0] for i in tweets_with_140]))
    tweets_with_140 = [(i[0]/max_score, i[1]) for i in tweets_with_140]
    tweets_wo_140 = [(i[0]/max_score, i[1]) for i in tweets_wo_140]
    tweets_with_140 = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_with_140))
    tweets_wo_140 = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_wo_140))
    plt.scatter([i[1] for i in tweets_with_140], [i[0] for i in tweets_with_140], label = "Tweet Text Length $\geq$ 140")
    plt.scatter([i[1] for i in tweets_wo_140], [i[0] for i in tweets_wo_140], label = "Tweet Text Length < 140")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    if len(save_to) > 0:
        saveFig(plt, save_to,  "GT140.png")
        saveTweetsToCSV(tweets, save_to, "GT140.csv", "length_gt_140")
    else:
        plt.show()
    clearPlt()


def plotTweetsByLength(tweets, min_score, bearer_token, title = "Tweet Engagement Score by Text Length",save_to = ""):
    scores = []
    for j in range(len(tweets["data"])):
         i = tweets["data"][j]
         score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
         tweets["data"][j]["score"] = score
         tweets["data"][j]["text_length"] = len(i["text"])
         if score > min_score:
            scores.append((score, len(i["text"])))
    scores.sort(key = lambda x: x[1])
    max_score = max(scores, key = lambda x: x[0])[0]
    scores = (list(map(lambda x: (x[0]/max_score,x[1]), scores)))
    scores = list(filter(lambda x: x[0] >= UPPER_PERCENTILE , scores))
    x = [i[1] for i in scores]
    y = [i[0] for i in scores]
    plt.scatter(x,y)
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    if len(save_to) > 0:
        saveFig(plt, save_to, "tweets_by_length.png")
        saveTweetsToCSV(tweets, save_to, "tweets_by_length.csv", "text_length")
    else:
        plt.show()
    clearPlt()

def quadRegression(x,y, plot):
    #polynomial fit with degree = 2
    model = np.poly1d(np.polyfit(x, y, 2))
    #add fitted polynomial line to scatterplot
    polyline = np.linspace(0, max(x),  10)
    plot.plot(polyline, model(polyline))


def plotTweetsWithin140Len(tweets, min_score, bearer_token, margin, title = "Tweet Engagement Score by Sole Text Presence",save_to = ""):
    # Sort entries by time

    # Identify media
    tweets_with_text = []
    tweets_wo_text = []
    tweets["data"] = sorted(tweets["data"], key = lambda x: datetime.strptime(x["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ'))
    ave_score_text = 0
    ave_score_wo_text = 0
    for j in range(len(tweets["data"])):
        i = tweets["data"][j]
        score = stats.get_engagement_score(i, tweets["users"][i["author_id"]], bearer_token)
        tweets["data"][j]["score"] = score
        date = datetime.strptime(i["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if 140 - margin <= len(i["text"]) <= 140+margin and score > min_score:
            tweets_with_text.append((score, date))
            ave_score_text+=score
            tweets["data"][j]["length_between{}_and_{}".format(140-margin, 140+margin)] = True
        elif score > min_score:
            tweets_wo_text.append((score, date))
            ave_score_wo_text
            tweets["data"][j]["length_between{}_and_{}".format(140-margin, 140+margin)] = False
    ave_score_text/=len(tweets_with_text)
    ave_score_wo_text/=len(tweets_wo_text)
    print("Average Score with {} <= len(Text) <= {}: ".format(140-margin, 140+margin) + str(ave_score_text))
    print("Average Score without length(Text) < {} or length(Text) > {}: ".format(140-margin, 140+margin) + str(ave_score_wo_text))
    max_score = max(max([i[0] for i in tweets_wo_text]), max([i[0] for i in tweets_with_text]))
    tweets_with_text = [(i[0]/max_score, i[1]) for i in tweets_with_text]
    tweets_wo_text = [(i[0]/max_score, i[1]) for i in tweets_wo_text]
    tweets_with_text = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_with_text))
    tweets_wo_text = list(filter(lambda x: x[0] >= UPPER_PERCENTILE, tweets_wo_text))
    plt.scatter([i[1] for i in tweets_with_text], [i[0] for i in tweets_with_text], label = "Tweets within 140 $\pm$ characters")
    plt.scatter([i[1] for i in tweets_wo_text], [i[0] for i in tweets_wo_text], label = "Tweets outside 140 $\pm$ characters")
    plt.ylabel("Tweet Engagement Score")
    plt.title(title)
    plt.legend()
    if len(save_to) > 0:
        saveFig(plt, save_to,  "within140Len.png")
        saveTweetsToCSV(tweets, save_to, "within140len.csv", "length_between{}_and_{}".format(140-margin, 140+margin))
    else:
        plt.show()
    clearPlt()

def clearPlt():
    plt.close()
    plt.cla()
    plt.clf()


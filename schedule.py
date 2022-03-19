from stats import getPopularTweetIds, getTweetsv2, saveTweetIdsSpecial, getTweetsById
from filter import filterTweets, combineTweets
import datetime
import time
from dotenv import dotenv_values
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
starttime = time.time()
config = dotenv_values(".env")

def getAndSaveTweets(filename, pagination_token):
	bearer_token = config["TWITTER_BEARER_TOKEN"]
	tweetsv1 = getTweetsById(getPopularTweetIds(), bearer_token)
	tweetsv2 = getTweetsv2(pagination_token[0], bearer_token)
	next_token = tweetsv2["meta"]["next_token"] if "meta" in tweetsv2 and "next_token" in tweetsv2["meta"] else ""
	pagination_token[0] = next_token
	tweetsv1 = filterTweets(tweetsv1)
	tweetsv2 = filterTweets(tweetsv2)
	tweets = combineTweets(tweetsv1, tweetsv2)
	tweets_saved = saveTweetIdsSpecial(tweets,bearer_token)
	fp = open("updates.txt","a")
	fp.write("{} tweets saved at {}\n".format(tweets_saved, datetime.datetime.now()))
	fp.close()


if __name__ == "__main__":
	bearer_token = config["TWITTER_BEARER_TOKEN"]
	pagination_token = [""]
	scheduler = BackgroundScheduler()
	scheduler.configure(timezone=utc)
	scheduler.add_job(lambda: getAndSaveTweets("ids.txt", pagination_token), 'interval', seconds=600)
	scheduler.start()
	while True:
		time.sleep(595)

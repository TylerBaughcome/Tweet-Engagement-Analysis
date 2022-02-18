from stats import getTweetsv2, filterTweets, saveTweetIds
import datetime
import time
from dotenv import dotenv_values
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
starttime = time.time()
config = dotenv_values(".env")

def getAndSaveTweets():
    bearer_token = config["TWITTER_BEARER_TOKEN"]
    tweets = getTweetsv2(bearer_token)
    tweets = filterTweets(tweets)
    saveTweetIds(tweets,bearer_token)
    fp = open("updates.txt","a")
    fp.write("{} tweets saved at {}\n".format(len(tweets["data"]), datetime.datetime.now()))


if __name__ == "__main__":
	bearer_token = config["TWITTER_BEARER_TOKEN"]
	scheduler = BackgroundScheduler()
	scheduler.configure(timezone=utc)
	scheduler.add_job(getAndSaveTweets, 'interval', seconds=30)
	scheduler.start()
	while True:
		time.sleep(25)	

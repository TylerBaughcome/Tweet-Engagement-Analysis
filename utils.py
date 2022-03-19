from stats import get_engagement_score, getAllTweets, filterTweets, hasMedia
import sys
def filterFile(filename, min_reach):
    new_lines = []
    for line in open(filename):
        val = float(line.strip().split()[1])
        if val > min_reach:
            new_lines.append(line)
    fp = open(filename, "w")
    for line in new_lines:
        fp.write(line)
    fp.close()

def repartitionMedia(bearer_token, min_reach):
    media_file = open("byMedia/media.txt", "w")
    nomedia_file = open("byMedia/nomedia.txt", "w")
    tweets = getAllTweets("ids.txt", bearer_token)
    for i in tweets["data"]:
        score = get_engagement_score(i,tweets["users"][i["author_id"]], bearer_token)
        if hasMedia(i, tweets["media_keys_by_id"]) and score > min_reach:
            media_file.write(i["id"] +  ' ' + str(score)+ "\n")
        elif score > min_reach:
            nomedia_file.write(i["id"] +  ' ' + str(score)+ "\n")
    media_file.close()
    nomedia_file.close()

if __name__ == "__main__":
    bearer_token = sys.argv[1]
    repartitionMedia(bearer_token, 30)
def filterTweets(response):
    previous_tweet_ids = set([line.strip().split()[0] for line in open("ids.txt")])
    tweets = {"data":[], "media": {}, "users": {}}
    # Set pagination token
    tweets["pagination_token"] = response["meta"]["next_token"] if "meta" in response.keys() and "next_token" in response["meta"] else ""
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

def combineTweets(tweets1, tweets2):
    tweets = {"data":[], "media": {}, "users": {}, "media_keys_by_id": {}}
    for i in tweets1["data"]:
        tweets["data"].append(i)
    for i in tweets2["data"]:
        tweets["data"].append(i)
    for i in tweets1["media"].keys():
        if i not in tweets:
            tweets["media"][i] = tweets1["media"][i]
    for i in tweets2["media"].keys():
        if i not in tweets:
            tweets["media"][i] = tweets2["media"][i]
    for i in tweets1["users"].keys():
        if i not in tweets:
            tweets["users"][i] = tweets1["users"][i]
    for i in tweets2["users"].keys():
        if i not in tweets:
            tweets["users"][i] = tweets2["users"][i]
    for i in tweets1["media_keys_by_id"].keys():
        if i not in tweets:
            tweets["media_keys_by_id"][i] = tweets1["media_keys_by_id"][i]
    for i in tweets2["media_keys_by_id"].keys():
        if i not in tweets:
            tweets["media_keys_by_id"][i] = tweets2["media_keys_by_id"][i]
    return tweets
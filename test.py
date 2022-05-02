import sys
def getIdsToScore(csv_file):
    ids_to_score = {}
    for line in csv_file:
        content = line.strip().split(',')
        score = content[2]
        id = content[0]
        ids_to_score[id] = score
    return ids_to_score


def assertSameScoresForUser(username):
    """
    Check that all csvs have the same score for a given id
    """
    media_csv = open("byUser/{}/byMedia.csv".format(username), "r")
    uri_csv = open("byUser/{}/byUri.csv".format(username), "r")
    tl_csv = open("byUser/{}/tweets_by_length.csv".format(username), "r")
    within140_csv = open("byUser/{}/within140len.csv".format(username), "r")

    media_ids_to_score = getIdsToScore(media_csv)
    uri_ids_to_score = getIdsToScore(uri_csv)
    tl_ids_to_score = getIdsToScore(tl_csv)
    within140_ids_to_score = getIdsToScore(within140_csv)
    for i in media_ids_to_score:
        assert media_ids_to_score[i] == uri_ids_to_score[i]
        assert media_ids_to_score[i] == tl_ids_to_score[i]
        assert media_ids_to_score[i] == within140_ids_to_score[i]
    for i in uri_ids_to_score:
        assert uri_ids_to_score[i] == tl_ids_to_score[i]
        assert uri_ids_to_score[i] == within140_ids_to_score[i]
        assert uri_ids_to_score[i] == media_ids_to_score[i]
    for i in tl_ids_to_score:
        assert tl_ids_to_score[i] == within140_ids_to_score[i]
        assert tl_ids_to_score[i] == media_ids_to_score[i]
        assert tl_ids_to_score[i] == uri_ids_to_score[i]
    for i in within140_ids_to_score:
        assert within140_ids_to_score[i] == media_ids_to_score[i]
        assert within140_ids_to_score[i] == uri_ids_to_score[i]
        assert within140_ids_to_score[i] == tl_ids_to_score[i]

if __name__ == "__main__":
    username = sys.argv[1]
    assertSameScoresForUser(username)
    
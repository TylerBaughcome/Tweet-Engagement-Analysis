# Tweet-Engagement-Analysis
<h1>
  Introduction
  </h1>
This repostiory analyzes the attributes of tweets eliciting an anti-vax sentiment. Hence, we seek "successful" tweets that meet a search criteria, where, by successful, we mean that the tweet exhibits user engagement of a high quality (the user spends time on the tweet) and quatity (many users interact with the tweet). Measuring the success of a tweet requires several heuristics and formulas
  that tell us just how successful the tweet is, and measuring its success requires examining patterns displayed by its author as well. For example, if we observe that account <em>A</em>'s most successful tweets are usually those with images, and account <em>A</em> posts a new tweet eliciting an anti-vax sentiment, then we can estimate the success of this tweet by determining if it has an image. The <strong>methods</strong> section further details 
  the use of this reasoning. 
<h1>
  Methods
   </h1>
   <h2>API Use</h2>
  To programatically retrieve tweets that meet our criteria, we make use of Twitter's APIs. Namely, we make use of Twitter API v1.1 and Twitter API v2. Note that the use of both APIs relies on a search query that returns tweets in the domain of anti-vax, including events surrounding vaccinations, such as the "Truckey Convoy", and tweets that discuss and express opinions vaccinations. The query string is not listed here, as it is particularly long, but it can be found in <strong>query.txt</strong>.
  <h3>
    Twitter API v1.1
  </h3>
  This API was used to retrieve popular tweets that meet the search criteria. Here, the criterion of popular is defined by Twitter, but it can be generally be thought of as those tweets with a high like count, reply count, and share count. We only use one API endpoint from v1.1, and it can be found here: [Standard Search API Reference](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets).


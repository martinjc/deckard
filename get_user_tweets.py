#!/usr/bin/env python
#

import os
import sys
import csv
import json
import argparse

from twitter_api import Twitter_API
from file_cache import JSONFileCache


def get_tweet_history(api, am):

    # make an api call to get the most recent tweets of the am
    params = {
        "screen_name": am,
        "count": 200,
        "exclude_replies": "false"
    }
    tweets = api.query_get("statuses", "user_timeline", params)

    # find the earliest tweet retrieved
    if len(tweets) > 0:
        earliest_id = tweets[0]["id"]
        for tweet in tweets:
            if tweet["id"] < earliest_id:
                earliest_id = tweet["id"]

        # assume there are more tweets to retrieve
        more_tweets = True

        # while there are more tweets to retrieve
        while(more_tweets):

            # make an api call to get the tweets prior
            # to our earliest retrieved tweet so far
            params = {
                "screen_name": am,
                "count": 200,
                "exclude_replies": "false",
                "max_id": earliest_id
            }

            new_tweets = ta.query_get("statuses", "user_timeline", params)

            # add the newly retrieved tweets to our list
            tweets.extend(new_tweets)

            # find the earliest retrieved tweet
            current_earliest = earliest_id
            for tweet in tweets:
                if tweet["id"] < earliest_id:
                    earliest_id = tweet["id"]

            # if the earliest tweet hasn't changed
            # we can't go back any further
            if current_earliest == earliest_id:
                more_tweets=False

    return tweets


def get_latest_tweets(api, am, tweets):

    # find the latest tweet retrieved
    latest_id = 0
    for tweet in tweets:
        if tweet["id"] > latest_id:
            latest_id = tweet["id"]

    # make a call and find the latest tweets
    params = {
        "screen_name": am,
        "count": 200,
        "exclude_replies": "false",
        "since_id": latest_id
    }
    new_tweets = api.query_get("statuses", "user_timeline", params)

    # add any new tweets to our set of tweets
    tweets.extend(new_tweets)
    # assume there's more
    more_tweets = True

    # find the latest tweet
    for tweet in tweets:
        if tweet["id"] > latest_id:
            latest_id = tweet["id"]

    while more_tweets:

        # make a call and find the latest tweets
        params = {
            "screen_name": am,
            "count": 200,
            "exclude_replies": "false",
            "since_id": latest_id
        }
        new_tweets = api.query_get("statuses", "user_timeline", params)

        # add any new tweets to our set of tweets

        for tweet in tweets: tweets.extend(new_tweets)

        current_latest = latest_id
        # find the latest tweet
        if tweet["id"] > latest_id:
            latest_id = tweet["id"]

        if current_latest == latest_id:
            more_tweets = False

    return tweets

def remove_duplicates(tweets):

    tweet_ids = []
    to_remove = []
    # go through all the tweets
    for tweet in tweets:
        # if we've already seen this tweet
        if tweet["id"] in tweet_ids:
            # add it to the list of tweets to remove
            to_remove.append(tweet)
        else:
            # otherwise add the ID to the list of tweets we've seen
            tweet_ids.append(tweet["id"])

    for tweet in to_remove:
        tweets.remove(tweet)

    return tweets


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Quick script allowing you to grab someones latest tweets')
    parser.add_argument('screen_name', help='Screen name to grab tweets of')
    args = parser.parse_args()

    ta = Twitter_API()
    cache = JSONFileCache()

    screen_name = args.screen_name

    print(screen_name)

    # get the list of tweets that have been downloaded, if it exists
    cache_file = "%s_tweets.json" % (screen_name)

    if cache.file_exists(cache_file):
        tweets = cache.get_json(cache_file)
    else:
        tweets = []

    print(len(tweets))

    if len(tweets) > 0:
        tweets = get_latest_tweets(ta, screen_name, tweets)
    else:
        tweets = get_tweet_history(ta, screen_name)

    print(len(tweets))

    tweets = remove_duplicates(tweets)

    print(len(tweets))

    cache.put_json(tweets, cache_file)

    text = ""
    for tweet in tweets:
        text += '%s\n' % tweet['text']

    cache.put_text(text, '%s_tweets.txt' % screen_name)

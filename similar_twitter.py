import json
import sys
import datetime
import re
import os
import time
from twitter import UserClient
import numpy as np
from time import sleep
import pandas as pd
from twitter_credentials import TwitterCredentials


class TwitterClient(object):
    def __init__(self):
        self._twitter_credentials = None
        self._client = None
        self._i = 0

    def get_user_client(self):
        self._twitter_credentials = TwitterCredentials(self._i % 4)
        self._client = UserClient(self._twitter_credentials.CONSUMER_KEY, self._twitter_credentials.CONSUMER_SECRET,
                                  self._twitter_credentials.ACCESS_TOKEN, self._twitter_credentials.ACCESS_TOKEN_SECRET)
        self._i += 1
        return self._client


def get_base_users_list(twitter_client):
    client = twitter_client.get_user_client()
    user_subs = []

    for user in users:
        print(user)
        sub = []

        next_cursor = -1

        while next_cursor != 0:
            while True:
                try:
                    response = client.api.lists.memberships.get(screen_name=user, count=1, cursor=next_cursor)
                    break
                except Exception as err:
                    print(err)
                    sleep(10)
                    client = twitter_client.get_user_client()

            next_cursor = response.data['next_cursor']
            sub.extend(response.data['lists'])

        user_subs.append(sub)

    return user_subs


def get_specifications_of_userlists(userSubs):
    # 0. "name": "Digital Marketing"
    # 1. "slug": "digital-marketing"
    # 2. "id": 49260625
    # 3. "full_name": "@pointcg/digital-marketing"
    # 4. "subscriber_count": 1
    # 5. "member_count": 46

    userLists = []

    for userSub in userSubs:
        ul = []
        for li in userSub:
            ul.append(
                (li['name'], li['slug'], str(li['id']), li['full_name'], li['subscriber_count'], li['member_count']))

        userLists.append(ul)

    print(userLists[0][5])

    return userLists


def find_common_lists(userLists):
    # commonLists = []

    # for li in userLists[0]:
    #    if li in userLists[1]:
    #        commonLists.append(li)

    commonLists = list(userLists[0])

    for cL in commonLists[:]:
        for uL in userLists[1:]:
            if cL not in uL:
                commonLists.remove(cL)
                break

    print("Number of common lists: " + str(len(commonLists)))

    return commonLists


def eliminate_common_lists(commonLists):
    commonLists = sorted(commonLists, key=lambda x: x[4], reverse=True)

    mostCommons = []

    totalMember = 0
    for li in commonLists:
        # List subscriber >= 0 and List member < 300
        if li[4] >= minSubscriber and li[5] < maxMember:
            totalMember = totalMember + li[5]
            mostCommons.append(li)

    df = pd.DataFrame(columns=('Name', 'Slug', 'ID', 'Fullname', 'Subscribers', 'Members'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(len(mostCommons)):
        df.loc[i] = mostCommons[i]

    print(df)

    print()
    print("Number of common lists after elimination: " + str(len(mostCommons)))
    print("Number of members in lists: " + str(totalMember))

    return mostCommons

def get_members_of_common_lists(mostCommons):

    keyInd = 1

    client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

    similarUsers = []

    for li in mostCommons:
        print(li)
        sims = []

        while (True):
            try:
                response = client.api.lists.members.get(list_id=li[2], count=1000, cursor=-1)
                break
            except Exception as err:
                print(err)
                sleep(15)
                keyInd = (keyInd + 1) % len(key)
                client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])
                # response = client.api.lists.members.get(list_id=li[2], count=1000, cursor=-1)

        ncur = response.data['next_cursor']
        for s in response.data['users']:
            sims.append(s)

        while (ncur != 0):
            while (True):
                try:
                    response = client.api.lists.members.get(list_id=li[2], count=1000, cursor=ncur)
                    break
                except Exception as err:
                    print(err)
                    sleep(15)
                    keyInd = (keyInd + 1) % len(key)
                    client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])
                    # response = client.api.lists.members.get(list_id=li[2], count=1000, cursor=ncur)

            ncur = response.data['next_cursor']
            for s in response.data['users']:
                sims.append(s)

        similarUsers.append(sims)

    return similarUsers


def extract_important_information_of_users(similarUsers):
    # 0. id_str				: ID of the user
    # 1. screen_name		: Screen name of the user (@screen_name)
    # 2. followers_count	: # Followers
    # 3. friends_count		: # Following
    # 4. favourites_count	: # Likes
    # 5. listed_count		: Total number of list subscription and membership (?)
    # 6. statuses_count		: # Tweets
    # 7. verified			: True or False
    # 8. protected			: True or False / if true can't crawl the account
    # 9. created_at			: Creation time of the account / (2009-10-30 12:11:39)

    similars = []
    uNames = []
    for sus in similarUsers:
        for su in sus:
            if su['screen_name'] not in uNames:
                uNames.append(su['screen_name'])
                similars.append((su['id_str'], su['screen_name'], su['followers_count'], su['friends_count'],
                                 su['favourites_count'], su['listed_count'], su['statuses_count'], su['verified'],
                                 su['protected'], su['created_at']))

    print("Number of unique users: " + str(len(similars)))

    return similars


def choose_not_humans(similars):
    sortedSimilars = sorted(similars, key=lambda x: x[2], reverse=True)

    chosens = []

    for s in sortedSimilars:
        if s[2] < minFollower:
            break
        if s[6] > minTweets and s[2] > s[3]:
            chosens.append(s)

    df = pd.DataFrame(columns=(
    'ID', 'Name', 'Followers', 'Friends', 'Favourites', 'Listed', 'Statuses', 'Verified', 'Protected', 'Created_at'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(20):
        df.loc[i] = chosens[i]

    print(len(chosens))
    print(df)

    return chosens


def next_function(similarUsers):
    goodLists = []
    badUsers = []
    badUsers = ['cnnbrk', 'nytimes', 'CNN', 'BBCBreaking', 'TheEconomist', 'BBCWorld', 'Reuters', 'FoxNews', 'TIME',
                'WSJ',
                'Forbes', 'ABC', 'HuffPost', 'washingtonpost']

    for i in range(len(similarUsers)):
        bad = False
        for su in similarUsers[i]:
            if su['screen_name'] in badUsers:
                bad = True
                break
        if not bad:
            goodLists.append(i)

    print("Number of remaining lists after elimination: " + str(len(goodLists)))
    # print(goodLists)

    return goodLists


def second_next_function(goodLists, similarUsers, mostCommons):
    similarUsers2 = []

    totalMember = 0

    for i in goodLists:
        if mostCommons[i][4] >= minSubscriber and mostCommons[i][5] < maxMember:
            totalMember = totalMember + mostCommons[i][5]
            similarUsers2.append(similarUsers[i])

    df = pd.DataFrame(columns=('Name', 'Slug', 'ID', 'Fullname', 'Subscribers', 'Members'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(len(goodLists)):
        if mostCommons[i][4] >= minSubscriber and mostCommons[i][5] < maxMember:
            df.loc[i] = mostCommons[goodLists[i]]

    print(df)

    print()
    print("Number of common lists after elimination: " + str(len(similarUsers2)))
    print("Number of members in lists: " + str(totalMember))

    return similarUsers2


def third_next_function(similarUsers2):
    # 0. id_str				: ID of the user
    # 1. screen_name		: Screen name of the user (@screen_name)
    # 2. followers_count	: # Followers
    # 3. friends_count		: # Following
    # 4. favourites_count	: # Likes
    # 5. listed_count		: Total number of list subscription and membership (?)
    # 6. statuses_count		: # Tweets
    # 7. verified			: True or False
    # 8. protected			: True or False / if true can't crawl the account
    # 9. created_at			: Creation time of the account / (2009-10-30 12:11:39)

    similars2 = []
    uNames2 = []
    for sus in similarUsers2:
        for su in sus:
            if su['screen_name'] not in uNames2:
                uNames2.append(su['screen_name'])
                similars2.append((su['id_str'], su['screen_name'], su['followers_count'], su['friends_count'],
                                  su['favourites_count'], su['listed_count'], su['statuses_count'], su['verified'],
                                  su['protected'], su['created_at']))

    print("Number of unique users: " + str(len(similars2)))

    return similars2


def last_similars(similars2):
    lastSimilars = []

    sortedSimilars2 = sorted(similars2, key=lambda x: x[2], reverse=True)

    f = open("SimilarUsers.txt", 'w', encoding='utf-8')

    f.write(users[0])
    for u in users[1:]:
        f.write("," + u)
    f.write("\n")

    for s in sortedSimilars2:
        if s[2] < minFollower:
            break
        if s[6] > minTweets and s[2] > s[3]:
            lastSimilars.append(s)
            f.write(
                s[0] + ',' + s[1] + ',' + str(s[2]) + ',' + str(s[3]) + ',' + str(s[4]) + ',' + str(s[5]) + ',' + str(
                    s[6])
                + ',' + str(s[7]) + ',' + str(s[8]) + ',' + str(s[9]))
            f.write("\n")

    f.close()

    print("Number of similar users: " + str(len(lastSimilars)))
    print()

    df = pd.DataFrame(columns=(
    'ID', 'Name', 'Followers', 'Friends', 'Favourites', 'Listed', 'Statuses', 'Verified', 'Protected', 'Created_at'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(20):
        df.loc[i] = lastSimilars[i]

    print(df)

    return last_similars


if __name__ == '__main__':

    twitter_client = TwitterClient()

    users = ['Tom_Slater_', 'IanDunt', 'georgeeaton', 'DavidLammy', 'ShippersUnbound', 'GuidoFawkes', 'OwenJones84',
             'bbclaurak']

    # List preferences
    minSubscriber = 0
    maxMember = 300

    # User preferences
    minFollower = 5000
    minTweets = 500

    get_base_users_list(twitter_client)

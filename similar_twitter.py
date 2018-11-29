import json
import os
from time import sleep
import pandas as pd
from twitter_credentials import TwitterClient


class EmptyApiResponse:
    def __init__(self):
        self.data = {}


def lists_memberships_get(client, screen_name, count, cursor):
    try_count = 1
    for i in range(try_count):
        try:
            response = client.api.lists.memberships.get(screen_name=screen_name, count=count, cursor=cursor)
            if response is None:
                return EmptyApiResponse()
            return response
        except Exception as err:
            print(err)
            sleep(10)
            client = twitter_client.get_user_client()

    print("Error {} times, moving to the next user.".format(try_count))
    return EmptyApiResponse()


def get_base_users_list(twitter_client, user_subs = {}):

    client = twitter_client.get_user_client()

    for user in users:

        if user in user_subs:
            continue

        print(user)
        sub = []

        next_cursor = -1

        while next_cursor != 0:
            response = lists_memberships_get(client, user, 250, next_cursor)
            if len(response.data) is 0:
                break
            else:
                next_cursor = response.data['next_cursor']
                sub.extend(response.data['lists'])

        if len(sub) is not 0:
            user_subs[user] = sub

    write_json_to_file(user_subs, os.path.join(data_folder, '1_user_subs.json'))

    return user_subs


def get_specifications_of_userlists(userSubs):
    # 0. "name": "Digital Marketing"
    # 1. "slug": "digital-marketing"
    # 2. "id": 49260625
    # 3. "full_name": "@pointcg/digital-marketing"
    # 4. "subscriber_count": 1
    # 5. "member_count": 46

    userLists = {}

    for user, userSub in userSubs.items():
        ul = []
        for li in userSub:
            ul.append(
                (li['name'], li['slug'], str(li['id']), li['full_name'], li['subscriber_count'], li['member_count']))

        userLists[user] = ul

    write_json_to_file(userLists, os.path.join(data_folder, '2_user_lists.json'))

    return userLists


def find_common_lists(userLists):

    userListsValues = [v for k,v in userLists.items()]

    commonLists = list(userListsValues[0])

    for cL in commonLists[:]:
        for uL in userListsValues[1:]:
            if cL not in uL:
                commonLists.remove(cL)
                break

    print("Number of common lists: " + str(len(commonLists)))

    write_json_to_file(commonLists, os.path.join(data_folder, "3_common_lists.json"))

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

    write_json_to_file(mostCommons, os.path.join(data_folder, "4_most_commons.json"))

    return mostCommons


def lists_members_get(client, list_id, count, cursor):
    try_count = 1
    for i in range(try_count):
        try:
            response = client.api.lists.members.get(list_id=list_id, count=count, cursor=cursor)
            if response is None:
                return EmptyApiResponse()
            return response
        except Exception as err:
            print(err)
            sleep(10)
            client = twitter_client.get_user_client()

    print("Error {} times, moving to the next user.".format(try_count))
    return EmptyApiResponse()


def get_members_of_common_lists(mostCommons, similarUsers = {}):

    client = twitter_client.get_user_client()

    for li in mostCommons:

        if li[2] in similarUsers:
            continue

        print(li)
        sims = []

        next_cursor = -1

        while next_cursor != 0:
            response = lists_members_get(client, li[2], 1000, next_cursor)
            if len(response.data) is 0:
                break
            else:
                next_cursor = response.data['next_cursor']
                sims.extend(response.data['users'])

        if len(sims) is not 0:
            similarUsers[li[2]] = sims

    write_json_to_file(similarUsers, os.path.join(data_folder, '5_similar_users.json'))
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
    for li, sus in similarUsers.items():
        for su in sus:
            if su['screen_name'] not in uNames:
                uNames.append(su['screen_name'])
                similars.append((su['id_str'], su['screen_name'], su['followers_count'], su['friends_count'],
                                 su['favourites_count'], su['listed_count'], su['statuses_count'], su['verified'],
                                 su['protected'], su['created_at']))

    print("Number of unique users: " + str(len(similars)))

    write_json_to_file(similars, os.path.join(data_folder, '6_similars.json'))

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

    write_json_to_file(chosens, os.path.join(data_folder, '7_chosens.json'))

    return chosens


def eliminate_bad_users(similarUsers):
    goodLists = []
    badUsers = ['cnnbrk', 'nytimes', 'CNN', 'BBCBreaking', 'TheEconomist', 'BBCWorld', 'Reuters', 'FoxNews', 'TIME',
                'WSJ', 'Forbes', 'ABC', 'HuffPost', 'washingtonpost']

    similarUsersValues = [v for k, v in similarUsers.items()]
    for i in range(len(similarUsersValues)):
        bad = False
        for su in similarUsersValues[i]:
            if su['screen_name'] in badUsers:
                bad = True
                break
        if not bad:
            goodLists.append(i)

    print("Number of remaining lists after elimination: " + str(len(goodLists)))

    write_json_to_file(goodLists, os.path.join(data_folder, '8_good_lists.json'))

    return goodLists


def eliminate_lists_with_company_acounts(goodLists, similarUsers, mostCommons):
    similarUsers2 = []

    totalMember = 0
    similarUsersValues = [v for k, v in similarUsers.items()]
    for i in goodLists:
        if mostCommons[i][4] >= minSubscriber and mostCommons[i][5] < maxMember:
            totalMember = totalMember + mostCommons[i][5]
            similarUsers2.append(similarUsersValues[i])

    df = pd.DataFrame(columns=('Name', 'Slug', 'ID', 'Fullname', 'Subscribers', 'Members'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(len(goodLists)):
        if mostCommons[i][4] >= minSubscriber and mostCommons[i][5] < maxMember:
            df.loc[i] = mostCommons[goodLists[i]]

    print(df)

    print()
    print("Number of common lists after elimination: " + str(len(similarUsers2)))
    print("Number of members in lists: " + str(totalMember))

    write_json_to_file(similarUsers2, os.path.join(data_folder, '9_similar_users_2.json'))

    return similarUsers2


def get_remaining_similars(similarUsers2):
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

    write_json_to_file(similars2, os.path.join(data_folder, '10_similars_2.json'))

    return similars2


def get_last_similars(similars2):
    lastSimilars = []

    sortedSimilars2 = sorted(similars2, key=lambda x: x[2], reverse=True)

    for s in sortedSimilars2:
        if s[2] < minFollower:
            break
        if s[6] > minTweets and s[2] > s[3]:
            lastSimilars.append(s)

    print("Number of similar users: " + str(len(lastSimilars)))
    print()

    df = pd.DataFrame(columns=(
    'ID', 'Name', 'Followers', 'Friends', 'Favourites', 'Listed', 'Statuses', 'Verified', 'Protected', 'Created_at'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(20):
        df.loc[i] = lastSimilars[i]

    print(df)

    write_json_to_file(lastSimilars, os.path.join(data_folder, '11_last_similars.json'))

    return lastSimilars


def get_user_timelines(twitter_client, last_similars):
    userSubsDir = './user_subs'
    if not os.path.exists(userSubsDir):
        os.mkdir(userSubsDir)

    client = twitter_client.get_user_client()
    user_subs = []

    for user in users:
        print(user)
        sub = []

        next_cursor = -1

        while next_cursor != 0:
            while True:
                try:
                    response = client.api.lists.memberships.get(screen_name=user, count=250, cursor=next_cursor)
                    response2 = client.api.statuses.user_timeline.get(screen_name="realDonaldTrump", count=20, cursor=-1)
                    break
                except Exception as err:
                    print(err)
                    sleep(10)
                    client = twitter_client.get_user_client()

            next_cursor = response.data['next_cursor']
            sub.extend(response.data['lists'])

        with open('{}/{}.json'.format(userSubsDir, user), 'w') as outfile:
            json.dump(sub, outfile)

        user_subs.append(sub)

    return user_subs


def load_json_from_file(file_path):
    with open(file_path, 'r') as infile:
        res = json.load(infile)
    return res


def write_json_to_file(content, file_path, indent=4):
    with open(file_path, 'w', encoding="utf-8") as sw:
        sw.write(json.dumps(content, indent=indent, sort_keys=False))


def write_all_lines(file_path, lines, file_format="utf-8"):
    with open(file_path, 'w', encoding=file_format) as sw:
        for line in lines:
            sw.write("{}\n".format(line))


def create_dir_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)


if __name__ == '__main__':

    twitter_client = TwitterClient()

    users = ['Tom_Slater_', 'IanDunt', 'georgeeaton', 'DavidLammy', 'ShippersUnbound', 'GuidoFawkes', 'OwenJones84', 'bbclaurak']
    users = ['thegrugq', 'SwiftOnSecurity', 'pwnallthethings', 'josephfcox', 'mikko']

    data_folder = "./cyber_security"
    create_dir_if_not_exist(data_folder)

    # List preferences
    minSubscriber = 0
    maxMember = 300

    # User preferences
    minFollower = 5000
    minTweets = 500

    # user_subs = get_base_users_list(twitter_client)
    user_subs = load_json_from_file(os.path.join(data_folder, '1_user_subs.json'))

    user_lists = get_specifications_of_userlists(userSubs=user_subs)
    common_lists = find_common_lists(userLists=user_lists)
    most_commons = eliminate_common_lists(commonLists=common_lists)

    similar_users = get_members_of_common_lists(mostCommons=most_commons)
    # similar_users = load_json_from_file(os.path.join(data_folder, '5_similar_users.json'))

    similars = extract_important_information_of_users(similarUsers=similar_users)
    chosens = choose_not_humans(similars=similars)
    good_lists = eliminate_bad_users(similarUsers=similar_users)
    similar_users_2 = eliminate_lists_with_company_acounts(goodLists=good_lists,similarUsers=similar_users, mostCommons=most_commons)
    similars_2 = get_remaining_similars(similarUsers2=similar_users_2)
    last_similars = get_last_similars(similars2=similars_2)

    print()

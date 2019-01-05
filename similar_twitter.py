import json
import os
from time import sleep
from twitter_api_client import TwitterClient


def get_base_users_list(users, user_subs_path, user_subs = {}):
    for user in users:

        if user in user_subs:
            continue

        print(user)
        sub = []

        next_cursor = -1

        while next_cursor != 0:
            response = twitter_client.lists_memberships_get(user, 250, next_cursor)
            if len(response.data) is 0:
                break
            else:
                next_cursor = response.data['next_cursor']
                sub.extend(response.data['lists'])

        if len(sub) is not 0:
            user_subs[user] = sub

    write_json_to_file(user_subs, user_subs_path)
    return user_subs


def get_specifications_of_userlists(userSubs, user_lists_path):
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

    write_json_to_file(userLists, user_lists_path)
    return userLists


def find_common_lists(userLists, common_lists_path):

    userListsValues = [v for k,v in userLists.items()]

    commonLists = list(userListsValues[0])

    for cL in commonLists[:]:
        for uL in userListsValues[1:]:
            if cL not in uL:
                commonLists.remove(cL)
                break

    print("Number of common lists: " + str(len(commonLists)))

    write_json_to_file(commonLists, common_lists_path)
    return commonLists


def eliminate_common_lists(commonLists, most_commons_path):
    commonLists = sorted(commonLists, key=lambda x: x[4], reverse=True)

    mostCommons = []

    totalMember = 0
    for li in commonLists:
        # List subscriber >= 0 and List member < 300
        if li[4] >= minSubscriber and li[5] < maxMember:
            totalMember = totalMember + li[5]
            mostCommons.append(li)

    print("Number of common lists after elimination: " + str(len(mostCommons)))
    print("Number of members in lists: " + str(totalMember))

    write_json_to_file(mostCommons, most_commons_path)
    return mostCommons


def get_members_of_common_lists(mostCommons, similar_users_path, similarUsers = {}):

    for li in mostCommons:

        if li[2] in similarUsers:
            continue

        print(li)
        sims = []

        next_cursor = -1

        while next_cursor != 0:
            response = twitter_client.lists_members_get(li[2], 1000, next_cursor)
            if len(response.data) is 0:
                break
            else:
                next_cursor = response.data['next_cursor']
                sims.extend(response.data['users'])

        if len(sims) is not 0:
            similarUsers[li[2]] = sims

    write_json_to_file(similarUsers, similar_users_path)
    return similarUsers


def eliminate_bad_users(similarUsers, similar_users_2_path):
    badUsers = ['cnnbrk', 'nytimes', 'CNN', 'BBCBreaking', 'TheEconomist', 'BBCWorld', 'Reuters', 'FoxNews', 'TIME',
                'WSJ', 'Forbes', 'ABC', 'HuffPost', 'washingtonpost']

    print("Total number of members in lists before elimination: {}".format(sum([len(v) for k, v in similarUsers.items()])))

    similarUsers2 = {}
    for k, similarUser in similarUsers.items():
        similarUser2 = []
        for su in similarUser:
            if su['screen_name'] not in badUsers:
                similarUser2.append(su)
        similarUsers2[k] = similarUser2

    print("Total number of members in lists before elimination: {}".format(sum([len(v) for k, v in similarUsers2.items()])))

    write_json_to_file(similarUsers2, similar_users_2_path)
    return similarUsers2


def get_specifications_of_remaining_users(similarUsers2, similars_path):
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
    uNames2 = []
    for k, sus in similarUsers2.items():
        for su in sus:
            if su['screen_name'] not in uNames2:
                uNames2.append(su['screen_name'])
                similars.append((su['id_str'], su['screen_name'], su['followers_count'], su['friends_count'],
                                  su['favourites_count'], su['listed_count'], su['statuses_count'], su['verified'],
                                  su['protected'], su['created_at']))

    print("Number of unique users: " + str(len(similars)))

    write_json_to_file(similars, similars_path)
    return similars


def eliminate_remaining_users(similars, last_similars_path):
    lastSimilars = []

    sortedSimilars2 = sorted(similars, key=lambda x: x[2], reverse=True)

    for s in sortedSimilars2:
        if s[2] < minFollower:
            break
        if s[6] > minTweets and s[2] > s[3]:
            lastSimilars.append(s)

    print("Number of similar users: " + str(len(lastSimilars)))

    write_json_to_file(last_similars, last_similars_path)
    return lastSimilars


def get_user_timelines(last_similars, user_timelines_path, user_timelines = {}, no_tweets = 2):
    for user in last_similars:
        print(user)
        user_id = user[1]

        if user_id in user_timelines:
            user_timeline = user_timelines[user_id]
        else:
            user_timeline = {}

        while len(user_timeline) < no_tweets:
            response = twitter_client.statuses_user_timeline_get(user_id, 2)
            if len(response.data) is 0:
                break
            else:
                for d in response.data:
                    if d['id_str'] not in user_timeline:
                        user_timeline[d['id_str']] = d['full_text']

        if len(user_timeline) is not 0:
            user_timelines[user_id] = user_timeline

    write_json_to_file(user_timelines, user_timelines_path)
    return user_timelines


def load_json_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as infile:
            res = json.load(infile)
    else:
       res = {}
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

    data_folder = "./politics"
    create_dir_if_not_exist(data_folder)

    # List preferences
    minSubscriber = 0
    maxMember = 300

    # User preferences
    minFollower = 5000
    minTweets = 500

    user_subs_path = os.path.join(data_folder, '1_user_subs.json')
    user_lists_path = os.path.join(data_folder, '2_user_lists.json')
    common_lists_path = os.path.join(data_folder, '3_common_lists.json')
    most_commons_path = os.path.join(data_folder, '4_most_commons.json')
    similar_users_path = os.path.join(data_folder, '5_similar_users.json')
    similar_users_2_path = os.path.join(data_folder, '6_similar_users_2.json')
    similars_path = os.path.join(data_folder, '7_similars_2.json')
    last_similars_path = os.path.join(data_folder, '8_last_similars.json')
    user_timelines_path = os.path.join(data_folder, '9_user_timelines.json')

    # user_subs = get_base_users_list(users, user_subs_path)
    # user_subs = load_json_from_file(user_subs_path)
    #
    # user_lists = get_specifications_of_userlists(user_subs, user_lists_path)
    # user_lists = load_json_from_file(user_lists_path)
    #
    # common_lists = find_common_lists(user_lists, common_lists_path)
    # common_lists = load_json_from_file(common_lists_path)
    #
    # most_commons = eliminate_common_lists(common_lists, most_commons_path)
    # most_commons = load_json_from_file(most_commons_path)
    #
    # similar_users = get_members_of_common_lists(most_commons, similar_users_path)
    # similar_users = load_json_from_file(similar_users_path)
    #
    # similar_users_2 = eliminate_bad_users(similar_users, similar_users_2_path)
    # similar_users_2 = load_json_from_file(similar_users_2_path)
    #
    # similars = get_specifications_of_remaining_users(similar_users_2, similars_path)
    # similars = load_json_from_file(similars_path)
    #
    # last_similars = eliminate_remaining_users(similars, last_similars_path)
    last_similars = load_json_from_file(last_similars_path)

    user_timelines = get_user_timelines(last_similars, user_timelines_path, load_json_from_file(user_timelines_path), no_tweets=2)
    user_timelines = load_json_from_file(user_timelines_path)

    print()

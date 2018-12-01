import pandas as pd

def most_commons_to_data(mostCommons):
    df = pd.DataFrame(columns=('Name', 'Slug', 'ID', 'Fullname', 'Subscribers', 'Members'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(len(mostCommons)):
        df.loc[i] = mostCommons[i]
    return df


def chosens_to_data(chosens):
    df = pd.DataFrame(columns=(
    'ID', 'Name', 'Followers', 'Friends', 'Favourites', 'Listed', 'Statuses', 'Verified', 'Protected', 'Created_at'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(20):
        df.loc[i] = chosens[i]
    return df


def similar_users_2_to_data(goodLists, mostCommons, minSubscriber, maxMember):
    df = pd.DataFrame(columns=('Name', 'Slug', 'ID', 'Fullname', 'Subscribers', 'Members'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(len(goodLists)):
        if mostCommons[i][4] >= minSubscriber and mostCommons[i][5] < maxMember:
            df.loc[i] = mostCommons[goodLists[i]]
    return df

def last_similars_to_data(lastSimilars):
    df = pd.DataFrame(columns=(
    'ID', 'Name', 'Followers', 'Friends', 'Favourites', 'Listed', 'Statuses', 'Verified', 'Protected', 'Created_at'))
    pd.options.display.float_format = '{:,.0f}'.format
    for i in range(20):
        df.loc[i] = lastSimilars[i]
    return df
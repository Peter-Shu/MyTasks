import os
import tweepy as tw
import pandas as pd
import os.path
import csv
import pyodbc
#connect to mssql
conn = pyodbc.connect(r'Driver={ODBC Driver 17 for SQL Server};'
                      r'Server=localhost;'
                      r'Database=twitter;'
                      r'Trusted_Connection=yes;')

consumer_key= 'ng8ANOG9HJRnrvWF7RIBjICZq'
consumer_secret= 'PWMScfPqFCwVfF69uCfnwSuWRk3nVzYO6AloivFhKmZfcR5bjP'
access_token= '1377965772748681216-bLe3WbOUsKEIXqOVTIF0Qv2S7TFUN6'
access_token_secret= 'XOBqXe7u7SUux27bRstFln3NwsNybkLiyxTQzP4vxJbMy'
# Get authorization from Twitter API
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth)
#check if dulipcate, empty data then delete 
def check_data(file_name):
    df = pd.read_csv(file_name, engine='python')
    try:
        df.drop_duplicates(subset='screen_name', keep='last', inplace=True) #keep the lastest data, screenname
    except:
        df.drop_duplicates(subset='tweet_id', keep='last', inplace=True)
    df.fillna("None",inplace=True)                                      #fill in empty data
    df.to_csv(file_name, index=False)
    del df                                                            #clear dataframe for reuse

# Search for someone profile by user's screen name or ID
def profile_func():    
    db_p = pd.DataFrame(columns=['screen_name', 'username', 'followers_count', 
                                'favourites_count', 'friends_count','description'])
    profile_list=[]
    # Get the screen name and check for any errors
    user_screen_name = input("Please Enter Twitter user's screen name or ID : ")
    user_screen_name = user_screen_name.replace(' ', '') #clear space
    try :
        user_detail = api.get_user(user_screen_name)
    except :
        print ("There are other Errors in your input")
        return
    # Get the details of the user
    user_name = user_detail.name
    user_followers_count = user_detail.followers_count
    user_favourites_count = user_detail.favourites_count
    user_friends_count = user_detail.friends_count
    user_description = user_detail.description
    # Put into dataframe and make a .csv file for user
    profile_list = [user_screen_name, user_name, user_followers_count, 
                                user_favourites_count, user_friends_count, user_description]
    db_p.loc[len(db_p)] = profile_list
    #create file if not exist
    if os.path.isfile('profile.csv'):
        db_p.to_csv('profile.csv', mode='a',index = False, header = False)
    else:
        db_p.to_csv('profile.csv',index = False)
    #Data checking
    check_data('profile.csv')
    #Store profile.csv into SQL
    cursor = conn.cursor()
    profile_data = pd.read_csv('profile.csv')
    try:
        cursor.execute('Create table profile(screen_name CHAR(20),username VARCHAR(50),followers_count INT, favourites_count INT, friends_count INT, description VARCHAR(350))')
        conn.commit()
    except:
        cursor.execute('DELETE FROM dbo.profile')
    for index,row in profile_data.iterrows():
        cursor.execute('INSERT INTO dbo.profile([screen_name],[username],[followers_count],[favourites_count],[friends_count],[description]) values (?,?,?,?,?,?)', 
                    row['screen_name'], 
                    row['username'], 
                    row['followers_count'],
                    row['favourites_count'],
                    row['friends_count'],
                    row['description'])
    conn.commit()
    cursor.close()
    print(f""" 
User Name: {user_name}
Followers: {user_followers_count}
The number of tweets that {user_name} has marked as favorite:{user_favourites_count}
Friends: {user_friends_count}
Desciption: {user_description}""")
    return ("Finish searching !")

# Get the social network information of someone
def social_network_func():
    db_s = pd.DataFrame(columns=['screen_name', 'username', 'followers_list', 
                                 'friends_list'])
    socialInfo=[]
    # Get the screen name and check for any errors
    user_screen_name = input("Please Enter Twitter user's screen name or ID : ")
    user_screen_name = user_screen_name.replace(' ', '')
    user_followers = []
    user_friends = []
    try :
        user_detail = api.get_user(user_screen_name)
    except :
        print ("There are some Errors in your input")
        return
    # Get the information(followers, friends)
    user_name = user_detail.name
    user_followers_count = user_detail.followers_count
    user_friends_count = user_detail.friends_count
    print(f"""
    {user_name} has {user_followers_count} follwers and {user_friends_count} friends. """)
    print("-------------------------\nFirst 30 Followers in the list:")
    for follower in tw.Cursor(api.followers, user_screen_name).items(30):
        user_followers.append(follower.screen_name)
        print(follower.screen_name)
    print("-------------------------\nFirst 30 Friends int the list: ")
    for friend in tw.Cursor(api.friends, user_screen_name).items(30):
        user_friends.append(friend.screen_name)
        print(friend.screen_name)
    #put the data into socailInfo.csv
    socialInfo_list = [user_screen_name, user_name , user_followers, user_friends]
    db_s.loc[len(db_s)] = socialInfo_list
    #create file if not exist
    if os.path.isfile('socialInfo.csv'):
        db_s.to_csv('socialInfo.csv', mode='a',index = False, header = False)
    else:
        db_s.to_csv('socialInfo.csv',index = False)
    check_data('socialInfo.csv')
    # insert data into mssql
    cursor = conn.cursor()
    socialInfo = pd.read_csv('socialInfo.csv')
    try:
        cursor.execute('Create table socialInfo(screen_name CHAR(20),username VARCHAR(50), followers_list VARCHAR(MAX), friends_list VARCHAR(MAX))')
        conn.commit()
    except:
        cursor.execute('DELETE FROM dbo.socialInfo')
    for index,row in socialInfo.iterrows():
        cursor.execute('INSERT INTO dbo.socialInfo([screen_name],[username],[followers_list], [friends_list]) values (?,?,?,?)', 
                    row['screen_name'], 
                    row['username'], 
                    row['followers_list'],
                    row['friends_list'])
    conn.commit()
    cursor.close()
    
# Search keyword function
def keyword_func():
    db = pd.DataFrame(columns=['screenName', 'keyword', 'tweet_id', 'location', #columns of .csv
                                'created_at','favorite_count', 'totaltweets',
                                'retweetcount', 'text', 'hashtags'])
    tweets_list = []
    tweet_count = 1                                                                 #show no. of tweet received, max20
    no_HT = 1                                                                       #count no. of keyword
    #Ask for keyword
    print('You are searching Latest 200 Tweets with Keyword !')
    keyword = input('Please enter a keyword: ')
    while len(keyword)< 500:                                                     #check search query< limit, then add more keywords
        two_keyword = input('Search tweet with more keyword?(Y/N)')
        if   (two_keyword.upper() == 'Y'):
            keyword2 = input('Please enter other keyword: ')
            keyword += "+"+keyword2
            no_HT += 1
        elif (two_keyword.upper() == 'N'): 
            print(f'Searching Tweets with {no_HT} keyword...')
            break
        else: print('Invalid Input!')
    else: return print("Over keyword limit!")
    # Get 200 tweets
    for tweet in tw.Cursor(api.search, q=keyword, lang='en').items(200):
        tweets_list.append(tweet)
    # Put tweet into list then into dataframe for 200 times
    for tweet in tweets_list:
        screename = tweet.user.screen_name
        tweet_id = tweet.id
        location = tweet.user.location
        created_at = tweet.created_at
        favorite_count = tweet.favorite_count
        totaltweets = tweet.user.statuses_count
        retweetcount = tweet.retweet_count
        hashtags = tweet.entities['hashtags']
        text = tweet.text
        hashtext = list()
        for j in range(0, len(hashtags)):
            hashtext.append(hashtags[j]['text'])
        # Tweet into dataframe
        n_tweet = [screename, keyword, tweet_id, location,
                    created_at, favorite_count, totaltweets,
                     retweetcount, text, hashtext]
        db.loc[len(db)] = n_tweet
        print(f"""
Tweet {tweet_count}:
Username:{n_tweet[0]}
Tweet_id:{n_tweet[2]}
Location:{n_tweet[3]}
Created at:{n_tweet[4]}
Favorite Count:{n_tweet[5]}
Total Tweets:{n_tweet[6]}
Retweet Count:{n_tweet[7]}
Tweet Text:{n_tweet[8]}
Hashtags Used:{n_tweet[9]}""")

        tweet_count +=1
    #create if not exist then put data
    if os.path.isfile('result.csv'):
        db.to_csv('result.csv', mode='a',index = False, header = False)
    else:
        db.to_csv('result.csv',index = False)
    #data checking
    check_data('result.csv')
    #store into database
    cursor = conn.cursor()
    result_data = pd.read_csv('result.csv')
    try:
        cursor.execute('Create table result(screenName CHAR(20),keyword VARCHAR(300),tweet_id VARCHAR(255), location VARCHAR(200), created_at VARCHAR(255), favorite_count INT, totaltweets INT, retweetcount INT, text VARCHAR(300), hashtags VARCHAR(255))')
        conn.commit()
    except:
        cursor.execute('DELETE FROM dbo.result')
    for index,row in result_data.iterrows():
        cursor.execute('INSERT INTO dbo.result([screenName],[keyword],[tweet_id],[location],[created_at],[favorite_count],[totaltweets],[retweetcount],[text],[hashtags]) values (?,?,?,?,?,?,?,?,?,?)', 
                    row['screenName'], 
                    row['keyword'], 
                    row['tweet_id'],
                    row['location'],
                    row['created_at'],
                    row['favorite_count'],
                    row['totaltweets'],
                    row['retweetcount'],
                    row['text'],
                    row['hashtags']
                    )
    conn.commit()
    cursor.close()

# Menu
def main():
    print("Welcome to collect Twitter's data!")
    while True:
        print(f'''
You can choose 4 functions:
1. collecting the user's profile information
2. collecting the user's social network information
3. collecting the tweets using the keywords
4. exit the program
Please input 1-4 to choose the function''')
        a = input('->')
        if   (a=='1'):
            profile_func()
        elif (a=='2'):
            social_network_func()
        elif (a=='3'):
            keyword_func()
        elif (a=='4'):
            print('Thank you for using the program! Peace!')
            conn.close()
            quit()
        else: print('Invalid Input!')
if __name__ == "__main__":
    main()

import os
import tweepy as tw
import pandas as pd

consumer_key= 'ng8ANOG9HJRnrvWF7RIBjICZq'
consumer_secret= 'PWMScfPqFCwVfF69uCfnwSuWRk3nVzYO6AloivFhKmZfcR5bjP'
access_token= '1377965772748681216-bLe3WbOUsKEIXqOVTIF0Qv2S7TFUN6'
access_token_secret= 'XOBqXe7u7SUux27bRstFln3NwsNybkLiyxTQzP4vxJbMy'
# Get authorization from Twitter API
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth)

# Search for someone profile by user's screen name or ID
def profile_func():    
    # Get the screen name and check for any errors
    user_screen_name = input("Please Enter Twitter user's screen name or ID : ")
    user_screen_name = user_screen_name.replace(' ', '')
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
    print(f""" 
User Name: {user_name}
Followers: {user_followers_count}
The number of tweets that {user_name} has marked as favorite:{user_favourites_count}
Friends: {user_friends_count}
Desciption: {user_description}""")
    return ("Finish searching !")
# Get the social network information of someone
def social_network_func():
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
    # Get the information
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
# Search keyword function
def keyword_func():
    db = pd.DataFrame(columns=['screename', 'description', 'location', 
                                'following','followers', 'totaltweets',
                                'retweetcount', 'text', 'hashtags'])
    tweets_list = []
    tweet_count = 1
    no_HT = 1
    #Ask for keyword
    print('You are searching Latest 20 Tweets with Keyword !')
    keyword = input('Please enter a keyword: ')
    while True:
        two_keyword = input('Search tweet with more keyword?(Y/N)')
        if   (two_keyword.upper() == 'Y'):
            keyword2 = input('Please enter other keyword: ')
            keyword += "+"+keyword2
            no_HT += 1
        elif (two_keyword.upper() == 'N'): 
            print(f'Searching Tweets with {no_HT} keyword...')
            break
        else: print('Invalid Input!')
    # Get 20 tweets
    for tweet in tw.Cursor(api.search, q=keyword).items(20):
        tweets_list.append(tweet)
    # Put tweet into list for 20 times
    for tweet in tweets_list:
        screename = tweet.user.screen_name
        description = tweet.user.description
        location = tweet.user.location
        following = tweet.user.friends_count
        followers = tweet.user.followers_count
        totaltweets = tweet.user.statuses_count
        retweetcount = tweet.retweet_count
        hashtags = tweet.entities['hashtags']
        text = tweet.text
        hashtext = list()
        for j in range(0, len(hashtags)):
            hashtext.append(hashtags[j]['text'])
        # Tweet into dataframe
        n_tweet = [screename, description, location,
                    following, followers, totaltweets,
                     retweetcount, text, hashtext]
        db.loc[len(db)] = n_tweet
          
        print(f"""
Tweet {tweet_count}:
Username:{n_tweet[0]}
Description:{n_tweet[1]}
Location:{n_tweet[2]}
Following Count:{n_tweet[3]}
Follower Count:{n_tweet[4]}
Total Tweets:{n_tweet[5]}
Retweet Count:{n_tweet[6]}
Tweet Text:{n_tweet[7]}
Hashtags Used:{n_tweet[8]}""")

        tweet_count +=1
    #Add into .csv file
    filename = 'result_'+keyword.lower()+'.csv'
    db.to_csv(filename)

# Menu
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
        quit()
    else: print('Invalid Input!')
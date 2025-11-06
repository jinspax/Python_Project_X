import tweepy
import csv
import configparser
import datetime
from datetime import date
from enum import Enum

#Read the file
config = configparser.ConfigParser()
fp = config['Twitter']['LOG_FILE']

class TweetType(Enum):
    Post = 1
    Reply = 2
    Quote = 3
    
def writeToCsv(text):
    print(f"Saving the text '{text}' to csv")
    try:
        with open(fp, 'a', encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(text)
    except FileNotFoundError:
        pass

class MyTweet:
    def __init__(
        self,
        datePosted: date,
        tweetType: TweetType.Post,
        tweetText: str,
        
        initialUserChategory: str,  # moved before defaults
        views: int = 0,
        characterization: str = "",
        userName: str = "https://x.com/",
        tweetUrl: str = "",
        negativeCharacterization: str = "",
        initialText: str = "",
        initialUserUrl: str = "https://x.com/"
    ):
        self.datePosted = datePosted
        self.tweetType = tweetType
        self.tweetText = tweetText
        self.userName = userName
        self.views = views
        self.initialUserChategory = initialUserChategory
        self.characterization = characterization
        self.tweetUrl = tweetUrl
        self.negativeCharacterization = negativeCharacterization
        self.initialText = initialText
        self.initialUserUrl = initialUserUrl
   

class Listener(tweepy.StreamingClient):
    
    def on_connect(self):
        print("Connected Waiting for tweets...")
    
    def on_closed(self, response):
        print(response)
        print("Connection closed...")
        
    def on_tweet(self, tweet):
        print(f"🕊️ @{tweet.author_id}: {tweet.text}\n")
        ## DATE/TYPE--/TEXT/URL/VIEWS/CHARACTERIZATION.../URL/CHARACTERIZATION_NEGATIVE/TEXT_OF_INITIAL_POST/INITIAL_USERS/INITIAL_URL
        #Determine tweet type
        tw = MyTweet()
        
        tw.datePosted = datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S %z %Y").strftime("%d/%m/%Y")
        if (tweet.truncated==True):
            tw.tweetText = "..."
        else:
            tw.tweetText = tweet.text
            
        if hasattr(tweet,"referenced_tweets"):
            for ref in tweet.referenced_tweets:
                if ref["type"] == "replied_to":
                    tw.tweetType = TweetType.Reply
                elif ref["type"] == "quoted":
                    tw.tweetType = TweetType.Quote
                         
        #Get author username
        if hasattr(tweet,"user"):
            tw.userName += tweet.user.screen_name
        else:
            tw.userName += self.client.get_user(id=tweet.author_id)
        
        #Views
        tw.views = 0
        
        #Characterization EMPTY
        
        #URL - Note the username is already a link!!
        tw.URL = f"{tw.userName}/status/{tweet.id}"
        
        #Characterization Negative EMPTY
        
        #Initial post text
        
        #Initail User screen name
        
        tw.initialUserUrl += f"https://x.com/{tweet.in_reply_to_screen_name}"
        
        
def main():
    #read credentials
    config.read('config.ini')
    
    #read rules
    rules = config['Twitter']['KEYWORD_RULE']
    
    #authentication
    bearer_token = config['Twitter']['BEARER_TOKEN']
    xclient = tweepy.Client(bearer_token)
    
    

    print(type(xclient))
    # Prepare the CSV file with headers (once)
    try:
        with open(fp, "x", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ΗΜΕΡΟΜΗΝΙΑ", "ΚΑΤΗΓΟΡΙΑ", "ΑΝΑΦΟΡΑ", "ΧΡΗΣΤΗΣ",
                "ΑΠΗΧΗΣΗ", "ΧΑΡΑΚΤΗΡΙΣΜΟΣ", "ΣΥΝΔΕΣΜΟΣ",
                "ΧΑΡΑΚΤΗΡΙΣΜΟΣ ΑΡΝΗΤΙΚΟΥ", "ΑΡΧΙΚΗ ΔΗΜΟΣΙΕΥΣΗ",
                "ΧΡΗΣΤΕΣ ΑΡΧΙΚΗΣ ΔΗΜΟΣΙΕΥΣΗΣ", "ΠΡΟΕΛΕΥΣΗ ΑΡΧΙΚΗΣ ΔΗΜΟΣΙΕΥΣΗΣ"
            ])
    except FileExistsError:
        pass
    
    
    
    
    
    
    
    
if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
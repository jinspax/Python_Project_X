import tweepy
import csv
import time
from datetime import datetime

KEYWORD_RULE = '("MyKeyWord" OR "Dendias")'
LOG_FILE = "mentions_log.csv"


BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAK7I5AEAAAAAtc5G3oYOOy%2F9o46VG%2BkGayQDBnM%3DU3aVESbzveE7A81e66Zn9SDkbS7NPIVI4YpJDJpRsExzxV2wJC"
ACCESS_TOKEN = "1514609709612892166-nUieT8LaxhhI8mLiocfyntPRiJoAmu"
ACCESS_TOKEN_SECRET = "IflYQTAbLhDndQMHvBTl1XLXgUQIhjV6mgFW5xZ8sTrsO"
API_KEY = "fZ724JtAIHFQhg95PQzJagCQv"
API_KEY_SECRET = "8j83DCxq8Ge1EwPfd6v0syJ9m8IEKuA4GvabFzktIdPe9ckLrn"


# === TWEET CLIENT (optional direct API usage) ===
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)


# === STREAM CLASS ===
class KeywordStream(tweepy.StreamingClient):
    """Stream that saves matching tweets and reconnects if needed."""

    

    def on_connect(self):
        print(f"[{datetime.now()}] ✅ Connected to X Stream API.")

    def on_tweet(self, tweet):
        """Triggered when a new tweet arrives."""

        print(f"🆕 New tweet at {tweet.created_at}:\n{tweet.text}\n")

        # Default placeholders for CSV columns
        original_text = ""
        original_users = ""
        original_source = ""

        # Determine tweet type
        tweet_type = "Post"
        if hasattr(tweet, "referenced_tweets"):
            for ref in tweet.referenced_tweets:
                if ref["type"] == "replied_to":
                    tweet_type = "Reply"
                elif ref["type"] == "quoted":
                    tweet_type = "Quote"

        # Get author username (via API call — guaranteed result)
        try:
            user = self.client.get_user(id=tweet.author_id)
            username = user.data.username
        except Exception as e:
            print(f"⚠️ Could not fetch username: {e}")
            username = str(tweet.author_id)

        # Tweet URL
        tweet_url = f"https://x.com/{username}/status/{tweet.id}"

        # Engagement metric (placeholder)
        engagement = 0
        if hasattr(tweet, "public_metrics"):
            metrics = tweet.public_metrics
            engagement = metrics.get("like_count", 0) + metrics.get("retweet_count", 0)

        # Append to CSV
        with open(LOG_FILE, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                tweet.created_at,                   # ΗΜΕΡΟΜΗΝΙΑ
                tweet_type,                         # ΚΑΤΗΓΟΡΙΑ
                tweet.text.replace("\n", " "),      # ΑΝΑΦΟΡΑ
                f"https://x.com/{username}",        # ΧΡΗΣΤΗΣ
                engagement,                         # ΑΠΗΧΗΣΗ
                "",                                 # ΧΑΡΑΚΤΗΡΙΣΜΟΣ
                tweet_url,                          # ΣΥΝΔΕΣΜΟΣ
                "", "", "", ""                      # Remaining placeholders
            ])

    def on_connection_error(self):
        print("⚠️ Connection error — will reconnect automatically.")
        self.disconnect()

    def on_errors(self, errors):
        print("API returned error:", errors)

    def on_exception(self, exception):
        print("Exception:", exception)
        self.disconnect()


# === SETUP STREAM RULES ===
def setup_rules(stream: KeywordStream):
    """Remove existing rules and add the new one."""
    rules = stream.get_rules().data
    if rules:
        stream.delete_rules([rule.id for rule in rules])
    stream.add_rules(tweepy.StreamRule(KEYWORD_RULE))
    print(f"🔍 Tracking rule: {KEYWORD_RULE}")


# === MAIN ===
if __name__ == "__main__":
    stream = KeywordStream(client)

    # Prepare the CSV file with headers (once)
    try:
        with open(LOG_FILE, "x", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ΗΜΕΡΟΜΗΝΙΑ", "ΚΑΤΗΓΟΡΙΑ", "ΑΝΑΦΟΡΑ", "ΧΡΗΣΤΗΣ",
                "ΑΠΗΧΗΣΗ", "ΧΑΡΑΚΤΗΡΙΣΜΟΣ", "ΣΥΝΔΕΣΜΟΣ",
                "ΧΑΡΑΚΤΗΡΙΣΜΟΣ ΑΡΝΗΤΙΚΟΥ", "ΑΡΧΙΚΗ ΔΗΜΟΣΙΕΥΣΗ",
                "ΧΡΗΣΤΕΣ ΑΡΧΙΚΗΣ ΔΗΜΟΣΙΕΥΣΗΣ", "ΠΡΟΕΛΕΥΣΗ ΑΡΧΙΚΗΣ ΔΗΜΟΣΙΕΥΣΗΣ"
            ])
    except FileExistsError:
        pass

    setup_rules(stream)

    while True:
        try:
            stream.filter(
                tweet_fields=["created_at", "lang", "public_metrics"],
                expansions=["author_id"],
                user_fields=["username", "name"],
                threaded=False,
            )
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error: {e}")
            print("Reconnecting in 10 seconds...")
            time.sleep(10)

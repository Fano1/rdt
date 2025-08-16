import praw
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("PERSONAL_USE_SCRIPT")
CLIENT_SECRET = os.getenv("API_KEY_REDDIT")
USER_AGENT = "story-scraper by u/Fanoalone"  


print(CLIENT_ID, CLIENT_SECRET)

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

subreddits = ["nosleep", "shortscarystories", "tifu", "AskReddit"]

def scrape_stories(limit=5):
    with open("stories.md", 'a') as f:
        for sub in subreddits:
            print(f"\nTop stories from r/{sub} \n" + "-"*40)
            hot_posts = reddit.subreddit(sub).hot(limit=limit)
            for post in hot_posts:
                if not post.stickied:
                    print(f"Title: {post.title}\n")
                    f.write(f"\n {post.title}\n")
                    print(f"Story:\n{post.selftext[:1000]}...\n")
                    f.write(f"\n {post.selftext}\n")
                    print("—" * 40)

if __name__ == "__main__":
    scrape_stories(limit=3)

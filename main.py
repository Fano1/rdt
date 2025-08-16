import praw
from dotenv import load_dotenv
import os
import random

load_dotenv()

# -------- CONFIG --------
CLIENT_ID = os.getenv("PERSONAL_USE_SCRIPT")
CLIENT_SECRET = os.getenv("API_KEY_REDDIT")
USER_AGENT = "story-scraper by u/Fano"

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

subreddits = ["nosleep", "shortscarystories", "tifu", "AskReddit"]

def get_one_story():
    sub = random.choice(subreddits)
    print(f"\n🎲 Fetching a random story from r/{sub}\n" + "-"*40)

    posts = [p for p in reddit.subreddit(sub).hot(limit=20) if not p.stickied]
    post = random.choice(posts)

    title = post.title
    body = post.selftext.strip() or "(no body text, just the title/post)"
    author = str(post.author)

    # Append to file instead of overwriting
    with open("story.md", "a", encoding="utf-8") as f:
        f.write(f"\n---\n\n")  # separator between stories
        f.write(f"# {title}\n\n")
        f.write(f"👤 Author: u/{author}\n\n")
        f.write(body + "\n")

    print(f"✅ Appended: {title} (from r/{sub}) → story.md")

if __name__ == "__main__":
    get_one_story()

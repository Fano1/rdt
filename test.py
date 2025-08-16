# -----------------------------
# Reddit to TikTok Horror Video (gTTS version)
# -----------------------------
import os
from dotenv import load_dotenv
import praw
import json
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pyttsx3
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import logging

# Load environment variables
load_dotenv()

# -----------------------------
# Config
# -----------------------------
REDDIT_CLIENT_ID = os.getenv("PERSONAL_USE_SCRIPT")
REDDIT_CLIENT_SECRET = os.getenv("API_KEY_REDDIT")
REDDIT_USER_AGENT = "story_scraper"

SUBREDDITS = ["nosleep", "shortscarystories", "tifu", "AskReddit"]
CACHE_FILE = "story_cache.json"
BACKGROUND_VIDEO = "subwaysurfer.mp4"
OUTPUT_AUDIO = "story_audio.mp3"   # gTTS generates mp3
OUTPUT_VIDEO = "final_video.mp4"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------
# Reddit Setup
# -----------------------------
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Load cache
try:
    with open(CACHE_FILE, "r") as f:
        story_cache = json.load(f)
except FileNotFoundError:
    story_cache = []

# -----------------------------
# Functions
# -----------------------------
def fetch_story():
    """Fetch a unique Reddit story."""
    subreddit_name = random.choice(SUBREDDITS)
    subreddit = reddit.subreddit(subreddit_name)
    for post in subreddit.hot(limit=50):
        if post.id not in story_cache and not post.stickied and post.selftext.strip():
            story_cache.append(post.id)
            with open(CACHE_FILE, "w") as f:
                json.dump(story_cache, f)
            logging.info(f"Fetched story from r/{subreddit_name}: {post.title}")
            return post.title + "\n\n" + post.selftext
    logging.info("No new stories found in all subreddits.")
    return None

def generate_audio(story_text, speed = 900):
    """Generate audio from text using gTTS."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', speed)
        engine.save_to_file(story_text, 'story_audio.mp3')
        engine.runAndWait()
        logging.info("Audio generated successfully.")
    except Exception as e:
        logging.error(f"Error generating audio: {e}")

def generate_video(story_text):
    """Create scrolling text video."""
    try:
        background = VideoFileClip(BACKGROUND_VIDEO)
        audio = AudioFileClip(OUTPUT_AUDIO)

        # Scrolling text clip
        text_clip = TextClip(
            story_text, fontsize=40, color='white', method='caption', size=(background.w * 0.8, None), font='Arial-Bold'
        )
        text_clip = text_clip.set_pos(lambda t: ('center', -text_clip.h + t * 50))  # Scrolls up
        text_clip = text_clip.set_duration(background.duration)

        # Composite video
        final_clip = CompositeVideoClip([background, text_clip])
        final_clip = final_clip.set_audio(audio)
        final_clip.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", threads=4)
        logging.info(f"Video saved as {OUTPUT_VIDEO}.")
    except Exception as e:
        logging.error(f"Error generating video: {e}")

# -----------------------------
# Async Pipeline
# -----------------------------
async def main():
    logging.info("Starting the pipeline.")
    executor = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()

    story_text = await loop.run_in_executor(executor, fetch_story)
    if not story_text:
        logging.info("No new stories found!")
        return

    logging.info(f"Fetched story:\n{story_text[:300]}...\n")

    # Generate audio
    await loop.run_in_executor(executor, lambda: generate_audio(story_text))
    logging.info("Audio generated.")

    # Generate video
    await loop.run_in_executor(executor, lambda: generate_video(story_text))
    logging.info(f"Video saved as {OUTPUT_VIDEO}.")

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())

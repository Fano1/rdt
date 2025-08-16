import os
from dotenv import load_dotenv
import praw
from gtts import gTTS
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

load_dotenv()

# ---------------- CONFIG ----------------
CLIENT_ID = os.getenv("PERSONAL_USE_SCRIPT")
CLIENT_SECRET = os.getenv("API_KEY_REDDIT")
USER_AGENT = "story-scraper by u/yourusername"
BACKGROUND_VIDEO = "subwaysurfer.mp4"  # your background video path
AUDIO_FILE = "story_audio.mp3"
FINAL_VIDEO = "final_video.mp4"

# ---------------- INIT ----------------
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

SUBREDDITS = ["nosleep", "shortscarystories", "tifu", "AskReddit"]

# ---------------- FUNCTIONS ----------------
def get_one_story():
    """Fetch one random hot story from the subreddits."""
    for sub in SUBREDDITS:
        for post in reddit.subreddit(sub).hot(limit=10):
            if not post.stickied and post.selftext.strip():
                return post.title, post.selftext
    return "No Story Found", "No story content available."

def create_audio(text, filename=AUDIO_FILE):
    """Generate speech from text using gTTS."""
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return filename

def create_video(bg_video_path, text_title, text_story, audio_path, output_path):
    """Combine background video, text, and audio into final video."""
    clip = VideoFileClip(bg_video_path)
    
    # Title clip (top)
    title_clip = TextClip(
        txt=text_title,
        fontsize=50,
        color='yellow',
        font='Arial',
        method='label'
    ).set_position(("center", 50)).set_duration(clip.duration)

    # Story clip (scrolling)
    story_clip = TextClip(
        txt=text_story,
        fontsize=40,
        color='white',
        font='Arial',
        method='caption',
        size=(clip.w - 40, None)
    ).set_position(("center", 150)).set_duration(clip.duration)

    # Audio
    audio_clip = AudioFileClip(audio_path)
    clip = clip.set_audio(audio_clip)

    final_clip = CompositeVideoClip([clip, title_clip, story_clip])
    final_clip.write_videofile(output_path, codec="libx264", fps=clip.fps)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    title, story = get_one_story()
    create_audio(story)
    create_video(BACKGROUND_VIDEO, title, story, AUDIO_FILE, FINAL_VIDEO)
    print(f"✅ Video created: {FINAL_VIDEO}")

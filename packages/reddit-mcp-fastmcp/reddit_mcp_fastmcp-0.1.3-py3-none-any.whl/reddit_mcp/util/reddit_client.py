import os
import praw
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class RedditClient:
    _instance: Optional["RedditClient"] = None

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="Interesting Posts Reader",
        )

    @classmethod
    def get_instance(cls) -> "RedditClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

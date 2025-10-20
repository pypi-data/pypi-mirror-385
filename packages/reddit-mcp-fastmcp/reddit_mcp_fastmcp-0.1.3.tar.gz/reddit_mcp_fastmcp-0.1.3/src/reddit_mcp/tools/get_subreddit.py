from pydantic import BaseModel, Field, validate_call
from ..util.reddit_client import RedditClient


class SubredditResult(BaseModel):
    """Subreddit details"""

    display_name: str = Field(description="Display name of the subreddit")
    title: str = Field(description="Title of the subreddit")
    description: str = Field(description="Full subreddit description")
    public_description: str = Field(description="Short public description")
    subscribers: int = Field(description="Number of subscribers")
    created_utc: float = Field(description="UTC timestamp when subreddit was created")
    over18: bool = Field(description="Whether the subreddit is NSFW")
    url: str = Field(description="URL of the subreddit")


@validate_call(validate_return=True)
def get_subreddit(subreddit_name: str) -> SubredditResult:
    """
    Retrieve a subreddit by name.

    Args:
        subreddit_name: Name of the subreddit to retrieve

    Returns:
        Detailed information about the subreddit
    """
    client = RedditClient.get_instance()
    subreddit = client.reddit.subreddit(subreddit_name)

    return SubredditResult(
        display_name=subreddit.display_name,
        title=subreddit.title,
        description=subreddit.description,
        public_description=subreddit.public_description,
        subscribers=subreddit.subscribers,
        created_utc=subreddit.created_utc,
        over18=subreddit.over18,
        url=subreddit.url,
    )

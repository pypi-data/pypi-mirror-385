from typing import List, Literal
from pydantic import BaseModel, Field, validate_call
from ..util.reddit_client import RedditClient
from ..util.date_utils import format_utc_timestamp


class PostResult(BaseModel):
    """Reddit post search result"""

    id: str = Field(description="Unique identifier of the post")
    title: str = Field(description="Title of the post")
    url: str = Field(description="URL of the post")
    score: int = Field(description="Number of upvotes minus downvotes")
    num_comments: int = Field(description="Number of comments on the post")
    created_utc: str = Field(description="UTC timestamp when post was created")


class SearchPostsParams(BaseModel):
    """Parameters for searching posts within a subreddit"""

    subreddit_name: str = Field(description="Name of the subreddit to search in")
    query: str = Field(description="Search query string")
    sort: Literal["relevance", "hot", "top", "new", "comments"] = Field(
        default="relevance", description="How to sort the results"
    )
    syntax: Literal["cloudsearch", "lucene", "plain"] = Field(
        default="lucene", description="Query syntax to use"
    )
    time_filter: Literal["all", "year", "month", "week", "day", "hour"] = Field(
        default="all", description="Time period to limit results to"
    )


@validate_call(validate_return=True)
def search_posts(params: SearchPostsParams) -> List[PostResult]:
    """
    Search for posts within a subreddit.

    Args:
        params: Search parameters including subreddit name, query, and filters

    Returns:
        List of matching posts with their details
    """
    client = RedditClient.get_instance()
    subreddit = client.reddit.subreddit(params.subreddit_name)

    posts = subreddit.search(
        query=params.query,
        sort=params.sort,
        syntax=params.syntax,
        time_filter=params.time_filter,
    )

    return [
        PostResult(
            id=post.id,
            title=post.title,
            url=post.url,
            score=post.score,
            num_comments=post.num_comments,
            created_utc=format_utc_timestamp(post.created_utc),
        )
        for post in posts
    ]

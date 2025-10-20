from typing import List, Literal, Union

from ..util.reddit_client import RedditClient
from ..util.date_utils import format_utc_timestamp

from pydantic import BaseModel, Field, validate_call


class SubredditResult(BaseModel):
    """Subreddit search result"""

    name: str = Field(description="Display name of the subreddit")
    public_description: str = Field(description="Short description shown publicly")
    url: str = Field(description="URL of the subreddit")
    subscribers: int | None = Field(default=None, description="Number of subscribers")
    created_utc: str = Field(description="UTC date when subreddit was created")
    description: str | None = Field(
        default=None,
        description="Full subreddit description with markdown formatting",
    )


class SearchByName(BaseModel):
    """Parameters for searching subreddits by name"""

    type: Literal["name"]
    query: str
    include_nsfw: bool = Field(
        default=False,
        description="Whether to include NSFW subreddits in search results",
    )
    exact_match: bool = Field(
        default=False, description="If True, only return exact name matches"
    )


class SearchByDescription(BaseModel):
    """Parameters for searching subreddits by description"""

    type: Literal["description"]
    query: str
    include_full_description: bool = Field(
        default=False,
        description="Whether to include the full subreddit description (aka sidebar description) in results -- can be very long and contain markdown formatting",
    )


SearchParams = Union[SearchByName, SearchByDescription]


@validate_call(validate_return=True)
def search_subreddits(by: SearchParams) -> List[SubredditResult]:
    """
    Search for subreddits using either name-based or description-based search.

    Args:
        by: Search parameters, either SearchByName or SearchByDescription

    Returns:
        List of matching subreddits with their details
    """
    client = RedditClient.get_instance()

    if by.type == "name":
        subreddits = client.reddit.subreddits.search_by_name(
            by.query, exact=by.exact_match, include_nsfw=by.include_nsfw
        )
    else:  # by.type == "description"
        subreddits = client.reddit.subreddits.search(by.query)

    return [
        SubredditResult(
            name=subreddit.display_name,
            public_description=subreddit.public_description,
            description=(
                subreddit.description
                if (by.type == "description" and by.include_full_description)
                else None
            ),
            url=subreddit.url,
            subscribers=subreddit.subscribers,
            created_utc=format_utc_timestamp(subreddit.created_utc),
        )
        for subreddit in subreddits
    ]

from pydantic import BaseModel, Field, validate_call
from ..util.reddit_client import RedditClient
from ..util.date_utils import format_utc_timestamp


class SubmissionResult(BaseModel):
    """Reddit submission details"""

    title: str = Field(description="Title of the submission")
    url: str = Field(description="URL of the submission")
    author: str | None = Field(description="Username of the author, or None if deleted")
    subreddit: str = Field(description="Name of the subreddit")
    score: int = Field(description="Number of upvotes minus downvotes")
    num_comments: int = Field(description="Number of comments on the submission")
    selftext: str = Field(description="Text content of the submission")
    created_utc: str = Field(description="UTC timestamp when submission was created")


@validate_call(validate_return=True)
def get_submission(submission_id: str) -> SubmissionResult:
    """
    Retrieve a specific submission by ID.

    Args:
        submission_id: ID of the submission to retrieve

    Returns:
        Detailed information about the submission
    """
    client = RedditClient.get_instance()
    submission = client.reddit.submission(submission_id)

    return SubmissionResult(
        title=submission.title,
        url=submission.url,
        author=None if submission.author is None else submission.author.name,
        subreddit=submission.subreddit.display_name,
        score=submission.score,
        num_comments=submission.num_comments,
        selftext=submission.selftext,
        created_utc=format_utc_timestamp(submission.created_utc),
    )

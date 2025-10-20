from typing import List
from pydantic import BaseModel, Field, validate_call
from ..util.reddit_client import RedditClient
from ..util.date_utils import format_utc_timestamp
from praw.models import MoreComments


class CommentResult(BaseModel):
    """Reddit comment details"""

    id: str = Field(description="Unique identifier of the comment")
    body: str = Field(description="Text content of the comment")
    author: str | None = Field(description="Username of the author, or None if deleted")
    created_utc: str = Field(description="UTC timestamp when comment was created")
    is_submitter: bool = Field(
        description="Whether the comment author is the submission author"
    )
    score: int = Field(description="Number of upvotes minus downvotes")
    replies: List["CommentResult"] = Field(
        description="List of reply comments", default_factory=list
    )


CommentResult.model_rebuild()  # Required for self-referential models


def comment_to_model(comment) -> CommentResult:
    """Convert PRAW comment object to CommentResult model."""
    # Skip MoreComments objects
    if isinstance(comment, MoreComments):
        return None

    return CommentResult(
        id=comment.id,
        body=comment.body,
        author=None if comment.author is None else comment.author.name,
        created_utc=format_utc_timestamp(comment.created_utc),
        is_submitter=comment.is_submitter,
        score=comment.score,
        replies=[
            result
            for reply in comment.replies
            if (result := comment_to_model(reply)) is not None
        ],
    )


@validate_call(validate_return=True)
def get_comments_by_submission(
    submission_id: str, replace_more: bool = True
) -> List[CommentResult]:
    """
    Retrieve comments from a specific submission.

    Args:
        submission_id: ID of the submission to get comments from
        replace_more: Whether to replace MoreComments objects with actual comments

    Returns:
        List of comments with their replies
    """
    client = RedditClient.get_instance()
    submission = client.reddit.submission(submission_id)
    if replace_more:
        submission.comments.replace_more()
    return [
        result
        for comment in submission.comments.list()
        if (result := comment_to_model(comment)) is not None
    ]


@validate_call(validate_return=True)
def get_comment_by_id(comment_id: str) -> CommentResult:
    """
    Retrieve a specific comment by ID.

    Args:
        comment_id: ID of the comment to retrieve

    Returns:
        Comment details with any replies
    """
    client = RedditClient.get_instance()
    return comment_to_model(client.reddit.comment(comment_id))

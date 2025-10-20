import pytest
from reddit_mcp.tools.search_subreddits import (
    search_subreddits,
    SearchByName,
    SearchByDescription,
)
from reddit_mcp.tools.get_subreddit import get_subreddit, SubredditResult
from reddit_mcp.tools.search_posts import search_posts, SearchPostsParams
from reddit_mcp.tools.get_submission import get_submission, SubmissionResult
from reddit_mcp.tools.get_comments import (
    get_comments_by_submission,
    get_comment_by_id,
    CommentResult,
)


def test_search_subreddits():
    # Test name-based search
    results = search_subreddits(SearchByName(type="name", query="computer"))
    assert isinstance(results, list)
    if results:
        assert isinstance(results[0].name, str)
        assert isinstance(results[0].public_description, str)

    # Test description-based search
    results = search_subreddits(
        SearchByDescription(type="description", query="computers")
    )
    assert isinstance(results, list)
    if results:
        assert isinstance(results[0].name, str)
        assert isinstance(results[0].public_description, str)


def test_get_subreddit():
    result = get_subreddit("ChatGPT")
    assert isinstance(result, SubredditResult)
    assert isinstance(result.display_name, str)
    assert isinstance(result.subscribers, int)


def test_search_posts():
    # Test with Pydantic model params
    results = search_posts(
        SearchPostsParams(subreddit_name="ChatGPT", query="artificial intelligence")
    )
    assert isinstance(results, list)
    if results:
        assert isinstance(results[0].id, str)
        assert isinstance(results[0].title, str)


def test_get_submission():
    result = get_submission("1j66jbs")
    assert isinstance(result, SubmissionResult)
    assert isinstance(result.title, str)
    assert isinstance(result.url, str)


def test_get_comments():
    # Test getting comments by submission
    comments = get_comments_by_submission("1j66jbs", replace_more=False)
    assert isinstance(comments, list)
    if comments:
        assert isinstance(comments[0], CommentResult)
        assert isinstance(comments[0].id, str)
        assert isinstance(comments[0].body, str)

    # Test getting single comment
    comment = get_comment_by_id("mgmk7d2")
    assert isinstance(comment, CommentResult)
    assert isinstance(comment.id, str)
    assert isinstance(comment.body, str)

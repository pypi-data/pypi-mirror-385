"""
Functions for notifying different platforms and services.
"""

import logging
import os
import shutil
import subprocess
from urllib.parse import urlparse

from github import Github

from fraim.core.history import EventRecord, History

logger = logging.getLogger(__name__)


def _get_github_token() -> str | None:
    """
    Get GitHub token from multiple sources in order of preference:
    1. GITHUB_TOKEN environment variable
    2. GitHub CLI token
    3. Git credential helper for github.com
    """
    logger.debug("Attempting to get GitHub token from multiple sources")

    # Try environment variable first
    logger.debug("Checking GITHUB_TOKEN environment variable")
    token = os.getenv("GITHUB_TOKEN")
    if token:
        logger.info("GitHub token found in environment variable")
        return token
    logger.debug("No GitHub token found in environment variable")

    # Try GitHub CLI
    logger.debug("Checking GitHub CLI for authentication")
    if shutil.which("gh"):
        logger.debug("GitHub CLI found, attempting to get token")
        try:
            result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
            token = result.stdout.strip()
            if token:
                logger.info("GitHub token found via GitHub CLI")
                return token
        except subprocess.CalledProcessError as e:
            logger.debug(f"GitHub CLI authentication failed: {e}")
    else:
        logger.debug("GitHub CLI not found")

    # Try git credential helper
    logger.debug("Attempting to get GitHub token from git credential helper")
    try:
        # Use git credential fill to get credentials for github.com
        result = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse the credential response
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if line.startswith("password="):
                password = line.split("=", 1)[1]
                # GitHub personal access tokens start with 'ghp_', 'gho_', or 'ghu_'
                # or could be classic tokens that start with letters/numbers
                if password and (password.startswith(("ghp_", "gho_", "ghu_")) or len(password) >= 20):
                    logger.info("GitHub token found via git credential helper")
                    return password
    except subprocess.CalledProcessError as e:
        logger.debug(f"Git credential helper failed: {e}")

    logger.warning("No GitHub token found from any source")
    return None


def parse_pr_url(pr_url: str) -> tuple[str, str, str]:
    # Parse PR URL to get owner, repo, and PR number
    logger.debug(f"Parsing PR URL: {pr_url}")
    try:
        path_parts = urlparse(pr_url).path.strip("/").split("/")
        if len(path_parts) < 4 or path_parts[-2] != "pull":
            raise ValueError
        owner, repo, _, pr_number = path_parts
        logger.debug(f"Parsed PR details - Owner: {owner}, Repo: {repo}, PR: {pr_number}")
    except (ValueError, IndexError):
        logger.error(f"Failed to parse PR URL: {pr_url}")
        raise ValueError(f"Invalid PR URL format: {pr_url}")

    return owner, repo, pr_number


def add_comment(history: History, pr_url: str, description: str, user_or_group: str) -> None:
    """
    Adds a comment to a GitHub PR.
    """
    history.append_record(EventRecord(description=f"Adding comment to PR {pr_url}"))

    owner, repo, pr_number = parse_pr_url(pr_url)

    # Get GitHub token from multiple sources
    logger.debug("Getting GitHub authentication token")
    github_token = _get_github_token()
    if not github_token:
        logger.error("GitHub authentication failed - no token found")
        raise RuntimeError(
            "GitHub authentication required. Please ensure one of the following:\n"
            "1. Set GITHUB_TOKEN environment variable\n"
            "2. Configure git credentials for github.com\n"
            "3. Login with GitHub CLI (`gh auth login`)"
        )

    # Initialize GitHub client
    logger.debug("Initializing GitHub client")
    gh = Github(github_token)

    try:
        # Get repository and PR
        logger.debug(f"Getting repository: {owner}/{repo}")
        repository = gh.get_repo(f"{owner}/{repo}")
        logger.debug(f"Getting pull request #{pr_number}")
        pull_request = repository.get_pull(int(pr_number))
    except Exception as e:
        logger.error(f"Failed to get repository or pull request: {e!s}")
        raise RuntimeError(f"Failed to get repository or pull request: {e!s}") from e

    try:
        # Add comment with optional user_or_group mention
        if user_or_group.strip():
            comment_text = f"@{user_or_group}\n\n{description}"
            logger.info(f"Adding comment to PR with user_or_group mention: {user_or_group}")
        else:
            comment_text = description
            logger.info("Adding comment to PR without user_or_group mention")
        pull_request.create_issue_comment(comment_text)
        logger.info(f"Successfully added comment to PR #{pr_number}")
    except Exception as e:
        logger.error(f"Failed to add comment to PR: {e!s}")
        raise RuntimeError(f"Failed to add comment to PR: {e!s}") from e


def add_reviewer(history: History, pr_url: str, user_or_group: str) -> None:
    """
    Notifies a GitHub user or team by adding them as reviewers and leaving a comment on a PR.

    Simple detection logic:
    1. First tries to find as organization team (supports "org/team" or just "team")
    2. Then tries to find as individual user
    3. Fails if neither exists

    Args:
        pr_url: The full URL to the GitHub PR
        description: The description to add as a comment
        user_or_group: The GitHub user or team to notify

    Raises:
        ValueError: If the PR URL is invalid
        RuntimeError: If GitHub token is not set, API calls fail, or user/team cannot be found
    """
    logger.info(f"Adding GitHub user_or_group {user_or_group} as reviewer for PR: {pr_url}")
    history.append_record(
        EventRecord(description=f"Adding GitHub user_or_group {user_or_group} as reviewer for PR: {pr_url}")
    )

    owner, repo, pr_number = parse_pr_url(pr_url)

    # Get GitHub token from multiple sources
    logger.debug("Getting GitHub authentication token")
    github_token = _get_github_token()
    if not github_token:
        logger.error("GitHub authentication failed - no token found")
        raise RuntimeError(
            "GitHub authentication required. Please ensure one of the following:\n"
            "1. Set GITHUB_TOKEN environment variable\n"
            "2. Configure git credentials for github.com\n"
            "3. Login with GitHub CLI (`gh auth login`)"
        )

    # Initialize GitHub client
    logger.debug("Initializing GitHub client")
    gh = Github(github_token)

    try:
        # Get repository and PR
        logger.debug(f"Getting repository: {owner}/{repo}")
        repository = gh.get_repo(f"{owner}/{repo}")
        logger.debug(f"Getting pull request #{pr_number}")
        pull_request = repository.get_pull(int(pr_number))
    except Exception as e:
        logger.error(f"Failed to get repository or pull request: {e!s}")
        raise RuntimeError(f"Failed to get repository or pull request: {e!s}") from e

    try:
        # Try to add reviewer - first as team, then as user
        reviewer_name = user_or_group.strip("@").split("/")[-1]
        logger.info(f"Attempting to add reviewer: {reviewer_name}")

        # First, try as organization team
        team_error = None
        user_error = None

        try:
            team_name = reviewer_name

            # Request review from team
            pull_request.create_review_request(team_reviewers=[team_name])
            logger.info(f"Successfully requested review from team {owner}/{team_name} for PR #{pr_number}")
            return
        except Exception as e:
            team_error = e
            logger.debug(f"Not found as team: {team_error}")

        # Then, try as user
        try:
            # Request review from user
            pull_request.create_review_request(reviewers=[reviewer_name])
            logger.info(f"Successfully requested review from user {reviewer_name} for PR #{pr_number}")
            return

        except Exception as e:
            user_error = e
            logger.debug(f"Not found as user: {user_error}")

        # Neither worked - include both errors in message
        error_msg = f"Could not find '{reviewer_name}' as either a GitHub team or user. Team error: {team_error}. User error: {user_error}"
        raise RuntimeError(error_msg)

    except Exception as e:
        logger.error(f"Failed to request review: {e!s}")
        raise RuntimeError(f"Failed to request review: {e!s}") from e

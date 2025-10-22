"""GitHub-specific runner that builds context from GitHub issues."""

from typing import TypeVar

from pydantic import BaseModel

from .base_runner import BaseAgentRunner
from .github_context import build_github_context

T = TypeVar("T", bound=BaseModel)


class GitHubIssueRunner(BaseAgentRunner):
    """GitHub issue analysis runner.

    Handles converting GitHub issue data into context strings
    while remaining agnostic about output data types.
    """

    def _build_context(self, issue_data) -> str:
        """Build context string from GitHub issue data."""
        # Extract the issue from the stored issue data
        issue = (
            issue_data["issue"]
            if isinstance(issue_data, dict) and "issue" in issue_data
            else issue_data
        )
        return build_github_context(issue)

    def _get_logging_id(self, issue_data) -> str:
        """Extract issue number from GitHub issue for logging."""
        if isinstance(issue_data, dict) and "issue" in issue_data:
            issue = issue_data["issue"]
            if hasattr(issue, "number"):
                return str(issue.number)
            else:
                return str(issue.get("number", "unknown"))
        return "unknown"

    def _build_user_message(self, context: str) -> str:
        """Format GitHub issue context as a problem description for analysis."""
        return f"**Problem Description:**\n{context}"

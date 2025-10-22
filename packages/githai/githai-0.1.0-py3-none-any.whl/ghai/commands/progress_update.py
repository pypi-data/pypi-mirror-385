"""Progress update command for GHAI CLI."""

import importlib.resources
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click

from ghai.github_api import GitHubGraphQLClient
from ghai.llm_api import LLMClient
from ghai.types.github_api_types import Issue, IssueState


@click.command()
@click.option(
    "--issue-url",
    "-u",
    required=True,
    help="GitHub issue URL (e.g., https://github.com/owner/repo/issues/123)",
)
@click.option(
    "--days",
    "-d",
    default=7,
    help="Number of days to look back for comments (default: 7)",
)
@click.option(
    "--prompt-file",
    "-pf",
    help="Custom prompt file path (defaults to built-in prompt)",
)
@click.option(
    "--prompt",
    "-p",
    help="Custom prompt string (overrides prompt file if provided)",
)
@click.pass_context
def progress_update(
    ctx: click.Context, issue_url: str, days: int, prompt_file: Optional[str] = None, prompt: Optional[str] = None
) -> None:
    """Get progress update from GitHub issue and its sub-issues"""

    print("Getting issue details...")
    github_client = GitHubGraphQLClient()
    owner, repo, issue_number = github_client.parse_github_issue_url(issue_url)

    initiative_issue = github_client.get_issue_details(
        owner, repo, issue_number
    )

    if initiative_issue is None:
        raise ValueError(f"Issue not ${issue_url} not found.")

    sub_issues = github_client.get_issue_details_list(
        initiative_issue.subIssueIds
    )

    since_datetime = datetime.now() - timedelta(days=days)

    for issue in sub_issues:
        issue.filter_comments_since(since_datetime)
        issue.calculate_issue_state_change(since_datetime)

    print("Generating context file...")
    markdown_output = format_context(initiative_issue, sub_issues)

    with open("context.md", "w") as f:
        f.write(markdown_output)

    if prompt_file:
        prompt_path = Path(prompt_file)
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Custom prompt file not found: {prompt_path.absolute()}"
            )
        prompt_content = prompt_path.read_text().strip()
    elif prompt:
        prompt_content = prompt.strip()
    else:
        # Default built-in prompt
        import ghai.prompts as prompts_package
        prompt_content = importlib.resources.read_text(
            prompts_package, "initiative_prompt.md"
        ).strip()

    print("Generating LLM response...")
    llmClient = LLMClient()
    response = llmClient.generate_response(
        prompt_content, context_files=["context.md"])

    with open("response.md", "w") as f:
        f.write(response)

    Path("context.md").unlink(missing_ok=True)


def format_context(initiative_issue: Issue, sub_issues: List[Issue]) -> str:
    """Format the context for the progress update (legacy table format)."""

    context: list[str] = []
    context.append("# Initiative Details: ")
    context.append(f"**Title:** {initiative_issue.title}")
    context.append(f"**URL:** {initiative_issue.url}")
    context.append("### Recent Initiative Comments: ")
    for comment in initiative_issue.comments:
        context.append(f"##### Date: {comment.createdAt}")
        context.append("```")
        context.append(f"{comment.body}")
        context.append("```")
        context.append("")

    context.append("# 📋 Sub-Issues Progress")
    for issue in sub_issues:
        if len(issue.comments) == 0 and issue.stateChange.__eq__(IssueState.NONE):
            continue
        context.append(f"## {issue.title}")
        context.append(f"**URL:** {issue.url}")
        context.append(f"**State Change:** {issue.stateChange.value}")
        context.append("### Recent Comments: ")
        for comment in issue.comments:
            context.append(f"##### Date: {comment.createdAt}")
            context.append("```")
            context.append(f"{comment.body}")
            context.append("```")
            context.append("")

    return "\n".join(context)

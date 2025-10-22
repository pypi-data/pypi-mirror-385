"""Snippet update command for GHAI CLI."""

import importlib.resources
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click

from ghai.github_api import GitHubGraphQLClient
from ghai.llm_api import LLMClient
from ghai.types.github_api_types import Issue


@click.command()
@click.option('--project-url', '-u',
              required=True,
              help='GitHub project URL (e.g., https://github.com/orgs/<org_name>/projects/<project_id>)'
              )
@click.option('--days', '-d', default=7, help='Number of days to look back (default: 7)')
@click.option('--workstream', '-w', default=None, help='Workstream to filter by (default: SFI)')
@click.option(
    "--prompt",
    "-p",
    help="Custom prompt file path (defaults to built-in prompt)",
)
@click.pass_context
def snippet_update(
    ctx: click.Context,
    project_url: str,
    workstream: str,
    days: int,
    prompt: Optional[str] = None
) -> None:
    """Get snippet update from a GitHub project workstream"""

    github_client = GitHubGraphQLClient()

    owner, project_number = github_client.parse_github_project_url(project_url)

    print("Getting project details...")
    project_issues = github_client.get_project_issues(
        owner, project_number
    )

    print("Filtering project issues...")
    filtered_issues: List[Issue] = []
    for issue in project_issues:
        issue.filter_comments_since(datetime.now() - timedelta(days=days))

        if workstream and issue.get_field_value("Workstream") != workstream:
            continue

        filtered_issues.append(issue)

    print("Generating context file...")
    generate_context_file(filtered_issues, "context.md")

    # Get the prompt file path - use custom if provided, otherwise default
    if prompt:
        prompt_path = Path(prompt)
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Custom prompt file not found: {prompt_path.absolute()}"
            )
        prompt_content = prompt_path.read_text().strip()
    else:
        import ghai.prompts as prompts_package
        prompt_content = importlib.resources.read_text(
            prompts_package, "snippet_prompt.md"
        ).strip()

    llm_client = LLMClient()

    print("Generating LLM response...")
    llm_response = llm_client.generate_response(
        prompt_content, context_files=["context.md"])

    with open("response.md", "w") as f:
        f.write(llm_response)

    Path("context.md").unlink(missing_ok=True)


def generate_context_file(issues: List[Issue], output_path: str = "context.md") -> None:
    """Generate a context markdown file from ProjectIssues with recent comments.

    Args:
        issues: List of ProjectIssue objects (should be pre-filtered for recent comments)
        output_path: Path where to save the context file
    """
    content: list[str] = []

    for issue in issues:
        if not issue.comments:
            continue

        content.append(f"# Issue: {issue.title}")
        content.append(f"**URL:** {issue.url}\n")
        content.append(f"**ID:** {issue.issue_id}\n")
        content.append(f"**Project:** {issue.projects[0]}\n\n")

        for field in issue.projects[0].fieldValues:
            content.append(f"- **{field.name}:** {field.value}\n")

        content.append("\n## Recent Comments (Last 14 Days):\n")
        for comment in sorted(issue.comments, key=lambda c: c.createdAt, reverse=True):
            if isinstance(comment.createdAt, str):
                date_str = comment.createdAt
            else:
                date_str = comment.createdAt.isoformat()

            content.append(f"\n### Comment - {date_str}\n")
            content.append(f"**URL:** {comment.url}\n")
            content.append("```\n")
            content.append(f"{comment.body}\n")
            content.append("```\n")

        content.append("\n---\n")

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

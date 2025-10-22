

import importlib.resources
from pathlib import Path
from typing import Optional

import click

from ghai.github_api import GitHubGraphQLClient
from ghai.llm_api import LLMClient


@click.command()
@click.option(
    "--issue-url",
    "-u",
    required=True,
    help="GitHub issue URL (e.g., https://github.com/owner/repo/issues/123)",
)
@click.option(
    "--prompt",
    "-p",
    help="Custom prompt file path (defaults to built-in prompt)",
)
@click.pass_context
def explain_issue(
    ctx: click.Context, issue_url: str, prompt: Optional[str] = None
) -> None:
    """Get progress update from GitHub issue and its sub-issues"""

    github_client = GitHubGraphQLClient()

    owner, repo, issue_number = github_client.parse_github_issue_url(issue_url)
    issue = github_client.get_issue_details(owner, repo, issue_number)

    formatted_issue = issue.format_issue_details() if issue else None

    if formatted_issue:
        with open("context.md", "w") as f:
            f.write(formatted_issue)

        llm_client = LLMClient()

        # Get the prompt file path - use custom if provided, otherwise default
        if prompt:
            prompt_path = Path(prompt)
            if not prompt_path.exists():
                raise FileNotFoundError(
                    f"Custom prompt file not found: {prompt_path.absolute()}")
            prompt_content = prompt_path.read_text().strip()
        else:
            import ghai.prompts as prompts_package
            prompt_content = importlib.resources.read_text(
                prompts_package, "explain_issue_prompt.md"
            ).strip()

        response = llm_client.generate_response(
            prompt_content,
            context_files=["context.md"]
        )
        print(response)

        Path("context.md").unlink(missing_ok=True)
    else:
        print(f"Issue {issue_number} not found.")

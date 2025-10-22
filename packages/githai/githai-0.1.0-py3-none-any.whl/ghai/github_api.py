"""GitHub GraphQL API client for GHAI CLI."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import requests

from ghai.types.github_api_types import Issue


class GitHubGraphQLClient:
    """A client for interacting with GitHub's GraphQL API."""

    def __init__(self) -> None:
        """Initialize the GitHub GraphQL client.

        Args:
            token: GitHub personal access token. Will try to get from keys.json.
        """
        self.base_url = "https://api.github.com/graphql"

        # Try multiple sources for the token
        self.token = self._get_token()

        if not self.token:
            raise ValueError(
                "GitHub token is required. You can set it by:\n"
                "- Using: ghai keys set GITHUB_TOKEN\n"
            )

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _get_token(self) -> Optional[str]:
        """Get GitHub token from keys.json"""
        home_dir = Path.home()
        keys_path = home_dir / ".ghai" / "keys.json"

        if keys_path.exists():
            keys_data: dict[str, str] = json.loads(keys_path.read_text())
            token = keys_data.get("GITHUB_TOKEN")
            if token:
                return token

        click.ClickException(
            "key 'GITHUB_TOKEN' not found. Please set it using 'ghai keys set GITHUB_TOKEN'"
        )
        return None

    def query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query against GitHub API.

        Args:
            query: The GraphQL query string
            variables: Optional variables for the query

        Returns:
            The response data from GitHub API

        Raises:
            requests.RequestException: If the HTTP request fails
            ValueError: If the GraphQL query has errors
        """
        payload: dict[str, Any] = {
            "query": query, "variables": variables or {}}

        try:
            response = requests.post(
                self.base_url, headers=self.headers, json=payload, timeout=30
            )
            response.raise_for_status()

            data: dict[str, Any] = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                error_messages = [
                    error.get("message", "Unknown error") for error in data["errors"]
                ]
                raise ValueError(
                    f"GraphQL errors: {'; '.join(error_messages)}")

            return data

        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to query GitHub API: {e}")

    def paginated_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        cursor_path: List[str] = [],
    ) -> List[Dict[str, Any]]:
        """
        Execute a paginated GraphQL query against GitHub API and return all results.

        Args:
            query: The GraphQL query string (must accept $after variable for pagination)
            variables: Optional dict of query variables
            cursor_path: Path (list of keys) to the paginated field in the response
                        e.g. ["organization", "projectV2", "items"]

        Returns:
            A list of all nodes across all pages.
        """
        all_nodes: list[dict[str, Any]] = []
        variables = variables or {}
        variables["after"] = None  # start without a cursor

        while True:
            data = self.query(query, variables)

            # Traverse into nested structure until we reach the paginated object
            page = data["data"]
            for key in cursor_path:
                page = page[key]

            # Collect nodes
            all_nodes.extend(page["nodes"])

            # Check if more pages exist
            page_info = page["pageInfo"]
            if not page_info["hasNextPage"]:
                break

            # Set cursor for next request
            variables["after"] = page_info["endCursor"]

        return all_nodes

    def parse_github_issue_url(self, url: str) -> tuple[str, str, int]:
        """Parse a GitHub issue URL to extract owner, repo, and issue number.

        Args:
            url: GitHub issue URL (e.g., "https://github.com/owner/repo/issues/123")

        Returns:
            Tuple of (owner, repo, issue_number)

        Raises:
            ValueError: If URL format is invalid
        """

        # Match GitHub issue URL pattern
        pattern = r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)"
        match = re.match(pattern, url)

        if not match:
            raise ValueError("Invalid GitHub issue URL format: {url}")

        owner, repo, issue_number = match.groups()
        return owner, repo, int(issue_number)

    def parse_github_project_url(self, url: str) -> tuple[str, int]:
        """Parse a GitHub project URL to extract owner and project number.

        Args:
            url: GitHub project URL (e.g., "https://github.com/orgs/owner/projects/20761"
                 or "https://github.com/users/username/projects/1")
        """
        # Match both organization and user project URLs
        pattern = r"https://github\.com/(?:orgs|users)/([^/]+)/projects/(\d+)"
        match = re.match(pattern, url)

        if not match:
            raise ValueError(f"Invalid GitHub project URL format: {url}")

        owner, project_number = match.groups()
        return owner, int(project_number)

    def is_organization(self, owner: str) -> bool:
        """Determine if the owner is an organisation or a user.

        Args:
            owner: GitHub username or organisation name

        Returns:
            True if owner is an organisation, False if it's a user
        """
        query = """
          query($login: String!) {
            organization(login: $login) {
              login
            }
          }
        """
        variables = {"login": owner}

        try:
            response = self.query(query, variables)
            # If the query succeeds, it's an organisation
            return response.get("data", {}).get("organization") is not None
        except ValueError:
            # If it fails, it's likely a user account
            return False

    def get_project_issues(self, owner: str, project_number: int) -> List[Issue]:
        """Get detailed information about a GitHub project including its issues.

        Args:
            owner: Organization or user who owns the repository
            project_number: Project number

        Returns:
            Project information including its issues
        """
        # Determine if owner is an organization or user
        is_org = self.is_organization(owner)
        owner_type = "organization" if is_org else "user"

        query = """
          query($owner: String!, $projectNumber: Int!, $after: String) {{
            {owner_type}(login: $owner) {{
              projectV2(number: $projectNumber) {{
                id
                title
                items(first: 100, after: $after) {{
                  nodes {{
                    content {{
                      ... on Issue {{
                        id
                        title
                        state
                        body
                        url
                        comments(last: 50, orderBy: {{field: UPDATED_AT, direction: ASC}}) {{
                            nodes {{
                                id
                                body
                                createdAt
                                url
                            }}
                            totalCount
                        }}
                        labels(first: 10) {{
                            nodes {{
                                name
                                description
                            }}
                        }}
                        timelineItems(last: 50, itemTypes: [CLOSED_EVENT]) {{
                            nodes {{
                                ... on ClosedEvent {{
                                    createdAt
                                    stateReason
                                }}
                            }}
                        }}
                        subIssues(first: 100) {{
                            nodes {{
                                id
                            }}
                        }}
                      }}
                    }}
                    fieldValues(first: 25) {{
                      nodes {{
                        ... on ProjectV2ItemFieldSingleSelectValue {{
                          name
                          field {{
                            ... on ProjectV2SingleSelectField {{
                              name
                            }}
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        """.format(owner_type=owner_type)
        variables: dict[str, Any] = {
            "owner": owner, "projectNumber": project_number}

        response = self.query(query, variables)
        project_id = response.get("data", {}).get(
            owner_type, {}).get("projectV2", {}).get("id")

        project_title = response.get("data", {}).get(
            owner_type, {}).get("projectV2", {}).get("title")

        project_issues: List[Issue] = []
        for node in response.get("data", {}).get(owner_type, {}).get("projectV2", {}).get("items", {}).get("nodes", []):
            # Skip if content is None (e.g., draft cards)
            if node.get("content") is None:
                continue

            project_issue: Issue = Issue.from_graphql_project_query(
                node,
                project_id,
                project_title
            )
            project_issues.append(project_issue)

        return project_issues

    def get_issue_details(self, owner: str, repository_name: str, issue_number: int) -> Optional[Issue]:
        """Get detailed information about a GitHub issue.

        Args:
            owner: Organization or user who owns the repository
            repository_name: Repository name
            issue_number: Issue number

        Returns:
            An Issue object with relevant details
        """

        query = """
          query($owner: String!, $name: String!, $issueNumber: Int!) {
              repository(owner: $owner, name: $name) {
                  issue(number: $issueNumber) {
                      id
                      title
                      state
                      body
                      url
                      comments(last: 50, orderBy: {field: UPDATED_AT, direction: ASC}) {
                          nodes {
                              id
                              body
                              createdAt
                              url
                          }
                          totalCount
                      }
                      labels(first: 10) {
                          nodes {
                              name
                              description
                          }
                      }
                      timelineItems(last: 50, itemTypes: [CLOSED_EVENT]) {
                          nodes {
                              ... on ClosedEvent {
                                  createdAt
                                  stateReason
                              }
                          }
                      }
                      projectItems(first: 5) {
                          nodes {
                              project {
                                  title
                                  id
                              }
                              fieldValues(first: 15) {
                                  nodes {
                                      ... on ProjectV2ItemFieldSingleSelectValue {
                                        field {
                                          ... on ProjectV2FieldCommon {
                                            name
                                          }
                                        }
                                        name
                                      }
                                      ... on ProjectV2ItemFieldDateValue {
                                          field {
                                            ... on ProjectV2FieldCommon {
                                              name
                                            }
                                          }
                                        date
                                      }
                                  }
                              }
                          }
                      }
                      subIssues(first: 100) {
                          nodes {
                              id
                          }
                      }
                  }
              }
          }
        """

        variables: dict[str, Any] = {
            "owner": owner,
            "name": repository_name, "issueNumber": issue_number
        }

        response: dict[str, Any] = self.query(query, variables)
        issue = Issue.from_graphql_response(response.get(
            "data", {}).get("repository", {}).get("issue", {}))
        return issue

    def get_issue_details_list(self, issue_ids: List[str]) -> List[Issue]:
        """Get detailed information about a list of GitHub issues.

        Args:
            issue_ids: List of issue IDs

        Returns:
            An Issue object list with relevant details
        """

        query = """
            query($issueIds: [ID!]!) {
                nodes(ids: $issueIds) {
                    ... on Issue {
                        id
                        title
                        state
                        body
                        url
                        comments(last: 50, orderBy: {field: UPDATED_AT, direction: ASC}) {
                            nodes {
                                id
                                body
                                createdAt
                                url
                            }
                            totalCount
                        }
                        labels(first: 10) {
                            nodes {
                                name
                                description
                            }
                        }
                        timelineItems(last: 50, itemTypes: [CLOSED_EVENT]) {
                            nodes {
                                ... on ClosedEvent {
                                    createdAt
                                    stateReason
                                }
                            }
                        }
                        projectItems(first: 5) {
                            nodes {
                                project {
                                    title
                                    number
                                }
                                fieldValues(first: 15) {
                                    nodes {
                                        ... on ProjectV2ItemFieldSingleSelectValue {
                                            field {
                                                ... on ProjectV2FieldCommon {
                                                    name
                                                }
                                            }
                                            name
                                        }
                                        ... on ProjectV2ItemFieldDateValue {
                                            field {
                                                ... on ProjectV2FieldCommon {
                                                    name
                                                }
                                            }
                                            date
                                        }
                                    }
                                }
                            }
                        }
                        subIssues(first: 100) {
                            nodes {
                                id
                            }
                        }
                    }
                }
            }
        """

        variables: dict[str, Any] = {
            "issueIds": issue_ids
        }

        response: dict[str, Any] = self.query(query, variables)
        issues: List[Issue] = []
        for issue_data in response.get("data", {}).get("nodes", {}):
            issues.append(Issue.from_graphql_response(issue_data))
        return issues



from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class IssueState(Enum):
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    NONE = "None"

    @classmethod
    def from_github_reason(cls, reason: str) -> "IssueState":
        mapping = {
            "COMPLETED": cls.COMPLETED,
            "CLOSED": cls.CLOSED,
            "OPEN": cls.OPEN,
        }
        return mapping.get(reason, cls.NONE)


class StateReason(Enum):
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    NOT_PLANNED = "NOT_PLANNED"
    DUPLICATE = "DUPLICATE"
    REOPENED = "REOPENED"
    NONE = "None"

    @classmethod
    def from_github_reason(cls, reason: str) -> "StateReason":
        mapping = {
            "COMPLETED": cls.COMPLETED,
            "CLOSED": cls.CLOSED,
            "NOT_PLANNED": cls.NOT_PLANNED,
            "DUPLICATE": cls.DUPLICATE,
            "REOPENED": cls.REOPENED,
        }
        return mapping.get(reason, cls.NONE)


@dataclass
class TimeLineItem:
    createdAt: datetime
    stateReason: StateReason


@dataclass
class IssueComment:
    comment_id: str
    body: str
    createdAt: datetime
    url: str


@dataclass
class FieldValue:
    name: str
    value: str


@dataclass
class IssueLabel:
    name: str
    description: str


@dataclass
class ProjectDetails:
    project_id: str
    name: str
    fieldValues: List[FieldValue]


@dataclass
class Issue:
    issue_id: str
    title: str
    state: IssueState
    stateChange: IssueState
    body: str
    url: str
    projects: List[ProjectDetails]
    labels: List[IssueLabel]
    comments: List[IssueComment]
    timeLineItems: List[TimeLineItem]
    subIssueIds: List[str]

    @classmethod
    def from_graphql_project_query(cls, data: Dict[str, Any], project_id: str, project_title: str) -> "Issue":
        # Implementation for project list queries
        issueData = data.get("content", {})
        fieldData = data.get("fieldValues", {})
        issue = Issue.from_graphql_response(issueData)
        issue.projects = [
            ProjectDetails(
                project_id=project_id,
                name=project_title,
                fieldValues=[
                    FieldValue(
                        name=field["field"]["name"],
                        value=field["name"],
                    )
                    for field in fieldData.get("nodes", [])
                    if field.get("field") and field.get("name")
                ],
            )
        ]
        return issue

    @classmethod
    def from_graphql_response(
        cls, data: Dict[str, Any]
    ) -> "Issue":

        return cls(
            issue_id=data.get("id", ""),
            title=data.get("title", ""),
            state=IssueState.from_github_reason(data.get("state", "")),
            # No since date, so stateChange is the same as state
            stateChange=IssueState.from_github_reason(data.get("state", "")),
            body=data.get("body", ""),
            url=data.get("url", ""),
            projects=[
                ProjectDetails(
                    project_id=project["project"]["id"],
                    name=project["project"]["title"],
                    fieldValues=[
                        FieldValue(
                            name=field["field"]["name"],
                            value=field["name"],
                        )
                        for field in project.get("fieldValues", {}).get("nodes", [])
                        if field.get("field") and field.get("name")
                    ],
                )
                for project in data.get("projectItems", {}).get("nodes", [])
                if project.get("project")
            ],
            labels=[
                IssueLabel(
                    name=label["name"],
                    description=label.get("description", "")
                )
                for label in data.get("labels", {}).get("nodes", [])
                if label.get("name")
            ],
            comments=[
                IssueComment(
                    comment_id=comment["id"],
                    body=comment["body"],
                    createdAt=datetime.fromisoformat(
                        comment["createdAt"].rstrip("Z")),
                    url=comment["url"],
                )
                for comment in data.get("comments", {}).get("nodes", [])
            ],
            timeLineItems=[
                TimeLineItem(
                    createdAt=datetime.fromisoformat(
                        item["createdAt"].rstrip("Z")),
                    stateReason=StateReason.from_github_reason(
                        item.get("stateReason", "None")
                    ),
                )
                for item in data.get("timelineItems", {}).get("nodes", [])
                if item.get("createdAt") and item.get("stateReason")
            ],
            subIssueIds=[
                sub_issue["id"]
                for sub_issue in data.get("subIssues", {}).get("nodes", [])
                if sub_issue.get("id")
            ],
        )

    def filter_comments_since(self, since: datetime) -> None:
        self.comments = [
            comment for comment in self.comments if comment.createdAt >= since
        ]

    def get_field_value(self, field_name: str) -> Optional[str]:
        # Retrieves the first occurrence of a field value by name across all projects.
        # You can filter by projects if there are multiple projects associated with the issue.
        for project in self.projects:
            for field in project.fieldValues:
                if field.name == field_name:
                    return field.value
        return None

    def format_issue_details(self) -> str:
        details = [
            f"Issue ID: {self.issue_id}",
            f"Title: {self.title}",
            f"State: {self.state.value}",
            f"URL: {self.url}",
            f"Body:\n{self.body}\n",
            "Fields:",
        ]
        for project in self.projects:
            for field in project.fieldValues:
                details.append(f"  - {field.name}: {field.value}")
        details.append("Labels:")
        for label in self.labels:
            details.append(f"  - {label.name}: {label.description}")
        details.append("Comments:")
        for comment in self.comments:
            details.append(
                f"  - [{comment.createdAt.isoformat()}] {comment.body} (URL: {comment.url})"
            )
        details.append("Timeline Items:")
        for item in self.timeLineItems:
            details.append(
                f"  - [{item.createdAt.isoformat()}] State Reason: {item.stateReason.value}"
            )
        if self.subIssueIds:
            details.append("Sub-Issue IDs:")
            for sub_id in self.subIssueIds:
                details.append(f"  - {sub_id}")
        return "\n".join(details)

    def calculate_issue_state_change(self, since: datetime) -> None:
        for item in self.timeLineItems:
            if item.stateReason != StateReason.NONE and item.createdAt >= since:
                self.stateChange = IssueState.from_github_reason(
                    item.stateReason.value
                )

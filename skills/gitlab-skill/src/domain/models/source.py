from pydantic import BaseModel


class GitLabSource(BaseModel):
    id: str
    title: str
    url: str
    source_type: str
    snippet: str
    description: str
    matched_query: str
    repository_id: str
    project_path: str
    file_path: str
    ref: str
    line: int | None = None

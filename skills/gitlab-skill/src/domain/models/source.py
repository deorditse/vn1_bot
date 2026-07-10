from pydantic import BaseModel


class GitLabSource(BaseModel):
    id: str
    title: str
    url: str
    source_type: str
    snippet: str


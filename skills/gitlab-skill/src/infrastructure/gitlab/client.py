class GitLabClient:
    """Thin adapter for future GitLab API integration."""

    async def search(self, query: str) -> list[dict]:
        raise NotImplementedError("GitLab API integration is not implemented yet")


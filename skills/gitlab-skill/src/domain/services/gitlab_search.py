from domain.models.source import GitLabSource


class GitLabSearchService:
    async def search(self, query: str) -> list[GitLabSource]:
        if not query.strip():
            return []

        # TODO: replace with GitLab API adapter from infrastructure/gitlab.
        return [
            GitLabSource(
                id="gitlab-placeholder-1",
                title="GitLab search placeholder",
                url="https://gitlab.example.local/search",
                source_type="placeholder",
                snippet=f"Query accepted for future GitLab search: {query}",
            )
        ]


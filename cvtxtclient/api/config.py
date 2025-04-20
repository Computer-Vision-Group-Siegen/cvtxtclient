class APIConfig:
    """Basic configuration for the API client."""

    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url
        """URL for the API server."""
        self.api_key = api_key
        """API key for authentication."""
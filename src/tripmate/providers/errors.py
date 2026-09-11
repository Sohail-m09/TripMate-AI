class ProviderError(Exception):
    """Base exception for external provider errors."""


class ProviderConnectionError(ProviderError):
    """Raised when TripMate cannot connect to a provider."""


class ProviderResponseError(ProviderError):
    """Raised when a provider returns an invalid or failed response."""
"""Custom exceptions for envresolve."""


class EnvResolveError(Exception):
    """Base exception for all envresolve errors."""


class CircularReferenceError(EnvResolveError):
    """Raised when a circular reference is detected in variable expansion."""

    def __init__(self, variable_name: str, chain: list[str] | None = None) -> None:
        """Initialize CircularReferenceError.

        Args:
            variable_name: The variable that caused the circular reference
            chain: Optional list showing the reference chain
        """
        self.variable_name = variable_name
        self.chain = chain or []
        chain_str = " -> ".join(self.chain) if self.chain else variable_name
        msg = f"Circular reference detected: {chain_str}"
        super().__init__(msg)


class VariableNotFoundError(EnvResolveError):
    """Raised when a referenced variable is not found in the environment."""

    def __init__(self, variable_name: str) -> None:
        """Initialize VariableNotFoundError.

        Args:
            variable_name: The variable that was not found
        """
        self.variable_name = variable_name
        super().__init__(f"Variable not found: {variable_name}")


class URIParseError(EnvResolveError):
    """Raised when a secret URI cannot be parsed."""

    def __init__(self, message: str, uri: str | None = None) -> None:
        """Initialize URIParseError.

        Args:
            message: Error message describing the parsing failure
            uri: The URI that failed to parse (optional)
        """
        self.uri = uri
        full_message = f"{message}: {uri}" if uri else message
        super().__init__(full_message)


class SecretResolutionError(EnvResolveError):
    """Raised when a secret cannot be resolved from its provider."""

    def __init__(
        self, message: str, uri: str, original_error: Exception | None = None
    ) -> None:
        """Initialize SecretResolutionError.

        Args:
            message: Error message describing the resolution failure
            uri: The URI that failed to resolve
            original_error: The original exception that caused this error (optional)
        """
        self.uri = uri
        self.original_error = original_error
        full_message = f"{message}: {uri}"
        if original_error:
            full_message = f"{full_message} (caused by: {original_error})"
        super().__init__(full_message)


class ProviderRegistrationError(EnvResolveError):
    """Raised when a provider registration fails."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        """Initialize ProviderRegistrationError.

        Args:
            message: Error message describing the registration failure
            original_error: The original exception that caused this error (optional)
        """
        self.original_error = original_error
        super().__init__(message)


class MutuallyExclusiveArgumentsError(EnvResolveError, TypeError):
    """Raised when mutually exclusive arguments are specified together."""

    def __init__(self, arg1: str, arg2: str) -> None:
        """Initialize MutuallyExclusiveArgumentsError.

        Args:
            arg1: First mutually exclusive argument name
            arg2: Second mutually exclusive argument name
        """
        self.arg1 = arg1
        self.arg2 = arg2
        msg = (
            f"Arguments '{arg1}' and '{arg2}' are mutually exclusive. "
            f"Specify either '{arg1}' or '{arg2}', but not both."
        )
        super().__init__(msg)

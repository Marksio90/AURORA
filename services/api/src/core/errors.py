"""Custom exceptions following RFC 7807 (Problem Details for HTTP APIs)."""

from typing import Any


class AppException(Exception):
    """Base application exception with problem+json support."""

    def __init__(
        self,
        title: str,
        detail: str,
        status: int = 500,
        type_uri: str = "about:blank",
        instance: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize exception with RFC 7807 fields.

        Args:
            title: Short, human-readable summary
            detail: Human-readable explanation
            status: HTTP status code
            type_uri: URI reference that identifies the problem type
            instance: URI reference that identifies the specific occurrence
            **kwargs: Additional problem details
        """
        self.title = title
        self.detail = detail
        self.status = status
        self.type_uri = type_uri
        self.instance = instance
        self.extensions = kwargs
        super().__init__(detail)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to problem+json format."""
        problem = {
            "type": self.type_uri,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
        }
        if self.instance:
            problem["instance"] = self.instance
        problem.update(self.extensions)
        return problem


class DatabaseException(AppException):
    """Operacja na bazie danych nie powiodła się."""

    def __init__(self, detail: str, **kwargs: Any) -> None:
        super().__init__(
            title="Błąd bazy danych",
            detail=detail,
            status=500,
            type_uri="https://decisioncalm.ai/errors/database",
            **kwargs,
        )


class OpenAIException(AppException):
    """Wywołanie API OpenAI nie powiodło się."""

    def __init__(self, detail: str, **kwargs: Any) -> None:
        super().__init__(
            title="Błąd usługi AI",
            detail=detail,
            status=503,
            type_uri="https://decisioncalm.ai/errors/ai-service",
            **kwargs,
        )


class ContentSafetyException(AppException):
    """Treść nie przeszła walidacji bezpieczeństwa."""

    def __init__(self, detail: str, blocked_reason: str, **kwargs: Any) -> None:
        super().__init__(
            title="Naruszenie bezpieczeństwa treści",
            detail=detail,
            status=400,
            type_uri="https://decisioncalm.ai/errors/content-safety",
            blocked_reason=blocked_reason,
            **kwargs,
        )


class ValidationException(AppException):
    """Walidacja danych wejściowych nie powiodła się."""

    def __init__(self, detail: str, field: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            title="Błąd walidacji",
            detail=detail,
            status=422,
            type_uri="https://decisioncalm.ai/errors/validation",
            field=field,
            **kwargs,
        )


class NotFoundException(AppException):
    """Zasób nie został znaleziony."""

    def __init__(self, detail: str, resource_type: str, **kwargs: Any) -> None:
        super().__init__(
            title="Zasób nie znaleziony",
            detail=detail,
            status=404,
            type_uri="https://decisioncalm.ai/errors/not-found",
            resource_type=resource_type,
            **kwargs,
        )

class AppError(Exception):
    """Base class for app-level errors."""


class ValidationError(AppError):
    """For bad input or business rule violations."""


class AuthorizationError(AppError):
    """User is not allowed to perform this action."""


class NotFoundError(AppError):
    """Requested resource (user, portfolio, security, etc.) was not found."""


class PortfolioNotEmptyError(AppError):
    """Trying to delete a portfolio that still has holdings."""

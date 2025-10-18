from .deps import (
    get_active_user,
    # Convenience aliases
    get_authenticated_user,
    get_current_active_superuser,
    get_current_active_user,
    get_current_active_verified_user,
    get_current_user,
    get_current_user_optional,
    get_user_email,
    get_user_id,
    # Utility functions
    is_user_authenticated,
    require_user_role,
)
from .deps_legacy import (
    get_current_active_superuser_legacy,
    get_current_active_user_legacy,
    get_current_active_verified_user_legacy,
    get_current_user_legacy,
)
from .middleware import AuthMiddleware
from .models import OAuthAccount, User

__all__ = [
    # Core dependencies
    "get_current_user",
    "get_current_user_optional",
    "get_current_active_user",
    "get_current_active_verified_user",
    "get_current_active_superuser",
    # Convenience aliases
    "get_authenticated_user",
    "get_active_user",
    # Utility functions
    "is_user_authenticated",
    "get_user_id",
    "get_user_email",
    "require_user_role",
    # Models and middleware
    "User",
    "OAuthAccount",
    "AuthMiddleware",

    # Legacy dependencies #TODO: To be removed after MSA transition complete
    "get_current_user_legacy",
    "get_current_active_user_legacy",
    "get_current_active_verified_user_legacy",
    "get_current_active_superuser_legacy",

]

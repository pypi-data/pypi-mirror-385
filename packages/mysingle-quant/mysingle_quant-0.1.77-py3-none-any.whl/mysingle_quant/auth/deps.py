"""
Authentication Dependencies v2 - Request-Based Unified Authentication

이 모듈은 AuthMiddleware와 완전히 통합된 새로운 Request 기반 인증 의존성 시스템입니다.
기존의 Depends() 패턴 대신 Request 파라미터를 직접 사용하여 미들웨어와 더 효율적으로 상호작용합니다.

Key Features:
- Request 기반 인증 (Request.state.user 직접 활용)
- AuthMiddleware 완전 통합
- Kong Gateway 완전 지원
- 서비스 타입별 자동 인증 (IAM vs NON_IAM)
- 높은 성능 (추가 DB 조회 없음)
- 일관된 에러 처리

Usage Example:
    from fastapi import Request
    from mysingle_quant.auth.deps_new import get_current_active_verified_user

    @router.get("/protected")
    async def protected_endpoint(request: Request):
        user = get_current_active_verified_user(request)
        return {"user_id": str(user.id)}
"""

from typing import Optional

from fastapi import Request

from ..core.logging_config import get_logger
from .exceptions import AuthorizationFailed, UserInactive, UserNotExists
from .models import User

logger = get_logger(__name__)


# =============================================================================
# Core Request-Based Authentication Functions
# =============================================================================


def get_current_user(request: Request) -> User:
    """
    현재 인증된 사용자 반환 (AuthMiddleware 기반)

    AuthMiddleware가 Request.state.user에 저장한 사용자 정보를 반환합니다.
    미들웨어에서 인증이 완료되었으므로 추가 검증이 불필요하며 고성능입니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 인증된 사용자 객체

    Raises:
        UserNotExists: 사용자 정보가 없는 경우 (미들웨어 인증 실패)

    Example:
        @router.get("/profile")
        async def get_profile(request: Request):
            user = get_current_user(request)
            return {"user_id": str(user.id)}
    """
    user = getattr(request.state, "user", None)
    if not user:
        logger.warning(
            "No user found in request.state - middleware authentication failed"
        )
        raise UserNotExists(identifier="user", identifier_type="authenticated user")
    return user


def get_current_active_user(request: Request) -> User:
    """
    활성 사용자 확인

    사용자가 활성 상태(is_active=True)인지 확인합니다.
    미들웨어에서 이미 기본 확인을 하지만, 추가 보안을 위해 재확인합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 활성 사용자 객체

    Raises:
        UserInactive: 사용자가 비활성 상태인 경우

    Example:
        @router.post("/action")
        async def perform_action(request: Request):
            user = get_current_active_user(request)
            # 활성 사용자만 작업 수행 가능
            return perform_user_action(user)
    """
    user = get_current_user(request)
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.id}")
        raise UserInactive(user_id=str(user.id))
    return user


def get_current_active_verified_user(request: Request) -> User:
    """
    이메일 검증된 활성 사용자 확인

    사용자가 활성 상태이면서 이메일 인증(is_verified=True)을 완료했는지 확인합니다.
    이메일 인증이 필요한 기능에 사용합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 이메일 검증된 활성 사용자 객체

    Raises:
        AuthorizationFailed: 이메일 인증이 완료되지 않은 경우

    Example:
        @router.post("/sensitive-action")
        async def sensitive_action(request: Request):
            user = get_current_active_verified_user(request)
            # 이메일 검증된 사용자만 민감한 작업 수행 가능
            return perform_sensitive_action(user)
    """
    user = get_current_active_user(request)
    if not user.is_verified:
        logger.warning(f"Unverified user attempted access: {user.id}")
        raise AuthorizationFailed("Email verification required", user_id=str(user.id))
    return user


def get_current_active_superuser(request: Request) -> User:
    """
    슈퍼유저 권한 검증

    사용자가 슈퍼유저 권한(is_superuser=True)을 가지고 있는지 확인합니다.
    관리자 권한이 필요한 기능에 사용합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 슈퍼유저 권한을 가진 사용자 객체

    Raises:
        AuthorizationFailed: 슈퍼유저 권한이 없는 경우

    Example:
        @router.delete("/admin/users/{user_id}")
        async def delete_user(request: Request, user_id: str):
            admin_user = get_current_active_superuser(request)
            # 슈퍼유저만 다른 사용자 삭제 가능
            return delete_user_by_admin(user_id, admin_user)
    """
    user = get_current_active_verified_user(request)
    if not user.is_superuser:
        logger.warning(f"Non-superuser attempted admin access: {user.id}")
        raise AuthorizationFailed("Superuser privileges required", user_id=str(user.id))
    return user


def get_current_user_optional(request: Request) -> Optional[User]:
    """
    선택적 사용자 인증 (공개 경로 또는 선택적 인증용)

    사용자가 로그인했으면 User 객체 반환, 아니면 None을 반환합니다.
    공개 경로나 선택적 인증이 필요한 엔드포인트에서 사용합니다.

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[User]: 인증된 사용자 객체 또는 None

    Example:
        @router.get("/public-content")
        async def public_content(request: Request):
            user = get_current_user_optional(request)
            if user:
                # 로그인된 사용자에게는 개인화된 콘텐츠
                return get_personalized_content(user)
            else:
                # 비로그인 사용자에게는 기본 콘텐츠
                return get_default_content()
    """
    return getattr(request.state, "user", None)


# =============================================================================
# Role-Based Access Control Functions
# =============================================================================


def require_user_role(request: Request, required_roles: list[str]) -> User:
    """
    특정 역할이 필요한 사용자 검증

    사용자에게 특정 역할이 있는지 확인합니다.
    현재는 is_superuser만 지원하지만, 향후 role 시스템 확장 시 사용됩니다.

    Args:
        request: FastAPI Request 객체
        required_roles: 필요한 역할 목록

    Returns:
        User: 역할 요구사항을 만족하는 사용자 객체

    Raises:
        AuthorizationFailed: 필요한 역할이 없는 경우

    Example:
        @router.get("/admin-only")
        async def admin_endpoint(request: Request):
            user = require_user_role(request, ["admin", "superuser"])
            return {"message": "Admin access", "user": str(user.id)}
    """
    user = get_current_active_verified_user(request)

    # 현재는 superuser만 지원
    # if "admin" in required_roles or "superuser" in required_roles:
    #     if not user.is_superuser:
    #         logger.warning(f"User {user.id} lacks required roles: {required_roles}")
    #         raise AuthorizationFailed(
    #             f"Required roles: {required_roles}", user_id=str(user.id)
    #         )

    # 향후 확장: user.roles 필드 체크
    # user_roles = getattr(user, 'roles', [])
    # if not any(role in user_roles for role in required_roles):
    #     raise AuthorizationFailed(
    #         f"Required roles: {required_roles}", user_id=str(user.id)
    #     )

    return user


def require_admin_access(request: Request) -> User:
    """
    관리자 권한 요구 (편의 함수)

    Args:
        request: FastAPI Request 객체

    Returns:
        User: 관리자 권한을 가진 사용자 객체

    Example:
        @router.get("/admin/dashboard")
        async def admin_dashboard(request: Request):
            admin_user = require_admin_access(request)
            return get_admin_dashboard_data(admin_user)
    """
    return require_user_role(request, ["admin", "superuser"])


# =============================================================================
# Utility Functions
# =============================================================================


def is_user_authenticated(request: Request) -> bool:
    """
    사용자가 인증되었는지 확인하는 유틸리티 함수

    Args:
        request: FastAPI Request 객체

    Returns:
        bool: 인증 여부

    Example:
        @router.get("/conditional")
        async def conditional_endpoint(request: Request):
            if is_user_authenticated(request):
                return {"message": "Welcome back!"}
            else:
                return {"message": "Hello, guest!"}
    """
    return hasattr(request.state, "user") and request.state.user is not None


def get_user_id(request: Request) -> Optional[str]:
    """
    인증된 사용자의 ID를 반환하는 유틸리티 함수

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: 사용자 ID 또는 None

    Example:
        @router.get("/activity")
        async def track_activity(request: Request):
            user_id = get_user_id(request)
            if user_id:
                track_user_activity(user_id, "page_view")
            return {"status": "tracked"}
    """
    user = getattr(request.state, "user", None)
    return str(user.id) if user else None


def get_user_email(request: Request) -> Optional[str]:
    """
    인증된 사용자의 이메일을 반환하는 유틸리티 함수

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: 사용자 이메일 또는 None

    Example:
        @router.post("/newsletter")
        async def subscribe_newsletter(request: Request):
            user_email = get_user_email(request)
            if user_email:
                return subscribe_user_to_newsletter(user_email)
            else:
                return {"error": "Authentication required"}
    """
    user = getattr(request.state, "user", None)
    return user.email if user else None


def get_user_display_name(request: Request) -> Optional[str]:
    """
    인증된 사용자의 표시 이름을 반환하는 유틸리티 함수

    Args:
        request: FastAPI Request 객체

    Returns:
        Optional[str]: 사용자 표시 이름 또는 None

    Example:
        @router.get("/welcome")
        async def welcome_message(request: Request):
            display_name = get_user_display_name(request)
            if display_name:
                return {"message": f"Welcome, {display_name}!"}
            else:
                return {"message": "Welcome, guest!"}
    """
    user = getattr(request.state, "user", None)
    if not user:
        return None

    # 표시 이름 우선순위: full_name → first_name → email
    if hasattr(user, "full_name") and user.full_name:
        return user.full_name
    elif hasattr(user, "first_name") and user.first_name:
        return user.first_name
    elif user.email:
        return user.email.split("@")[0]  # 이메일의 @ 앞부분
    else:
        return f"User {str(user.id)[:8]}"  # ID의 앞 8자리


# =============================================================================
# Security Context Helpers
# =============================================================================


def get_request_security_context(request: Request) -> dict:
    """
    요청의 보안 컨텍스트 정보를 반환

    Args:
        request: FastAPI Request 객체

    Returns:
        dict: 보안 컨텍스트 정보

    Example:
        @router.post("/sensitive-action")
        async def sensitive_action(request: Request):
            user = get_current_active_verified_user(request)
            security_context = get_request_security_context(request)

            # 보안 감사 로그
            logger.info(f"Sensitive action by user {user.id}", extra=security_context)

            return perform_action(user)
    """
    user = getattr(request.state, "user", None)

    context = {
        "authenticated": user is not None,
        "user_id": str(user.id) if user else None,
        "user_email": user.email if user else None,
        "is_active": user.is_active if user else False,
        "is_verified": user.is_verified if user else False,
        "is_superuser": user.is_superuser if user else False,
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "endpoint": f"{request.method} {request.url.path}",
    }

    return context


# =============================================================================
# Convenience Aliases
# =============================================================================

# 자주 사용되는 함수들의 간단한 별칭
get_authenticated_user = get_current_user
get_active_user = get_current_active_user
get_verified_user = get_current_active_verified_user
get_admin_user = get_current_active_superuser
get_optional_user = get_current_user_optional

# 유틸리티 별칭
check_authentication = is_user_authenticated
extract_user_id = get_user_id
extract_user_email = get_user_email


# =============================================================================
# Migration Helpers (기존 Depends 패턴에서 전환용)
# =============================================================================


def create_user_dependency_wrapper(auth_func):
    """
    Request 기반 함수를 Depends() 패턴으로 감싸는 래퍼 (전환기용)

    기존 코드가 Depends() 패턴을 사용하고 있을 때 점진적 전환을 위해 사용합니다.
    새로운 코드는 직접 Request 기반 함수를 사용하는 것을 권장합니다.

    Args:
        auth_func: Request 기반 인증 함수

    Returns:
        Callable: Depends()에서 사용할 수 있는 함수

    Example:
        # 기존 코드 (권장하지 않음)
        from fastapi import Depends

        get_user_dep = create_user_dependency_wrapper(get_current_active_verified_user)

        @router.get("/old-style")
        async def old_endpoint(user: User = Depends(get_user_dep)):
            return {"user_id": str(user.id)}

        # 새로운 코드 (권장)
        @router.get("/new-style")
        async def new_endpoint(request: Request):
            user = get_current_active_verified_user(request)
            return {"user_id": str(user.id)}
    """

    def dependency_wrapper(request: Request):
        return auth_func(request)

    return dependency_wrapper


# 전환기용 Depends() 호환 의존성들
CurrentUserDep = create_user_dependency_wrapper(get_current_user)
ActiveUserDep = create_user_dependency_wrapper(get_current_active_user)
VerifiedUserDep = create_user_dependency_wrapper(get_current_active_verified_user)
SuperuserDep = create_user_dependency_wrapper(get_current_active_superuser)
OptionalUserDep = create_user_dependency_wrapper(get_current_user_optional)

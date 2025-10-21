from beanie import PydanticObjectId
from fastapi import APIRouter, Request, Response, status

from ..deps import get_current_active_superuser, get_current_active_verified_user
from ..exceptions import (
    UserNotExists,
)
from ..schemas import UserResponse, UserUpdate
from ..user_manager import UserManager

user_manager = UserManager()


def get_users_router() -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()

    @router.get(
        "/me",
        response_model=UserResponse,
    )
    async def get_user_me(
        request: Request,
    ) -> UserResponse:
        current_user = get_current_active_verified_user(request)
        return UserResponse.model_validate(current_user, from_attributes=True)

    @router.patch(
        "/me",
        response_model=UserResponse,
    )
    async def update_user_me(
        request: Request,
        obj_in: UserUpdate,
    ) -> UserResponse:
        current_user = get_current_active_verified_user(request)
        # UserManager.update에서 이미 적절한 예외를 발생시키므로
        # 직접 전파하도록 수정
        user = await user_manager.update(obj_in, current_user, request=request)
        return UserResponse.model_validate(user, from_attributes=True)

    @router.get(
        "/{id}",
        response_model=UserResponse,
    )
    async def get_user(request: Request, id: PydanticObjectId) -> UserResponse:
        # 슈퍼유저 권한 확인
        get_current_active_superuser(request)
        user = await user_manager.get(id)
        if user is None:
            raise UserNotExists(identifier=str(id), identifier_type="user")
        return UserResponse.model_validate(user)

    @router.patch(
        "/{id}",
        response_model=UserResponse,
    )
    async def update_user(
        request: Request,
        id: PydanticObjectId,
        obj_in: UserUpdate,  # type: ignore
    ) -> UserResponse:
        # 슈퍼유저 권한 확인
        get_current_active_superuser(request)
        user = await user_manager.get(id)
        if user is None:
            raise UserNotExists(identifier=str(id), identifier_type="user")
        updated_user = await user_manager.update(obj_in, user, request=request)
        return UserResponse.model_validate(updated_user, from_attributes=True)

    @router.delete(
        "/{id}",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
    )
    async def delete_user(
        request: Request,
        id: PydanticObjectId,
    ) -> None:
        # 슈퍼유저 권한 확인
        get_current_active_superuser(request)
        user = await user_manager.get(id)
        if user is None:
            raise UserNotExists(identifier=str(id), identifier_type="user")
        await user_manager.delete(user, request=request)
        return None

    return router

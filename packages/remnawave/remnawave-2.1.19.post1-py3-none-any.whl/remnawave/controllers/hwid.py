from typing import Annotated
from uuid import UUID

from remnawave.models import (
    CreateUserHwidDeviceResponseDto,
    DeleteUserHwidDeviceResponseDto,
    GetUserHwidDevicesResponseDto,
    GetHwidStatisticsResponseDto,
    CreateHWIDUser,
    HWIDDeleteRequest,
    DeleteUserAllHwidDeviceRequestDto
)
from rapid_api_client import Path, PydanticBody
from remnawave.rapid import AttributeBody, BaseController, post, get


class HWIDUserController(BaseController):
    @get("/hwid/devices", response_class=GetUserHwidDevicesResponseDto)
    async def get_hwid_users(
        self,
        size: Annotated[int | None, AttributeBody()] = None,
        start: Annotated[int | None, AttributeBody()] = None,
    ) -> GetUserHwidDevicesResponseDto:
        """Get all user HWID devices"""
        ...

    @get("/hwid/devices/stats", response_class=GetHwidStatisticsResponseDto)
    async def get_hwid_stats(
        self,
    ) -> GetHwidStatisticsResponseDto:
        """Get HWID statistics"""
        ...

    @post("/hwid/devices", response_class=CreateUserHwidDeviceResponseDto)
    async def add_hwid_to_users(
        self,
        body: Annotated[CreateHWIDUser, PydanticBody()],
    ) -> CreateUserHwidDeviceResponseDto:
        """Create a user HWID device"""
        ...

    @post("/hwid/devices/delete", response_class=DeleteUserHwidDeviceResponseDto)
    async def delete_hwid_to_user(
        self,
        body: Annotated[HWIDDeleteRequest, PydanticBody()],
    ) -> DeleteUserHwidDeviceResponseDto:
        """Delete a user HWID device"""
        ...

    @post("/hwid/devices/delete-all", response_class=DeleteUserHwidDeviceResponseDto)
    async def delete_all_hwid_user(
        self,
        body: Annotated[DeleteUserAllHwidDeviceRequestDto, PydanticBody()],
    ) -> DeleteUserHwidDeviceResponseDto:
        """Delete all user HWID devices"""
        ...

    @get("/hwid/devices/{uuid}", response_class=GetUserHwidDevicesResponseDto)
    async def get_hwid_user(
        self,
        uuid: Annotated[str, Path(description="UUID of the User")],
    ) -> GetUserHwidDevicesResponseDto:
        """Get a user HWID device"""
        ...

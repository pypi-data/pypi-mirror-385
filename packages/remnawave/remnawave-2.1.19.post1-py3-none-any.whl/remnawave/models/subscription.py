from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from remnawave.enums import TrafficLimitStrategy, UserStatus


class HappCrypto(BaseModel):
    crypto_link: str = Field(alias="cryptoLink")


class UserLastConnectedNodeDto(BaseModel):
    connected_at: datetime = Field(alias="connectedAt")
    node_name: str = Field(alias="nodeName")
    country_code: str = Field(alias="countryCode")


class ActiveInternalSquadDto(BaseModel):
    uuid: UUID
    name: str


class UserResponseDto(BaseModel):
    uuid: UUID
    short_uuid: str = Field(alias="shortUuid")
    username: str
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    used_traffic_bytes: float = Field(alias="usedTrafficBytes")
    lifetime_used_traffic_bytes: float = Field(alias="lifetimeUsedTrafficBytes")
    traffic_limit_bytes: int = Field(default=0, alias="trafficLimitBytes")
    traffic_limit_strategy: TrafficLimitStrategy = Field(
        default=TrafficLimitStrategy.NO_RESET, 
        alias="trafficLimitStrategy"
    )
    sub_last_user_agent: Optional[str] = Field(None, alias="subLastUserAgent")
    sub_last_opened_at: Optional[datetime] = Field(None, alias="subLastOpenedAt")
    expire_at: datetime = Field(alias="expireAt")
    online_at: Optional[datetime] = Field(None, alias="onlineAt")
    sub_revoked_at: Optional[datetime] = Field(None, alias="subRevokedAt")
    last_traffic_reset_at: Optional[datetime] = Field(None, alias="lastTrafficResetAt")
    trojan_password: str = Field(alias="trojanPassword")
    vless_uuid: UUID = Field(alias="vlessUuid")
    ss_password: str = Field(alias="ssPassword")
    description: Optional[str] = None
    tag: Optional[str] = None
    telegram_id: Optional[int] = Field(None, alias="telegramId")
    email: Optional[str] = None
    hwid_device_limit: Optional[int] = Field(None, alias="hwidDeviceLimit")
    first_connected_at: Optional[datetime] = Field(None, alias="firstConnectedAt")
    last_triggered_threshold: int = Field(default=0, alias="lastTriggeredThreshold")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    active_internal_squads: List[ActiveInternalSquadDto] = Field(alias="activeInternalSquads")
    subscription_url: str = Field(alias="subscriptionUrl")
    last_connected_node: Optional[UserLastConnectedNodeDto] = Field(None, alias="lastConnectedNode")
    happ: HappCrypto = Field(alias="happ")


class ConvertedUserInfo(BaseModel):
    days_left: int = Field(alias="daysLeft")
    traffic_limit: str = Field(alias="trafficLimit")
    traffic_used: str = Field(alias="trafficUsed")
    lifetime_traffic_used: str = Field(alias="lifetimeTrafficUsed")
    is_hwid_limited: bool = Field(alias="isHwidLimited")


class Passwords(BaseModel):
    ss_password: str = Field(alias="ssPassword")
    trojan_password: str = Field(alias="trojanPassword")
    vless_password: str = Field(alias="vlessPassword")


class RawHostAdditionalParams(BaseModel):
    mode: Optional[str] = None
    heartbeat_period: Optional[float] = Field(None, alias="heartbeatPeriod")


class RawHostProtocolOptions(BaseModel):
    class SSOptions(BaseModel):
        method: Optional[str] = None
    
    ss: Optional[SSOptions] = None


class RawHostDbData(BaseModel):
    raw_inbound: Optional[Dict[str, Any]] = Field(alias="rawInbound")
    inbound_tag: str = Field(alias="inboundTag")
    uuid: str
    config_profile_uuid: Optional[str] = Field(alias="configProfileUuid")
    config_profile_inbound_uuid: Optional[str] = Field(alias="configProfileInboundUuid")
    is_disabled: bool = Field(alias="isDisabled")
    view_position: int = Field(alias="viewPosition") 
    remark: str
    is_hidden: bool = Field(alias="isHidden")
    tag: Optional[str] = None
    vless_route_id: Optional[int] = Field(None, alias="vlessRouteId")


class RawHost(BaseModel):
    password: Passwords 
    address: Optional[str] = None
    alpn: Optional[str] = None
    fingerprint: Optional[str] = None
    host: Optional[str] = None
    network: Optional[str] = None
    path: Optional[str] = None
    public_key: Optional[str] = Field(None, alias="publicKey")
    port: Optional[float] = None  # изменен тип на float
    protocol: Optional[str] = None
    remark: Optional[str] = None
    short_id: Optional[str] = Field(None, alias="shortId")
    sni: Optional[str] = None
    spider_x: Optional[str] = Field(None, alias="spiderX")
    tls: Optional[str] = None
    header_type: Optional[str] = Field(None, alias="headerType")
    additional_params: Optional[RawHostAdditionalParams] = Field(None, alias="additionalParams")
    x_http_extra_params: Optional[Dict[str, Any]] = Field(None, alias="xHttpExtraParams")
    mux_params: Optional[Dict[str, Any]] = Field(None, alias="muxParams")
    sockopt_params: Optional[Dict[str, Any]] = Field(None, alias="sockoptParams")
    server_description: Optional[str] = Field(None, alias="serverDescription")
    flow: Optional[str] = None
    allow_insecure: Optional[bool] = Field(None, alias="allowInsecure")
    shuffle_host: Optional[bool] = Field(None, alias="shuffleHost")
    mihomo_x25519: Optional[bool] = Field(None, alias="mihomoX25519")
    mldsa65_verify: Optional[str] = Field(None, alias="mldsa65Verify")
    encryption: Optional[str] = None
    protocol_options: Optional[RawHostProtocolOptions] = Field(None, alias="protocolOptions")
    db_data: RawHostDbData = Field(alias="dbData")


class RawSubscriptionResponse(BaseModel):
    user: UserResponseDto
    converted_user_info: ConvertedUserInfo = Field(alias="convertedUserInfo")
    headers: Dict[str, str]
    raw_hosts: List[RawHost] = Field(alias="rawHosts")


class GetRawSubscriptionByShortUuidResponseDto(RawSubscriptionResponse):
    pass

# Legacy alias for backward compatibility
class UserSubscription(BaseModel):
    short_uuid: str = Field(alias="shortUuid")
    username: str
    days_left: int = Field(alias="daysLeft")
    traffic_used: str = Field(alias="trafficUsed")
    traffic_limit: str = Field(alias="trafficLimit")
    lifetime_traffic_used: str = Field(alias="lifetimeTrafficUsed")
    traffic_used_bytes: str = Field(alias="trafficUsedBytes")
    traffic_limit_bytes: str = Field(alias="trafficLimitBytes")
    lifetime_traffic_used_bytes: int = Field(alias="lifetimeTrafficUsedBytes")
    traffic_limit_strategy: TrafficLimitStrategy = Field(alias="trafficLimitStrategy")
    expires_at: datetime = Field(alias="expiresAt")
    user_status: UserStatus = Field(alias="userStatus")
    is_active: bool = Field(alias="isActive")


class SubscriptionInfoData(BaseModel):
    is_found: bool = Field(alias="isFound")
    user: UserSubscription
    links: List[str]
    ss_conf_links: Dict[str, str] = Field(alias="ssConfLinks")
    subscription_url: str = Field(alias="subscriptionUrl")
    happ: HappCrypto


class GetSubscriptionInfoResponseDto(BaseModel):
    is_found: bool = Field(alias="isFound")
    user: UserSubscription
    links: List[str]
    ss_conf_links: Dict[str, str] = Field(alias="ssConfLinks")
    subscription_url: str = Field(alias="subscriptionUrl")
    happ: HappCrypto


class SubscriptionWithoutHapp(BaseModel):
    is_found: bool = Field(alias="isFound")
    user: UserSubscription
    links: List[str]
    ss_conf_links: Dict[str, str] = Field(alias="ssConfLinks")
    subscription_url: str = Field(alias="subscriptionUrl")


class GetAllSubscriptionsResponseDto(BaseModel):
    subscriptions: List[SubscriptionWithoutHapp]
    total: float


class GetSubscriptionByUsernameResponseDto(BaseModel):
    is_found: bool = Field(alias="isFound")
    user: UserSubscription
    links: List[str]
    ss_conf_links: Dict[str, str] = Field(alias="ssConfLinks")
    subscription_url: str = Field(alias="subscriptionUrl")


class GetSubscriptionByShortUUIDResponseDto(GetSubscriptionByUsernameResponseDto):
    pass


class GetSubscriptionByUUIDResponseDto(GetSubscriptionByUsernameResponseDto):
    pass


# Legacy alias for backward compatibility
SubscriptionInfoResponseDto = GetSubscriptionInfoResponseDto
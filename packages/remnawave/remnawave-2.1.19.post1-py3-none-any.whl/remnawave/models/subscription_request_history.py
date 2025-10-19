from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionRequestHistoryRecord(BaseModel):
    id: int
    user_uuid: UUID = Field(alias="userUuid")
    request_ip: Optional[str] = Field(alias="requestIp")
    user_agent: Optional[str] = Field(alias="userAgent")
    request_at: datetime = Field(alias="requestAt")


class SubscriptionRequestHistoryData(BaseModel):
    records: List[SubscriptionRequestHistoryRecord]
    total: float


class GetAllSubscriptionRequestHistoryResponseDto(SubscriptionRequestHistoryData):
    pass


class AppStatItem(BaseModel):
    app: str
    count: float


class HourlyRequestStat(BaseModel):
    date_time: datetime = Field(alias="dateTime")
    request_count: float = Field(alias="requestCount")


class SubscriptionRequestHistoryStatsData(BaseModel):
    by_parsed_app: List[AppStatItem] = Field(alias="byParsedApp")
    hourly_request_stats: List[HourlyRequestStat] = Field(alias="hourlyRequestStats")


class GetSubscriptionRequestHistoryStatsResponseDto(SubscriptionRequestHistoryStatsData):
    pass
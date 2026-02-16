from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# ─── Auth ───
class UserRegister(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    plan_type: str
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── SNS Account ───
class SnsAccountCreate(BaseModel):
    platform: str
    access_token: str
    access_token_secret: Optional[str] = None  # X OAuth 1.0a用
    refresh_token: Optional[str] = None
    account_name: Optional[str] = None


class SnsAccountResponse(BaseModel):
    id: str
    platform: str
    account_name: Optional[str] = None
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Genre ───
class GenreCreate(BaseModel):
    genre_name: str
    keywords: List[str] = []


class GenreResponse(BaseModel):
    id: str
    genre_name: str
    keywords: object  # JSON field, can be list or str

    model_config = {"from_attributes": True}


# ─── Schedule ───
class ScheduleCreate(BaseModel):
    time: str
    frequency: str = "daily"


class ScheduleResponse(BaseModel):
    id: str
    time: str
    frequency: str

    model_config = {"from_attributes": True}


# ─── Post ───
class PostGenerateRequest(BaseModel):
    genre: Optional[str] = None
    platform: str = "x"


class PostResponse(BaseModel):
    id: str
    platform: str
    content: str
    status: str
    posted_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Affiliate Account ───
class AffiliateAccountCreate(BaseModel):
    platform: str
    tracking_id: str


class AffiliateAccountResponse(BaseModel):
    id: str
    platform: str
    tracking_id: str

    model_config = {"from_attributes": True}


# ─── Affiliate Offer ───
class AffiliateOfferCreate(BaseModel):
    title: str
    affiliate_url: str
    genre: Optional[str] = None


class AffiliateOfferResponse(BaseModel):
    id: str
    title: str
    affiliate_url: str
    genre: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Analytics ───
class PostAnalyticsResponse(BaseModel):
    id: str
    post_id: str
    likes: int
    reposts: int
    comments: int
    views: int

    model_config = {"from_attributes": True}


# ─── Short Link ───
class ShortLinkCreate(BaseModel):
    original_url: str


class ShortLinkResponse(BaseModel):
    id: str
    original_url: str
    short_code: str

    model_config = {"from_attributes": True}


# ─── Revenue ───
class RevenueResponse(BaseModel):
    id: str
    amount: float
    recorded_at: datetime

    model_config = {"from_attributes": True}


# ─── Dashboard Stats ───
class DashboardStats(BaseModel):
    total_posts: int
    total_clicks: int
    total_revenue: float
    ctr: float
    recent_posts: List[PostResponse]


class AffiliateStats(BaseModel):
    total_clicks: int
    total_revenue: float
    ctr: float
    offers: List[AffiliateOfferResponse]


# ─── Trends ───
class TrendItem(BaseModel):
    source: str
    title: str
    description: str = ""
    score: float = 0.0
    url: str = ""
    category: Optional[str] = None


class TrendsResponse(BaseModel):
    google_trends: List[TrendItem]
    news: List[TrendItem]
    x_buzz: List[TrendItem]
    top_keywords: List[str]


# ─── Autopilot ───
class AutopilotStatus(BaseModel):
    enabled: bool
    user_id: str


class AutopilotToggle(BaseModel):
    enabled: bool

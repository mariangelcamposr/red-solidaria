from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from .models import DonationStatus, MatchStatus, TransactionStatus, UserRole, AccountStatus, RequestStatus, Priority


def blank_to_none(value):
    """Convierte campos opcionales enviados como texto vacío desde formularios en None."""
    return None if value == "" else value


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=5, max_length=40)
    address: str = Field(min_length=3, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=100)
    postal_code: Optional[str] = None
    role: UserRole = UserRole.PARTICULAR
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    terms_accepted: bool
    privacy_accepted: bool

    @field_validator("postal_code", "latitude", "longitude", mode="before")
    @classmethod
    def normalize_optional_values(cls, value):
        return blank_to_none(value)


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    address: str
    city: str
    state: str
    country: str
    postal_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    role: UserRole
    status: AccountStatus
    email_verified: bool
    reputation_score: float
    ratings_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class VerifyOut(BaseModel):
    message: str


class DonationCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=3, max_length=500)
    resource_type: str
    category: str
    quantity: float = Field(gt=0)
    condition: str
    location: str = Field(min_length=2, max_length=200)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    expiry_date: Optional[datetime] = None
    presentation: Optional[str] = None
    package_condition: Optional[str] = None
    delivery_conditions: str = Field(min_length=3, max_length=300)
    is_urgent: bool = False

    @field_validator("latitude", "longitude", "expiry_date", "presentation", "package_condition", mode="before")
    @classmethod
    def normalize_optional_values(cls, value):
        return blank_to_none(value)


class DonationOut(DonationCreate):
    id: int
    donor_id: int
    status: DonationStatus
    rejection_reason: Optional[str] = None
    image_path: Optional[str] = None
    ai_analysis_result: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RequestCreate(BaseModel):
    resource_type: str
    category: str
    quantity: float = Field(gt=0)
    justification: str = Field(min_length=20, max_length=1000)
    location: str = Field(min_length=2, max_length=200)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    priority: Priority = Priority.MEDIUM
    expires_at: Optional[datetime] = None

    @field_validator("latitude", "longitude", "expires_at", mode="before")
    @classmethod
    def normalize_optional_values(cls, value):
        return blank_to_none(value)


class RequestOut(RequestCreate):
    id: int
    requester_id: int
    status: RequestStatus
    image_path: Optional[str] = None
    created_at: datetime
    active: bool

    class Config:
        from_attributes = True


class MatchOut(BaseModel):
    id: int
    donation_id: int
    request_id: int
    requester_id: int
    score: float
    distance_km: Optional[float]
    criteria: Optional[str]
    status: MatchStatus
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class MessageOut(BaseModel):
    id: int
    match_id: int
    sender_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    delivery_details: str = Field(min_length=5, max_length=500)


class TransactionCoordinate(BaseModel):
    delivery_details: str = Field(min_length=5, max_length=500)


class TransactionOut(BaseModel):
    id: int
    match_id: int
    donation_id: int
    donor_id: int
    requester_id: int
    delivery_details: Optional[str]
    status: TransactionStatus
    donor_confirmed: bool
    requester_confirmed: bool
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class RatingCreate(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=1000)


class RatingOut(RatingCreate):
    id: int
    transaction_id: int
    rater_id: int
    rated_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SearchFilters(BaseModel):
    resource_type: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    max_distance_km: Optional[float] = Field(default=None, ge=0)
    status: Optional[str] = None
    urgent: Optional[bool] = None
    sort_by: str = "relevance"


class SearchFavoriteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    filters: SearchFilters
    alerts_enabled: bool = True


class SearchFavoriteOut(BaseModel):
    id: int
    name: str
    filters: dict
    alerts_enabled: bool
    created_at: datetime


class NotificationOut(BaseModel):
    id: int
    kind: str
    title: str
    message: str
    read: bool
    created_at: datetime


class CategoryCreate(BaseModel):
    resource_type: str
    name: str


class CategoryOut(CategoryCreate):
    id: int
    active: bool


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class CampaignOut(CampaignCreate):
    id: int
    created_at: datetime


class PartnerCreate(BaseModel):
    name: str
    type: str
    contact: Optional[str] = None
    active: bool = True


class PartnerOut(PartnerCreate):
    id: int
    created_at: datetime


class MembershipCreate(BaseModel):
    user_id: int
    plan: str
    status: str = "activa"
    ends_at: Optional[datetime] = None


class MembershipOut(MembershipCreate):
    id: int
    starts_at: datetime


class AssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class AssistantMessageOut(BaseModel):
    id: int
    sender: str
    content: str
    created_at: datetime


class SupportCreate(BaseModel):
    subject: str
    message: str


class SupportOut(SupportCreate):
    id: int
    user_id: int
    status: str
    created_at: datetime


class FavoriteOut(BaseModel):
    id: int
    donation_id: int
    created_at: datetime


class DashboardOut(BaseModel):
    active_donations: int
    open_requests: int
    recommended_matches: int
    recent_transactions: int
    reputation_score: float
    ratings_count: int
    donations_by_category: dict[str, int]
    requests_attended: int
    successful_rate: float
    expiring_soon: int

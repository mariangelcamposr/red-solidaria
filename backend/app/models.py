import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base

class UserRole(str, enum.Enum):
    PARTICULAR='particular'; RESCATISTA='rescatista'; HOGAR_TRANSITO='hogar_transito'; ONG='ong'; VETERINARIA='veterinaria'; COMERCIO='comercio'; ADMIN='admin'
class AccountStatus(str, enum.Enum): PENDING='pendiente_activacion'; ACTIVE='activa'; SUSPENDED='suspendida'
class DonationStatus(str, enum.Enum): PENDING='pendiente'; VISIBLE='disponible'; REJECTED='rechazada'; RESERVED='reservada'; MATCHED='en_proceso'; COMPLETED='entregada'; CANCELLED='cancelada'; EXPIRED='vencida'
class RequestStatus(str, enum.Enum): OPEN='abierta'; IN_PROGRESS='en_proceso'; CLOSED='cerrada'
class Priority(str, enum.Enum): LOW='baja'; MEDIUM='media'; HIGH='alta'
class MatchStatus(str, enum.Enum): PENDING='pendiente'; NOTIFIED='notificada'; VIEWED='visualizada'; CONTACTED='contactada'; COORDINATING='coordinando'; DELIVERED='entregada'; CLOSED='cerrada'
class TransactionStatus(str, enum.Enum): PENDING_CONFIRMATION='pendiente_confirmacion'; COMPLETED='completada'

class User(Base):
    __tablename__='users'
    id=Column(Integer,primary_key=True,index=True); username=Column(String(50),unique=True,index=True,nullable=False); email=Column(String(120),unique=True,index=True,nullable=False); hashed_password=Column(String(255),nullable=False)
    first_name=Column(String(100),nullable=False,default=''); last_name=Column(String(100),nullable=False,default=''); phone=Column(String(40),nullable=False,default=''); address=Column(String(200),nullable=False,default=''); city=Column(String(100),nullable=False,default=''); state=Column(String(100),nullable=False,default=''); country=Column(String(100),nullable=False,default=''); postal_code=Column(String(20),nullable=True)
    latitude=Column(Float,nullable=True); longitude=Column(Float,nullable=True); role=Column(Enum(UserRole),default=UserRole.PARTICULAR,nullable=False); status=Column(Enum(AccountStatus),default=AccountStatus.PENDING,nullable=False)
    email_verified=Column(Boolean,default=False); terms_accepted=Column(Boolean,default=False); privacy_accepted=Column(Boolean,default=False); verification_token=Column(String(120),nullable=True,index=True)
    reputation_score=Column(Float,default=0.0); ratings_count=Column(Integer,default=0); notification_frequency=Column(String(30),default='inmediata'); notification_types=Column(String(500),default='match,message,expiry,delivery,rating'); created_at=Column(DateTime,default=datetime.utcnow); updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    donations=relationship('Donation',back_populates='donor'); requests=relationship('Request',back_populates='requester')

class Donation(Base):
    __tablename__='donations'
    id=Column(Integer,primary_key=True,index=True); donor_id=Column(Integer,ForeignKey('users.id'),nullable=False); title=Column(String(150),nullable=False); description=Column(String(500),nullable=False); resource_type=Column(String(50),nullable=False); category=Column(String(80),nullable=False); quantity=Column(Float,nullable=False,default=1); condition=Column(String(100),nullable=False); location=Column(String(200),nullable=False); latitude=Column(Float,nullable=True); longitude=Column(Float,nullable=True); expiry_date=Column(DateTime,nullable=True); presentation=Column(String(100),nullable=True); package_condition=Column(String(100),nullable=True); delivery_conditions=Column(String(300),nullable=False,default='A coordinar'); image_path=Column(String(300),nullable=True); ai_analysis_result=Column(Text,nullable=True); is_urgent=Column(Boolean,default=False); status=Column(Enum(DonationStatus),default=DonationStatus.PENDING); rejection_reason=Column(String(255),nullable=True); created_at=Column(DateTime,default=datetime.utcnow); updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    donor=relationship('User',back_populates='donations'); matches=relationship('Match',back_populates='donation'); photos=relationship('Photo',back_populates='donation',cascade='all, delete-orphan')

class Request(Base):
    __tablename__='requests'
    id=Column(Integer,primary_key=True,index=True); requester_id=Column(Integer,ForeignKey('users.id'),nullable=False); resource_type=Column(String(50),nullable=False); category=Column(String(80),nullable=False); quantity=Column(Float,nullable=False,default=1); justification=Column(String(1000),nullable=False); location=Column(String(200),nullable=False); latitude=Column(Float,nullable=True); longitude=Column(Float,nullable=True); priority=Column(Enum(Priority),default=Priority.MEDIUM); status=Column(Enum(RequestStatus),default=RequestStatus.OPEN); expires_at=Column(DateTime,nullable=True); image_path=Column(String(300),nullable=True); created_at=Column(DateTime,default=datetime.utcnow)
    requester=relationship('User',back_populates='requests')

    @property
    def active(self):
        return self.status != RequestStatus.CLOSED and (self.expires_at is None or self.expires_at >= datetime.utcnow())

class Match(Base):
    __tablename__='matches'
    id=Column(Integer,primary_key=True,index=True); donation_id=Column(Integer,ForeignKey('donations.id'),nullable=False); request_id=Column(Integer,ForeignKey('requests.id'),nullable=False); requester_id=Column(Integer,ForeignKey('users.id'),nullable=False); score=Column(Float,nullable=False); distance_km=Column(Float,nullable=True); criteria=Column(Text,nullable=True); status=Column(Enum(MatchStatus),default=MatchStatus.PENDING); created_at=Column(DateTime,default=datetime.utcnow)
    donation=relationship('Donation',back_populates='matches'); messages=relationship('Message',back_populates='match',cascade='all, delete-orphan')

class Message(Base):
    __tablename__='messages'
    id=Column(Integer,primary_key=True,index=True); match_id=Column(Integer,ForeignKey('matches.id'),nullable=False); sender_id=Column(Integer,ForeignKey('users.id'),nullable=False); content=Column(Text,nullable=False); created_at=Column(DateTime,default=datetime.utcnow); match=relationship('Match',back_populates='messages')

class Transaction(Base):
    __tablename__='transactions'
    id=Column(Integer,primary_key=True,index=True); match_id=Column(Integer,ForeignKey('matches.id'),nullable=False,unique=True); donation_id=Column(Integer,ForeignKey('donations.id'),nullable=False); donor_id=Column(Integer,ForeignKey('users.id'),nullable=False); requester_id=Column(Integer,ForeignKey('users.id'),nullable=False); delivery_details=Column(String(500),nullable=True); status=Column(Enum(TransactionStatus),default=TransactionStatus.PENDING_CONFIRMATION); donor_confirmed=Column(Boolean,default=False); requester_confirmed=Column(Boolean,default=False); created_at=Column(DateTime,default=datetime.utcnow); completed_at=Column(DateTime,nullable=True)

class Rating(Base):
    __tablename__='ratings'
    id=Column(Integer,primary_key=True); transaction_id=Column(Integer,ForeignKey('transactions.id'),nullable=False); rater_id=Column(Integer,ForeignKey('users.id'),nullable=False); rated_user_id=Column(Integer,ForeignKey('users.id'),nullable=False); score=Column(Integer,nullable=False); comment=Column(Text,nullable=True); created_at=Column(DateTime,default=datetime.utcnow)

class Photo(Base):
    __tablename__='photos'
    id=Column(Integer,primary_key=True); donation_id=Column(Integer,ForeignKey('donations.id'),nullable=False); path=Column(String(300),nullable=False); uploaded_at=Column(DateTime,default=datetime.utcnow); ai_result=Column(Text,nullable=True); donation=relationship('Donation',back_populates='photos')

class Notification(Base):
    __tablename__='notifications'
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id'),nullable=False); kind=Column(String(60),nullable=False); title=Column(String(150),nullable=False); message=Column(String(500),nullable=False); read=Column(Boolean,default=False); created_at=Column(DateTime,default=datetime.utcnow)

class Favorite(Base):
    __tablename__='favorites'
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id'),nullable=False); donation_id=Column(Integer,ForeignKey('donations.id'),nullable=False); created_at=Column(DateTime,default=datetime.utcnow)

class SearchFavorite(Base):
    __tablename__='search_favorites'
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id'),nullable=False); name=Column(String(100),nullable=False); filters_json=Column(Text,nullable=False); alerts_enabled=Column(Boolean,default=True); created_at=Column(DateTime,default=datetime.utcnow)

class CatalogCategory(Base):
    __tablename__='catalog_categories'
    id=Column(Integer,primary_key=True); resource_type=Column(String(50),nullable=False); name=Column(String(80),nullable=False); active=Column(Boolean,default=True)

class Campaign(Base):
    __tablename__='campaigns'
    id=Column(Integer,primary_key=True); name=Column(String(150),nullable=False); description=Column(Text,nullable=True); active=Column(Boolean,default=True); starts_at=Column(DateTime,nullable=True); ends_at=Column(DateTime,nullable=True); created_at=Column(DateTime,default=datetime.utcnow)

class BusinessPartner(Base):
    __tablename__='business_partners'
    id=Column(Integer,primary_key=True); name=Column(String(150),nullable=False); type=Column(String(80),nullable=False); contact=Column(String(150),nullable=True); active=Column(Boolean,default=True); created_at=Column(DateTime,default=datetime.utcnow)

class Membership(Base):
    __tablename__='memberships'
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id'),nullable=False); plan=Column(String(80),nullable=False); status=Column(String(50),default='activa'); starts_at=Column(DateTime,default=datetime.utcnow); ends_at=Column(DateTime,nullable=True)

class SupportRequest(Base):
    __tablename__='support_requests'
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id'),nullable=False); subject=Column(String(150),nullable=False); message=Column(Text,nullable=False); status=Column(String(40),default='abierto'); created_at=Column(DateTime,default=datetime.utcnow)

class AssistantMessage(Base):
    __tablename__='assistant_messages'
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id'),nullable=False); sender=Column(String(20),nullable=False); content=Column(Text,nullable=False); created_at=Column(DateTime,default=datetime.utcnow)

class AuditLog(Base):
    __tablename__='audit_logs'
    id=Column(Integer,primary_key=True); user_id=Column(Integer,ForeignKey('users.id'),nullable=True); action=Column(String(100),nullable=False); entity=Column(String(80),nullable=False); entity_id=Column(Integer,nullable=True); details=Column(Text,nullable=True); created_at=Column(DateTime,default=datetime.utcnow)

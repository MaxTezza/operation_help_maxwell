"""
Client model for CRM functionality
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class AcquisitionSource(enum.Enum):
    REFERRAL = "referral"
    WEBSITE = "website"
    SOCIAL_MEDIA = "social_media"
    TRADE_SHOW = "trade_show"
    COLD_OUTREACH = "cold_outreach"
    EXISTING_CLIENT = "existing_client"
    OTHER = "other"

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    phone = Column(String(50))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(100), default="USA")

    # Business details
    industry = Column(String(100))
    acquisition_source = Column(Enum(AcquisitionSource), default=AcquisitionSource.OTHER)

    # Preferences and notes
    preferences = Column(Text)
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact_date = Column(DateTime)
    next_follow_up = Column(DateTime)

    # Relationships
    orders = relationship("Order", back_populates="client", cascade="all, delete-orphan")
    interactions = relationship("ClientInteraction", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, company={self.company_name})>"

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'industry': self.industry,
            'acquisition_source': self.acquisition_source.value if self.acquisition_source else None,
            'preferences': self.preferences,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_contact_date': self.last_contact_date.isoformat() if self.last_contact_date else None,
            'next_follow_up': self.next_follow_up.isoformat() if self.next_follow_up else None,
        }


class ClientInteraction(Base):
    __tablename__ = 'client_interactions'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    interaction_type = Column(String(50))  # email, call, meeting, quote, follow_up
    subject = Column(String(200))
    notes = Column(Text)
    interaction_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))

    # Relationships
    from sqlalchemy import ForeignKey
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client", back_populates="interactions")

    def __repr__(self):
        return f"<ClientInteraction(id={self.id}, type={self.interaction_type})>"

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'interaction_type': self.interaction_type,
            'subject': self.subject,
            'notes': self.notes,
            'interaction_date': self.interaction_date.isoformat() if self.interaction_date else None,
            'created_by': self.created_by,
        }

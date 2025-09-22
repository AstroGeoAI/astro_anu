from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

class QueryLog(Base):
    """Log model for tracking user queries and system interactions"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50))  # astronomy, geospatial, prediction, etc.
    processing_time_seconds = Column(Float)
    result_status = Column(String(20))  # success, error, partial
    result_summary = Column(Text)
    agents_involved = Column(JSON)  # List of agents that processed this query
    data_sources = Column(JSON)  # APIs and datasets used
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))
    user_agent = Column(Text)

class ApiUsage(Base):
    """Track API usage across different space agency endpoints"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    api_provider = Column(String(50), nullable=False)  # NASA, ISRO, ESA, Bhuvan
    endpoint = Column(String(255), nullable=False)
    request_method = Column(String(10))  # GET, POST
    request_params = Column(JSON)
    response_status = Column(Integer)
    response_time_ms = Column(Float)
    data_size_bytes = Column(Integer)
    rate_limit_remaining = Column(Integer)
    error_message = Column(Text)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class Feedback(Base):
    """User feedback and system performance ratings"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    query_log_id = Column(Integer, index=True)
    rating = Column(Integer)  # 1-5 star rating
    feedback_type = Column(String(50))  # quality, speed, accuracy, completeness
    feedback_text = Column(Text)
    is_resolved = Column(Boolean, default=False)
    admin_response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    category = Column(String(50))  # bug, feature_request, improvement, compliment

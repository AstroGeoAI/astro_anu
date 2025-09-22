from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from .models import User, QueryLog, ApiUsage, Feedback

class UserRepository:
    """Repository for User CRUD operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.session.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.session.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            self.session.commit()
            self.session.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Soft delete user by setting is_active to False"""
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            self.session.commit()
            return True
        return False
    
    def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.session.commit()

class QueryLogRepository:
    """Repository for QueryLog CRUD operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_query_log(self, log_data: Dict[str, Any]) -> QueryLog:
        """Create a new query log entry"""
        query_log = QueryLog(**log_data)
        self.session.add(query_log)
        self.session.commit()
        self.session.refresh(query_log)
        return query_log
    
    def get_query_log_by_id(self, log_id: int) -> Optional[QueryLog]:
        """Get query log by ID"""
        return self.session.query(QueryLog).filter(QueryLog.id == log_id).first()
    
    def get_user_query_logs(self, user_id: int, limit: int = 50) -> List[QueryLog]:
        """Get recent query logs for a specific user"""
        return (self.session.query(QueryLog)
                .filter(QueryLog.user_id == user_id)
                .order_by(desc(QueryLog.created_at))
                .limit(limit)
                .all())
    
    def get_query_logs_by_type(self, query_type: str, limit: int = 100) -> List[QueryLog]:
        """Get query logs by type"""
        return (self.session.query(QueryLog)
                .filter(QueryLog.query_type == query_type)
                .order_by(desc(QueryLog.created_at))
                .limit(limit)
                .all())
    
    def update_query_log(self, log_id: int, update_data: Dict[str, Any]) -> Optional[QueryLog]:
        """Update query log information"""
        query_log = self.get_query_log_by_id(log_id)
        if query_log:
            for key, value in update_data.items():
                setattr(query_log, key, value)
            self.session.commit()
            self.session.refresh(query_log)
        return query_log
    
    def get_query_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get query statistics for a date range"""
        stats = {}
        
        # Total queries
        stats['total_queries'] = (self.session.query(func.count(QueryLog.id))
                                 .filter(and_(QueryLog.created_at >= start_date,
                                            QueryLog.created_at <= end_date))
                                 .scalar())
        
        # Queries by type
        query_types = (self.session.query(QueryLog.query_type, func.count(QueryLog.id))
                      .filter(and_(QueryLog.created_at >= start_date,
                                 QueryLog.created_at <= end_date))
                      .group_by(QueryLog.query_type)
                      .all())
        stats['queries_by_type'] = dict(query_types)
        
        # Average processing time
        avg_time = (self.session.query(func.avg(QueryLog.processing_time_seconds))
                   .filter(and_(QueryLog.created_at >= start_date,
                              QueryLog.created_at <= end_date))
                   .scalar())
        stats['avg_processing_time'] = float(avg_time) if avg_time else 0.0
        
        return stats

class ApiUsageRepository:
    """Repository for ApiUsage CRUD operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_api_usage(self, usage_data: Dict[str, Any]) -> ApiUsage:
        """Create a new API usage record"""
        api_usage = ApiUsage(**usage_data)
        self.session.add(api_usage)
        self.session.commit()
        self.session.refresh(api_usage)
        return api_usage
    
    def get_api_usage_by_id(self, usage_id: int) -> Optional[ApiUsage]:
        """Get API usage record by ID"""
        return self.session.query(ApiUsage).filter(ApiUsage.id == usage_id).first()
    
    def get_api_usage_by_provider(self, provider: str, limit: int = 100) -> List[ApiUsage]:
        """Get API usage records by provider"""
        return (self.session.query(ApiUsage)
                .filter(ApiUsage.api_provider == provider)
                .order_by(desc(ApiUsage.created_at))
                .limit(limit)
                .all())
    
    def get_user_api_usage(self, user_id: int, limit: int = 50) -> List[ApiUsage]:
        """Get API usage for a specific user"""
        return (self.session.query(ApiUsage)
                .filter(ApiUsage.user_id == user_id)
                .order_by(desc(ApiUsage.created_at))
                .limit(limit)
                .all())
    
    def get_api_usage_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get API usage statistics for a date range"""
        stats = {}
        
        # Usage by provider
        provider_usage = (self.session.query(ApiUsage.api_provider, func.count(ApiUsage.id))
                         .filter(and_(ApiUsage.created_at >= start_date,
                                    ApiUsage.created_at <= end_date))
                         .group_by(ApiUsage.api_provider)
                         .all())
        stats['usage_by_provider'] = dict(provider_usage)
        
        # Average response time by provider
        response_times = (self.session.query(ApiUsage.api_provider, 
                                           func.avg(ApiUsage.response_time_ms))
                         .filter(and_(ApiUsage.created_at >= start_date,
                                    ApiUsage.created_at <= end_date))
                         .group_by(ApiUsage.api_provider)
                         .all())
        stats['avg_response_time'] = {provider: float(time) if time else 0.0 
                                     for provider, time in response_times}
        
        # Error rates
        error_counts = (self.session.query(ApiUsage.api_provider, 
                                         func.count(ApiUsage.id))
                       .filter(and_(ApiUsage.created_at >= start_date,
                                  ApiUsage.created_at <= end_date,
                                  ApiUsage.response_status >= 400))
                       .group_by(ApiUsage.api_provider)
                       .all())
        stats['error_counts'] = dict(error_counts)
        
        return stats

class FeedbackRepository:
    """Repository for Feedback CRUD operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_feedback(self, feedback_data: Dict[str, Any]) -> Feedback:
        """Create a new feedback entry"""
        feedback = Feedback(**feedback_data)
        self.session.add(feedback)
        self.session.commit()
        self.session.refresh(feedback)
        return feedback
    
    def get_feedback_by_id(self, feedback_id: int) -> Optional[Feedback]:
        """Get feedback by ID"""
        return self.session.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    def get_user_feedback(self, user_id: int, limit: int = 50) -> List[Feedback]:
        """Get feedback from a specific user"""
        return (self.session.query(Feedback)
                .filter(Feedback.user_id == user_id)
                .order_by(desc(Feedback.created_at))
                .limit(limit)
                .all())
    
    def get_unresolved_feedback(self, limit: int = 100) -> List[Feedback]:
        """Get unresolved feedback"""
        return (self.session.query(Feedback)
                .filter(Feedback.is_resolved == False)
                .order_by(desc(Feedback.created_at))
                .limit(limit)
                .all())
    
    def update_feedback(self, feedback_id: int, update_data: Dict[str, Any]) -> Optional[Feedback]:
        """Update feedback information"""
        feedback = self.get_feedback_by_id(feedback_id)
        if feedback:
            for key, value in update_data.items():
                setattr(feedback, key, value)
            self.session.commit()
            self.session.refresh(feedback)
        return feedback
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get overall feedback statistics"""
        stats = {}
        
        # Average rating
        avg_rating = self.session.query(func.avg(Feedback.rating)).scalar()
        stats['average_rating'] = float(avg_rating) if avg_rating else 0.0
        
        # Feedback by rating
        rating_counts = (self.session.query(Feedback.rating, func.count(Feedback.id))
                        .group_by(Feedback.rating)
                        .all())
        stats['ratings_distribution'] = dict(rating_counts)
        
        # Feedback by category
        category_counts = (self.session.query(Feedback.category, func.count(Feedback.id))
                          .group_by(Feedback.category)
                          .all())
        stats['feedback_by_category'] = dict(category_counts)
        
        # Resolution status
        resolution_stats = (self.session.query(Feedback.is_resolved, func.count(Feedback.id))
                           .group_by(Feedback.is_resolved)
                           .all())
        stats['resolution_status'] = dict(resolution_stats)
        
        return stats

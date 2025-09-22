from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from loguru import logger

from ..security.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from ..crew import AstroGeoCrew
from ..utils.vector_store import VectorStoreManager
from ..utils.config_loader import ConfigLoader

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    query_type: str = "astronomy"
    include_context: bool = True

class QueryResponse(BaseModel):
    result: str
    processing_time: float
    timestamp: datetime
    context: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Initialize FastAPI app
app = FastAPI(
    title="AstroGeo API",
    description="AI Space Data Analysis System API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
config_loader = ConfigLoader()
crew_instance = None
vector_store = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global crew_instance, vector_store
    try:
        # Initialize vector store
        rag_config = config_loader.load_config('rag')
        vector_store = VectorStoreManager(rag_config)
        vector_store.initialize_vector_store()
        
        # Initialize crew
        crew_instance = AstroGeoCrew()
        
        logger.info("AstroGeo API initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")

@app.post("/auth/register", response_model=Dict[str, str])
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # In production, save to database
        hashed_password = get_password_hash(user_data.password)
        
        # Mock user creation (implement database save in production)
        logger.info(f"User registration attempt: {user_data.username}")
        
        return {"message": "User created successfully", "username": user_data.username}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access token"""
    try:
        # Mock authentication (implement database check in production)
        if form_data.username == "demo" and form_data.password == "demo123":
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": form_data.username}, 
                expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_active_user)
):
    """Process query through CrewAI agents"""
    start_time = datetime.now()
    
    try:
        context = ""
        if request.include_context and vector_store:
            search_results = vector_store.similarity_search(request.query, k=3)
            context = "\n".join([result['document'] for result in search_results])
        
        # Prepare inputs for CrewAI
        inputs = {
            'topic': request.query,
            'query_type': request.query_type,
            'context': context,
            'data_categories': request.query_type,
            'time_range': 'recent',
            'celestial_objects': request.query,
            'geographic_region': 'global',
            'image_category': 'space',
            'monitoring_date': 'today',
            'research_topic': request.query,
            'dataset_category': 'space_data',
            'prediction_target': 'space_weather',
            'visualization_subject': request.query,
            'research_objective': request.query,
            'monitoring_parameters': 'anomalies'
        }
        
        # Execute CrewAI crew
        if crew_instance:
            result = crew_instance.crew().kickoff(inputs=inputs)
            result_text = str(result)
        else:
            result_text = "CrewAI not initialized"
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Log query in background
        background_tasks.add_task(
            log_query_usage, 
            current_user.get("username", "unknown"), 
            request.query, 
            request.query_type, 
            processing_time
        )
        
        return QueryResponse(
            result=result_text,
            processing_time=processing_time,
            timestamp=datetime.now(),
            context=context if request.include_context else None
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )

@app.get("/metrics")
async def get_metrics(current_user: Dict = Depends(get_current_active_user)):
    """Get system metrics"""
    try:
        metrics = {
            "timestamp": datetime.now(),
            "vector_db_status": "connected" if vector_store else "disconnected",
            "crew_status": "initialized" if crew_instance else "not_initialized",
            "active_agents": 12 if crew_instance else 0,
            "api_endpoints": len(app.routes)
        }
        
        if vector_store:
            db_info = vector_store.get_collection_info()
            metrics["vector_db_documents"] = db_info.get('document_count', 0)
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics retrieval failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

async def log_query_usage(username: str, query: str, query_type: str, processing_time: float):
    """Background task to log query usage"""
    try:
        # In production, save to database
        logger.info(f"Query logged - User: {username}, Type: {query_type}, Time: {processing_time}s")
    except Exception as e:
        logger.error(f"Failed to log query usage: {e}")

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps
from loguru import logger

# Prometheus metrics
AGENT_REQUESTS = Counter('astrogeo_agent_requests_total', 'Total agent requests', ['agent_name', 'status'])
AGENT_DURATION = Histogram('astrogeo_agent_duration_seconds', 'Agent processing time', ['agent_name'])
ACTIVE_AGENTS = Gauge('astrogeo_active_agents', 'Number of active agents')
API_CALLS = Counter('astrogeo_api_calls_total', 'Total API calls', ['provider', 'endpoint', 'status'])
VECTOR_DB_QUERIES = Counter('astrogeo_vector_db_queries_total', 'Vector database queries', ['status'])

class MetricsCollector:
    """Collect and expose system metrics"""
    
    def __init__(self, port: int = 8001):
        self.port = port
        self.start_time = time.time()
        
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        try:
            start_http_server(self.port)
            logger.info(f"Metrics server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    def track_agent_performance(self, agent_name: str):
        """Decorator to track agent performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    AGENT_REQUESTS.labels(agent_name=agent_name, status='success').inc()
                    return result
                except Exception as e:
                    AGENT_REQUESTS.labels(agent_name=agent_name, status='error').inc()
                    raise
                finally:
                    duration = time.time() - start_time
                    AGENT_DURATION.labels(agent_name=agent_name).observe(duration)
            return wrapper
        return decorator
    
    def track_api_call(self, provider: str, endpoint: str, status: str):
        """Track external API calls"""
        API_CALLS.labels(provider=provider, endpoint=endpoint, status=status).inc()
    
    def track_vector_db_query(self, status: str):
        """Track vector database queries"""
        VECTOR_DB_QUERIES.labels(status=status).inc()
    
    def update_active_agents(self, count: int):
        """Update active agents count"""
        ACTIVE_AGENTS.set(count)

# Global metrics instance
metrics = MetricsCollector()

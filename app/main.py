from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
import random
import os

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# Custom metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Duration of requests')

# Configure OpenTelemetry
def configure_tracing():
    # Create a resource with service information
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: "fastapi-observability-demo",
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.SERVICE_INSTANCE_ID: os.getenv("HOSTNAME", "fastapi-local"),
    })
    
    # Create tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_AGENT_HOST", "jaeger"),
        agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Get tracer
    return trace.get_tracer(__name__)

# Initialize tracing
tracer = configure_tracing()

app = FastAPI(
    title="FastAPI Observability Demo",
    description="A FastAPI application with Prometheus metrics and distributed tracing",
    version="1.0.0"
)

# Initialize Prometheus instrumentator
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Initialize OpenTelemetry automatic instrumentation
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
RequestsInstrumentor().instrument()

@app.get("/")
async def root():
    """Root endpoint"""
    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()
    return {"message": "Hello World! This is a FastAPI app with metrics."}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID - simulates database call"""
    start_time = time.time()
    REQUEST_COUNT.labels(method="GET", endpoint="/api/users/{user_id}").inc()
    
    # Create custom span for database simulation
    with tracer.start_as_current_span("simulate_database_query") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("db.operation", "select")
        span.set_attribute("db.table", "users")
        
        # Simulate some processing time
        processing_time = random.uniform(0.1, 0.5)
        span.set_attribute("db.duration_ms", processing_time * 1000)
        time.sleep(processing_time)
        
        if user_id == 404:
            span.set_attribute("error", True)
            span.set_attribute("error.message", "User not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        span.set_attribute("user.found", True)
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return {
        "user_id": user_id,
        "username": f"user_{user_id}",
        "email": f"user_{user_id}@example.com",
        "processing_time": processing_time
    }

@app.post("/api/users")
async def create_user():
    """Create a new user - simulates user creation"""
    start_time = time.time()
    REQUEST_COUNT.labels(method="POST", endpoint="/api/users").inc()
    
    new_user_id = random.randint(1000, 9999)
    
    # Create custom span for user validation
    with tracer.start_as_current_span("validate_user_data") as validation_span:
        validation_span.set_attribute("user.id", new_user_id)
        validation_time = random.uniform(0.05, 0.15)
        time.sleep(validation_time)
        validation_span.set_attribute("validation.duration_ms", validation_time * 1000)
        validation_span.set_attribute("validation.passed", True)
    
    # Create custom span for database insertion
    with tracer.start_as_current_span("database_insert") as db_span:
        db_span.set_attribute("user.id", new_user_id)
        db_span.set_attribute("db.operation", "insert")
        db_span.set_attribute("db.table", "users")
        
        # Simulate database processing time
        db_processing_time = random.uniform(0.15, 0.65)
        time.sleep(db_processing_time)
        db_span.set_attribute("db.duration_ms", db_processing_time * 1000)
        db_span.set_attribute("db.rows_affected", 1)
    
    processing_time = time.time() - start_time
    REQUEST_DURATION.observe(processing_time)
    
    return {
        "user_id": new_user_id,
        "username": f"user_{new_user_id}",
        "email": f"user_{new_user_id}@example.com",
        "created": True,
        "processing_time": processing_time
    }

@app.get("/api/simulate-error")
async def simulate_error():
    """Endpoint to simulate errors for testing"""
    REQUEST_COUNT.labels(method="GET", endpoint="/api/simulate-error").inc()
    
    # Randomly generate errors
    if random.random() < 0.3:  # 30% chance of error
        raise HTTPException(status_code=500, detail="Simulated internal server error")
    
    return {"message": "Success! No error this time."}

@app.get("/custom-metrics")
async def custom_metrics():
    """Expose custom metrics in Prometheus format"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
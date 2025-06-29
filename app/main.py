from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
import random

# Custom metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Duration of requests')

app = FastAPI(
    title="FastAPI Observability Demo",
    description="A FastAPI application with Prometheus metrics",
    version="1.0.0"
)

# Initialize Prometheus instrumentator
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

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
    
    # Simulate some processing time
    processing_time = random.uniform(0.1, 0.5)
    time.sleep(processing_time)
    
    if user_id == 404:
        raise HTTPException(status_code=404, detail="User not found")
    
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
    
    # Simulate processing time
    processing_time = random.uniform(0.2, 0.8)
    time.sleep(processing_time)
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    new_user_id = random.randint(1000, 9999)
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
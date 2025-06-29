# FastAPI Observability Demo

A FastAPI application with complete observability stack using Prometheus, Grafana, and Jaeger for comprehensive monitoring, metrics visualization, and distributed tracing.

## Features

- **FastAPI Application**: Modern, fast web framework with automatic API documentation
- **Prometheus Metrics**: Built-in metrics collection for request rates, duration, and custom metrics
- **Grafana Dashboards**: Pre-configured dashboards for visualizing application metrics and traces
- **Jaeger Tracing**: Distributed tracing for request flow visualization and performance analysis
- **OpenTelemetry Integration**: Industry-standard observability instrumentation
- **Docker Compose**: One-command setup with all services containerized
- **UV Package Manager**: Fast Python package management for dependency handling

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   FastAPI   │───▶│ Prometheus  │───▶│   Grafana   │
│   :8000     │    │   :9090     │    │   :3000     │
│             │    └─────────────┘    │             │
│             │                       │  ┌──────────┤
│             │    ┌─────────────┐    │  │ Jaeger   │
│             │───▶│   Jaeger    │───▶│  │ UI/Query │
│             │    │   :16686    │    │  └──────────┤
└─────────────┘    └─────────────┘    └─────────────┘
     │
     │ OpenTelemetry
     │ Traces
     ▼
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- UV (Python package manager) - [Install UV](https://docs.astral.sh/uv/getting-started/installation/)

### Setup and Run

1. **Clone and navigate to the project directory**:
   ```bash
   cd fastapi-obs
   ```

2. **Initialize the Python environment** (optional, for local development):
   ```bash
   uv sync
   ```

3. **Start all services with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

4. **Access the services**:
   - **FastAPI Application**: http://localhost:8000
   - **FastAPI Documentation**: http://localhost:8000/docs
   - **Prometheus**: http://localhost:9090
   - **Grafana**: http://localhost:3000 (admin/admin)
   - **Jaeger UI**: http://localhost:16686

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `GET /api/users/{user_id}` - Get user by ID (simulates database calls)
- `POST /api/users` - Create a new user
- `GET /api/simulate-error` - Endpoint that randomly generates errors for testing
- `GET /metrics` - Prometheus metrics endpoint (auto-generated)
- `GET /custom-metrics` - Custom metrics endpoint

## Monitoring Setup

### Prometheus Metrics

The application exposes several types of metrics:

1. **HTTP Request Metrics** (via prometheus-fastapi-instrumentator):
   - `http_requests_total` - Total number of HTTP requests
   - `http_request_duration_seconds` - HTTP request durations

2. **Custom Application Metrics**:
   - `app_requests_total` - Custom counter for tracking requests by endpoint
   - `app_request_duration_seconds` - Custom histogram for request durations

### Grafana Dashboards

The setup includes two pre-configured dashboards:

#### **Metrics Dashboard** (`fastapi-monitoring`):
1. **Request Rate**: Shows the rate of incoming requests over time
2. **Request Duration**: 95th and 50th percentile response times
3. **Error Rate**: Percentage of 4XX and 5XX errors
4. **Requests by Status Code**: Breakdown of requests by HTTP status
5. **Custom Metrics**: Application-specific metrics visualization

#### **Tracing Dashboard** (`fastapi-tracing`):
1. **Service Map**: Visual representation of service dependencies
2. **Request Latency Percentiles**: P50, P95, P99 latency tracking
3. **Request Rate by Endpoint**: Traffic distribution across endpoints
4. **Trace Search**: Interactive trace exploration and filtering
5. **Key Performance Indicators**: Current metrics at a glance

### Distributed Tracing

The application uses **OpenTelemetry** for distributed tracing with **Jaeger** as the backend:

1. **Automatic Instrumentation**:
   - FastAPI requests and responses
   - HTTP client calls (httpx, requests)
   - Database-like operations simulation

2. **Custom Spans**:
   - `simulate_database_query`: Database operation simulation
   - `validate_user_data`: User validation logic
   - `database_insert`: Database insertion simulation

3. **Trace Attributes**:
   - User IDs, operation types, duration metrics
   - Error tracking and status codes
   - Service and version information

4. **Features**:
   - End-to-end request tracing
   - Performance bottleneck identification
   - Error correlation across services
   - Service dependency mapping

## Development

### Local Development (without Docker)

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run the FastAPI application**:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Start Prometheus and Grafana separately** (you'll need to install them locally or use Docker for just these services)

### Testing the Application

Generate some traffic to see metrics in action:

```bash
# Test various endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/api/users/123
curl -X POST http://localhost:8000/api/users
curl http://localhost:8000/api/simulate-error

# View raw metrics
curl http://localhost:8000/metrics
curl http://localhost:8000/custom-metrics
```

### Load Testing

For more comprehensive testing, you can use tools like `wrk` or `apache-bench`:

```bash
# Install wrk (macOS)
brew install wrk

# Generate load
wrk -t12 -c400 -d30s http://localhost:8000/
```

## Configuration

### Prometheus Configuration

- **Scrape Interval**: 5s for FastAPI metrics, 10s for custom metrics
- **Targets**: Automatically discovers the FastAPI service
- **Configuration**: See `prometheus/prometheus.yml`

### Grafana Configuration

- **Data Source**: Automatically configured to use Prometheus
- **Dashboards**: Auto-provisioned from `grafana/dashboards/`
- **Default Credentials**: admin/admin (change in production!)

## Project Structure

```
fastapi-obs/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application with metrics & tracing
├── prometheus/
│   └── prometheus.yml       # Prometheus configuration
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   ├── prometheus.yml  # Prometheus datasource
│   │   │   └── jaeger.yml      # Jaeger datasource
│   │   └── dashboards/
│   │       └── dashboard.yml   # Dashboard provisioning
│   └── dashboards/
│       ├── fastapi-dashboard.json    # Metrics dashboard
│       └── tracing-dashboard.json    # Tracing dashboard
├── docker-compose.yml       # Docker Compose with all services
├── Dockerfile              # FastAPI application container
├── pyproject.toml          # Dependencies including OpenTelemetry
├── test_api.py             # Load testing script
└── README.md
```

## Customization

### Adding New Metrics

1. **Import Prometheus client**:
   ```python
   from prometheus_client import Counter, Histogram, Gauge
   ```

2. **Define your metric**:
   ```python
   MY_COUNTER = Counter('my_metric_total', 'Description of my metric')
   ```

3. **Use in your endpoint**:
   ```python
   @app.get("/my-endpoint")
   async def my_endpoint():
       MY_COUNTER.inc()
       return {"message": "Hello"}
   ```

### Adding New Dashboard Panels

1. Access Grafana at http://localhost:3000
2. Edit the existing dashboard or create a new one
3. Export the JSON and replace `grafana/dashboards/fastapi-dashboard.json`

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 3000, 8000, 9090, and 16686 are available
2. **Docker build issues**: Try `docker-compose down && docker-compose up --build`
3. **Metrics not showing**: Wait a few minutes for Prometheus to scrape metrics
4. **Grafana dashboard empty**: Check that Prometheus is running and configured correctly
5. **Traces not appearing**: Check that Jaeger is running and FastAPI can connect to it
6. **Tracing errors**: Verify OpenTelemetry configuration and Jaeger agent connectivity

### Logs

View logs for each service:
```bash
docker-compose logs fastapi
docker-compose logs prometheus  
docker-compose logs grafana
docker-compose logs jaeger
```

## Production Considerations

- Change default Grafana password
- Set up proper authentication for Prometheus
- Configure alerting rules
- Set up persistent storage for metrics data
- Use proper logging configuration
- Implement health checks and monitoring for the monitoring stack itself

## License

This project is for demonstration purposes. Use and modify as needed for your applications. 
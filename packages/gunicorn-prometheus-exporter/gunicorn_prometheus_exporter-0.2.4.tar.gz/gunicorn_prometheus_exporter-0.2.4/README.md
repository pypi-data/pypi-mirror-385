# Gunicorn Prometheus Exporter

[![CI](https://github.com/Agent-Hellboy/gunicorn-prometheus-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/Agent-Hellboy/gunicorn-prometheus-exporter/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Agent-Hellboy/gunicorn-prometheus-exporter/graph/badge.svg?token=NE7JS4FZHC)](https://codecov.io/gh/Agent-Hellboy/gunicorn-prometheus-exporter)
[![PyPI - Version](https://img.shields.io/pypi/v/gunicorn-prometheus-exporter.svg)](https://pypi.org/project/gunicorn-prometheus-exporter/)
[![Docker Pulls](https://badgen.net/docker/pulls/princekrroshan01/gunicorn-prometheus-exporter)](https://hub.docker.com/r/princekrroshan01/gunicorn-prometheus-exporter)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://Agent-Hellboy.github.io/gunicorn-prometheus-exporter)
[![PyPI Downloads](https://static.pepy.tech/badge/gunicorn-prometheus-exporter)](https://pepy.tech/projects/gunicorn-prometheus-exporter)

A comprehensive Prometheus metrics exporter for Gunicorn WSGI servers with support for multiple worker types and advanced monitoring capabilities, featuring innovative Redis-based storage, YAML configuration support, and advanced signal handling. This Gunicorn worker plugin exports Prometheus metrics to monitor worker performance, including memory usage, CPU usage, request durations, and error tracking (trying to replace <https://docs.gunicorn.org/en/stable/instrumentation.html> with extra info). It also aims to replace request-level tracking, such as the number of requests made to a particular endpoint, for any framework (e.g., Flask, Django, and others) that conforms to the WSGI specification.

## WSGI Protocol Limitations & Error Handling

### The Challenge with WSGI Error Tracking

One of the fundamental limitations of the WSGI protocol is that **Python frameworks consume errors and exceptions internally**. Most frameworks (Flask, Django, Pyramid, etc.) handle exceptions within their own middleware and error handling systems, making it difficult to capture comprehensive error metrics at the WSGI level.

This creates a challenge for monitoring tools like ours , we can only capture errors that bubble up to the WSGI layer, while many framework-specific errors are handled internally and never reach the WSGI interface.

**Note**: This is a fundamental limitation of the WSGI protocol design.

### Our Approach

We've implemented a two-tier error tracking system:

1. **WSGI-Level Errors**: Captured at the worker level for errors that reach the WSGI interface
2. **Framework Integration**: Designed to work with framework-specific error handlers when available

**Current Error Metrics:**
- `gunicorn_worker_failed_requests` - WSGI-level failed requests
- `gunicorn_worker_error_handling` - Errors handled by the worker

**Current Limitations**: Due to WSGI's design, we can only capture errors that bubble up to the WSGI layer. Framework-specific errors (like Django's 404s, Flask's route errors, etc.) are handled internally and never reach our monitoring system.

**Future Enhancement**: I'm exploring ways to integrate with framework-specific error handlers to capture more comprehensive error metrics.
And also, see [Issue #67](https://github.com/Agent-Hellboy/gunicorn-prometheus-exporter/issues/67) for request/response payload size tracking per endpoint , this is a nice issue and LLMs can't figure it out, please try it out if you can!


## Redis Storage Architecture

### Separating Storage from Compute

I've extended the Prometheus Python client to support **Redis-based storage** as an alternative to traditional multiprocess files. This architectural innovation is made possible by the brilliant protocol-based design of the Prometheus specification, which allows for clean storage backend replacement through the `StorageDictProtocol` interface.

The Prometheus multiprocess specification's protocol-based design enables us to seamlessly replace the default file-based storage (`MmapedDict`) with our Redis implementation (`RedisStorageDict`) without breaking compatibility. This is a testament to the excellent engineering behind the Prometheus ecosystem.

This architectural innovation provides several key benefits:

#### **Traditional Approach (File-Based)**

- Metrics stored in local files (`/tmp/prometheus_multiproc/`)
- Storage and compute are coupled on the same server
- Limited scalability across multiple instances
- File I/O overhead for metrics collection

#### **New Redis Storage Approach**

- Metrics stored directly in Redis (`gunicorn:*:metric:*` keys)
- **Storage and compute are completely separated**
- Shared metrics across multiple Gunicorn instances
- No local files created - pure Redis storage
- Better performance and scalability
- **Direct Redis integration** - no forwarding layer needed

### **Protocol-Based Design Benefits:**

The Prometheus specification's protocol-based design allows for:

- **Clean Interface Contract**: `StorageDictProtocol` defines exactly what methods storage backends must implement
- **Drop-in Replacement**: Our `RedisStorageDict` implements the same interface as `MmapedDict`
- **Type Safety**: Protocol ensures compile-time checking of interface compliance
- **Testing**: Easy to mock and test different storage implementations
- **Future Extensibility**: Can easily add database, S3, or other storage backends

### **Key Benefits:**

| Feature                | File-Based    | Redis Storage    |
| ---------------------- | ------------- | ---------------- |
| **Storage Location**   | Local files   | Redis server     |
| **Scalability**        | Single server | Multiple servers |
| **File I/O**           | High overhead | No file I/O      |
| **Shared Metrics**     | No            | Yes              |
| **Storage Separation** | Coupled       | Separated        |
| **Protocol Compliance** | MmapedDict   | RedisStorageDict |

### **Use Cases:**

- **Microservices Architecture**: Multiple services sharing metrics
- **Container Orchestration**: Kubernetes pods with shared Redis
- **High Availability**: Metrics survive server restarts
- **Cost Optimization**: Separate storage and compute resources
- **Sidecar Deployment**: Deploy as sidecar container in the same pod for isolated monitoring

## Features

- **Worker Metrics**: Memory, CPU, request durations, error tracking
- **Master Process Intelligence**: Signal tracking, restart analytics
- **Multiprocess Support**: Full Prometheus multiprocess compatibility
- **Redis Storage**: Store metrics directly in Redis (no files created)
- **YAML Configuration**: Structured, readable configuration management with environment variable override
- **Protocol-Based Design**: Leverages Prometheus specification's brilliant protocol architecture
- **Zero Configuration**: Works out-of-the-box with minimal setup
- **Production Ready**: Retry logic, error handling, health monitoring

## Quick Start

### Installation

**Basic installation (sync and thread workers only):**

```bash
pip install gunicorn-prometheus-exporter
```

**With async worker support:**

```bash
# Install with all async worker types
pip install gunicorn-prometheus-exporter[async]

# Or install specific worker types
pip install gunicorn-prometheus-exporter[eventlet]  # For eventlet workers
pip install gunicorn-prometheus-exporter[gevent]    # For gevent workers
```

**With Redis storage:**

```bash
pip install gunicorn-prometheus-exporter[redis]
```

**Complete installation (all features):**

```bash
pip install gunicorn-prometheus-exporter[all]
```

### Docker Image (Docker Hub)

The published container lives at `princekrroshan01/gunicorn-prometheus-exporter`. See the Docker Hub listing for tags and architecture support: <https://hub.docker.com/r/princekrroshan01/gunicorn-prometheus-exporter>

```bash
# Pull the latest stable exporter image
docker pull princekrroshan01/gunicorn-prometheus-exporter:0.2.4

# Run the exporter standalone
docker run --rm -p 9091:9091 princekrroshan01/gunicorn-prometheus-exporter:0.2.4
```

The container exposes metrics on `0.0.0.0:9091` by default. Override behaviour via environment variables such as `PROMETHEUS_METRICS_PORT`, `PROMETHEUS_BIND_ADDRESS`, and `PROMETHEUS_MULTIPROC_DIR`.

For the sidecar pattern, reuse the manifest under *Deployment Options → Sidecar Deployment* and reference the same image/tag.

### Basic Usage

#### Option A: YAML Configuration (Recommended)

Create a YAML configuration file (`gunicorn-prometheus-exporter.yml`):

```yaml
exporter:
  prometheus:
    metrics_port: 9091
    bind_address: "0.0.0.0"
    multiproc_dir: "/tmp/prometheus_multiproc"
  gunicorn:
    workers: 2
    timeout: 30
    keepalive: 2
  redis:
    enabled: false
  ssl:
    enabled: false
  cleanup:
    db_files: true
```

Create a Gunicorn config file (`gunicorn.conf.py`):

```python
from gunicorn_prometheus_exporter import load_yaml_config

# Load YAML configuration
load_yaml_config("gunicorn-prometheus-exporter.yml")

# Import hooks after loading YAML config
from gunicorn_prometheus_exporter.hooks import (
    default_when_ready,
    default_on_starting,
    default_worker_int,
    default_on_exit,
    default_post_fork,
)

# Gunicorn settings
bind = "0.0.0.0:8000"
workers = 2
worker_class = "gunicorn_prometheus_exporter.PrometheusWorker"

# Use pre-built hooks
when_ready = default_when_ready
on_starting = default_on_starting
worker_int = default_worker_int
on_exit = default_on_exit
post_fork = default_post_fork
```

#### Option B: Environment Variables

Create a Gunicorn config file (`gunicorn.conf.py`):

```python
# Basic configuration
bind = "0.0.0.0:8000"

# Worker configuration based on workload type
# For I/O-bound applications (typical web apps):
workers = 9  # 2 × CPU cores + 1 (classic Gunicorn formula)
# For CPU-bound applications:
# workers = 4  # 1 × CPU cores

# Prometheus exporter worker classes
# Sync workers (blocking I/O) - good for most web applications
worker_class = "gunicorn_prometheus_exporter.PrometheusWorker"

# Async workers (non-blocking I/O) - for high-concurrency apps
# worker_class = "gunicorn_prometheus_exporter.PrometheusEventletWorker"
# worker_connections = 1000  # connections per worker (async only)

# Optional: Custom hooks for advanced setup
def when_ready(server):
    from gunicorn_prometheus_exporter.hooks import default_when_ready
    default_when_ready(server)
```

**Worker Count Guidelines:**
- **Sync workers**: `2 × CPU cores + 1` (classic formula for I/O-bound apps)
- **Async workers**: `1-4 workers` (each handles many concurrent connections)
- **CPU-bound workloads**: Use closer to CPU core count
- **Memory considerations**: Each worker consumes ~50-100MB RAM
- **Monitor and adjust**: Start with the formula, then tune based on your app's behavior

### Production Configuration Examples

#### High-Traffic Web Application (I/O-bound)
```python
# gunicorn.conf.py for a typical web app
bind = "0.0.0.0:8000"
workers = 9  # 2×4 cores + 1 = 9 workers
worker_class = "gunicorn_prometheus_exporter.PrometheusWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Prometheus metrics
def when_ready(server):
    from gunicorn_prometheus_exporter.hooks import default_when_ready
    default_when_ready(server)
```

#### High-Concurrency API (Async)
```python
# gunicorn.conf.py for high-concurrency API
bind = "0.0.0.0:8000"
workers = 4  # Fewer workers for async
worker_class = "gunicorn_prometheus_exporter.PrometheusEventletWorker"
worker_connections = 2000  # More connections per worker
max_requests = 2000
timeout = 60

# Prometheus metrics
def when_ready(server):
    from gunicorn_prometheus_exporter.hooks import default_when_ready
    default_when_ready(server)
```

#### CPU-Intensive Application
```python
# gunicorn.conf.py for CPU-bound workloads
bind = "0.0.0.0:8000"
workers = 4  # 1×4 cores = 4 workers
worker_class = "gunicorn_prometheus_exporter.PrometheusWorker"
max_requests = 500
timeout = 120

# Prometheus metrics
def when_ready(server):
    from gunicorn_prometheus_exporter.hooks import default_when_ready
    default_when_ready(server)
```

### Supported Worker Types

The exporter supports all major Gunicorn worker types:

| Worker Class               | Concurrency Model | Use Case                               | Installation                                         |
| -------------------------- | ----------------- | -------------------------------------- | ---------------------------------------------------- |
| `PrometheusWorker`         | Pre-fork (sync)   | Simple, reliable, 1 request per worker | `pip install gunicorn-prometheus-exporter`           |
| `PrometheusThreadWorker`   | Threads           | I/O-bound apps, better concurrency     | `pip install gunicorn-prometheus-exporter`           |
| `PrometheusEventletWorker` | Greenlets         | Async I/O with eventlet                | `pip install gunicorn-prometheus-exporter[eventlet]` |
| `PrometheusGeventWorker`   | Greenlets         | Async I/O with gevent                  | `pip install gunicorn-prometheus-exporter[gevent]`   |

### Start Gunicorn

```bash
gunicorn -c gunicorn.conf.py app:app
```

### Access Metrics

Metrics are automatically exposed on the configured bind address and port (default: `0.0.0.0:9091`):

```bash
# Using default configuration
curl http://0.0.0.0:9091/metrics

# Or use your configured bind address
curl http://YOUR_BIND_ADDRESS:9091/metrics
```

## Documentation

**Complete documentation is available at: [https://princekrroshan01.github.io/gunicorn-prometheus-exporter](https://princekrroshan01.github.io/gunicorn-prometheus-exporter)**

The documentation includes:

- Installation and configuration guides
- YAML configuration guide with examples
- Complete metrics reference
- Framework-specific examples (Django, FastAPI, Flask, Pyramid)
- API reference and troubleshooting
- Contributing guidelines

## Available Metrics

The Gunicorn Prometheus Exporter provides comprehensive metrics for monitoring both worker processes and the master process. All metrics include appropriate labels for detailed analysis.

### Worker Metrics

#### Request Metrics
- **`gunicorn_worker_requests_total`** - Total number of requests handled by each worker
  - Labels: `worker_id`
  - Type: Counter

- **`gunicorn_worker_request_duration_seconds`** - Request duration histogram
  - Labels: `worker_id`
  - Type: Histogram
  - Buckets: 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, +Inf

- **`gunicorn_worker_request_size_bytes`** - Request size histogram
  - Labels: `worker_id`
  - Type: Histogram
  - Buckets: 1KB, 4KB, 16KB, 64KB, 256KB, 1MB, 4MB, +Inf

- **`gunicorn_worker_response_size_bytes`** - Response size histogram
  - Labels: `worker_id`
  - Type: Histogram
  - Buckets: 1KB, 4KB, 16KB, 64KB, 256KB, 1MB, 4MB, +Inf

#### Error Metrics
- **`gunicorn_worker_failed_requests`** - Total number of failed requests
  - Labels: `worker_id`, `method`, `endpoint`, `error_type`
  - Type: Counter

- **`gunicorn_worker_error_handling`** - Total number of errors handled
  - Labels: `worker_id`, `method`, `endpoint`, `error_type`
  - Type: Counter

#### System Metrics
- **`gunicorn_worker_memory_bytes`** - Memory usage per worker
  - Labels: `worker_id`
  - Type: Gauge

- **`gunicorn_worker_cpu_percent`** - CPU usage per worker
  - Labels: `worker_id`
  - Type: Gauge

- **`gunicorn_worker_uptime_seconds`** - Worker uptime
  - Labels: `worker_id`
  - Type: Gauge

#### State Metrics
- **`gunicorn_worker_state`** - Current state of the worker
  - Labels: `worker_id`, `state`, `timestamp`
  - Type: Gauge
  - Values: 1=running, 0=stopped

#### Restart Metrics
- **`gunicorn_worker_restart_total`** - Total worker restarts by reason
  - Labels: `worker_id`, `reason`
  - Type: Counter

- **`gunicorn_worker_restart_count_total`** - Worker restarts by type and reason
  - Labels: `worker_id`, `restart_type`, `reason`
  - Type: Counter

### Master Metrics

#### Restart Metrics
- **`gunicorn_master_worker_restart_total`** - Total worker restarts by reason
  - Labels: `reason`
  - Type: Counter
  - Common reasons: `hup`, `usr1`, `usr2`, `ttin`, `ttou`, `chld`, `int`

- **`gunicorn_master_worker_restart_count_total`** - Worker restarts by worker and reason
  - Labels: `worker_id`, `reason`, `restart_type`
  - Type: Counter

### Metric Labels Explained

#### Worker Labels
- **`worker_id`**: Unique identifier for each worker process
- **`method`**: HTTP method (GET, POST, PUT, DELETE, etc.)
- **`endpoint`**: Request endpoint/path
- **`error_type`**: Type of error (exception class name)
- **`state`**: Worker state (running, stopped, etc.)
- **`timestamp`**: Unix timestamp of state change
- **`reason`**: Reason for restart (signal name or error type)
- **`restart_type`**: Type of restart (signal, error, manual, etc.)

#### Master Labels
- **`reason`**: Signal or reason that triggered the restart
  - `hup`: HUP signal (reload configuration)
  - `usr1`: USR1 signal (reopen log files)
  - `usr2`: USR2 signal (upgrade on the fly)
  - `ttin`: TTIN signal (increase worker count)
  - `ttou`: TTOU signal (decrease worker count)
  - `chld`: CHLD signal (child process status change)
  - `int`: INT signal (interrupt/Ctrl+C)

### Example Queries

#### Basic Monitoring
```promql
# Total requests across all workers
sum(gunicorn_worker_requests_total)

# Average request duration
rate(gunicorn_worker_request_duration_seconds_sum[5m]) / rate(gunicorn_worker_request_duration_seconds_count[5m])

# Memory usage per worker
gunicorn_worker_memory_bytes

# CPU usage per worker
gunicorn_worker_cpu_percent
```

#### Error Analysis
```promql
# Failed requests by endpoint
sum by (endpoint) (rate(gunicorn_worker_failed_requests[5m]))

# Error rate by worker
sum by (worker_id) (rate(gunicorn_worker_error_handling[5m]))
```

#### Restart Monitoring
```promql
# Worker restarts by reason
sum by (reason) (rate(gunicorn_master_worker_restart_total[5m]))

# Restart frequency per worker
sum by (worker_id) (rate(gunicorn_worker_restart_total[5m]))
```

#### Performance Analysis
```promql
# Request size distribution
histogram_quantile(0.95, rate(gunicorn_worker_request_size_bytes_bucket[5m]))

# Response time percentiles
histogram_quantile(0.99, rate(gunicorn_worker_request_duration_seconds_bucket[5m]))
```


## Examples

See the `example/` directory for complete working examples with all worker types:

### Basic Examples

- `gunicorn_simple.conf.py`: Basic sync worker setup
- `gunicorn_thread_worker.conf.py`: Threaded workers for I/O-bound apps
- `gunicorn_redis_integration.conf.py`: Redis storage setup (no files)

### Async Worker Examples

- `gunicorn_eventlet_async.conf.py`: Eventlet workers with async app
- `gunicorn_gevent_async.conf.py`: Gevent workers with async app

### Test Applications

- `app.py`: Simple Flask app for sync/thread workers
- `async_app.py`: Async-compatible Flask app for async workers

Run any example with:

```bash
cd example
gunicorn --config gunicorn_simple.conf.py app:app
```

## Testing Status

All worker types have been thoroughly tested and are production-ready:

| Worker Type         | Status  | Metrics     | Master Signals  | Load Distribution |
| ------------------- | ------- | ----------- | --------------- | ----------------- |
| **Sync Worker**     | Working | All metrics | HUP, USR1, CHLD | Balanced          |
| **Thread Worker**   | Working | All metrics | HUP, USR1, CHLD | Balanced          |
| **Eventlet Worker** | Working | All metrics | HUP, USR1, CHLD | Balanced          |
| **Gevent Worker**   | Working | All metrics | HUP, USR1, CHLD | Balanced          |

All async workers require their respective dependencies:

- Eventlet: `pip install eventlet`
- Gevent: `pip install gevent`

## Configuration

### YAML Configuration (Recommended)

Create a YAML configuration file for structured, readable configuration:

```yaml
# gunicorn-prometheus-exporter.yml
exporter:
  prometheus:
    metrics_port: 9091
    bind_address: "0.0.0.0"
    multiproc_dir: "/tmp/prometheus_multiproc"
  gunicorn:
    workers: 2
    timeout: 30
    keepalive: 2
  redis:
    enabled: false
    host: "localhost"
    port: 6379
    db: 0
    password: ""
    key_prefix: "gunicorn"
    ttl_seconds: 300
  ssl:
    enabled: false
    certfile: ""
    keyfile: ""
  cleanup:
    db_files: true
```

Load YAML configuration in your Gunicorn config:

```python
from gunicorn_prometheus_exporter import load_yaml_config

# Load YAML configuration
load_yaml_config("gunicorn-prometheus-exporter.yml")
```

### Environment Variables

Environment variables can override YAML configuration values:

| Variable                   | Default                  | Description                                               |
| -------------------------- | ------------------------ | --------------------------------------------------------- |
| `PROMETHEUS_METRICS_PORT`  | `9091`                   | Port for metrics endpoint                                 |
| `PROMETHEUS_BIND_ADDRESS`  | `0.0.0.0`                | Bind address for metrics                                  |
| `GUNICORN_WORKERS`         | `1`                      | Number of workers                                         |
| `PROMETHEUS_MULTIPROC_DIR` | Auto-generated           | Multiprocess directory                                    |
| `REDIS_ENABLED`            | `false`                  | Enable Redis storage (no files created)                   |
| `REDIS_HOST`               | `127.0.0.1`              | Redis server hostname                                     |
| `REDIS_PORT`               | `6379`                   | Redis server port                                         |
| `REDIS_DB`                 | `0`                      | Redis database number                                     |
| `REDIS_PASSWORD`           | *(none)*                 | Redis password (optional)                                 |
| `REDIS_KEY_PREFIX`         | `gunicorn`               | Prefix for Redis keys                                     |

### Gunicorn Hooks

```python
# Basic setup
from gunicorn_prometheus_exporter.hooks import default_when_ready

def when_ready(server):
    default_when_ready(server)

# With Redis storage (no files created)
from gunicorn_prometheus_exporter.hooks import redis_when_ready

def when_ready(server):
    redis_when_ready(server)
```

## Deployment Options

### Quick Start
- **Local Development**: See [Deployment Guide](docs/examples/deployment-guide.md#quick-start)
- **Docker**: See [Docker Deployment](docs/examples/deployment-guide.md#docker-deployment)
- **Kubernetes**: See [Kubernetes Deployment](docs/examples/deployment-guide.md#kubernetes-deployment)

### Kubernetes Deployment Options

The exporter supports two main Kubernetes deployment patterns:

#### Sidecar Deployment

Deploy the exporter as a **sidecar container** within the same Kubernetes pod for isolated monitoring:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gunicorn-app-with-sidecar
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gunicorn-app
  template:
    metadata:
      labels:
        app: gunicorn-app
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9091"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        # Main application container
        - name: app
          image: princekrroshan01/gunicorn-app:0.2.4
          ports:
            - containerPort: 8200
              name: http
          env:
            - name: PROMETHEUS_MULTIPROC_DIR
              value: "/tmp/prometheus_multiproc"
            - name: GUNICORN_WORKERS
              value: "4"
          volumeMounts:
            - name: prometheus-data
              mountPath: /tmp/prometheus_multiproc

        # Prometheus exporter sidecar
        - name: prometheus-exporter
          image: princekrroshan01/gunicorn-prometheus-exporter:0.2.4
          ports:
            - containerPort: 9091
              name: metrics
          env:
            - name: PROMETHEUS_METRICS_PORT
              value: "9091"
            - name: PROMETHEUS_BIND_ADDRESS
              value: "0.0.0.0"
            - name: PROMETHEUS_MULTIPROC_DIR
              value: "/tmp/prometheus_multiproc"
          volumeMounts:
            - name: prometheus-data
              mountPath: /tmp/prometheus_multiproc
      volumes:
        - name: prometheus-data
          emptyDir: {}
```

**Benefits:**
- **Isolation**: Metrics collection separate from application logic
- **Resource Management**: Independent resource limits
- **Security**: Reduced attack surface
- **Maintenance**: Update monitoring independently

#### DaemonSet Deployment

Deploy the exporter as a **DaemonSet** for cluster-wide infrastructure monitoring:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: gunicorn-prometheus-exporter-daemonset
spec:
  selector:
    matchLabels:
      app: gunicorn-prometheus-exporter
      component: daemonset
  template:
    metadata:
      labels:
        app: gunicorn-prometheus-exporter
        component: daemonset
    spec:
      hostNetwork: true
      containers:
        - name: prometheus-exporter
          image: princekrroshan01/gunicorn-prometheus-exporter:0.2.4
          ports:
            - containerPort: 9091
              name: metrics
          env:
            - name: PROMETHEUS_METRICS_PORT
              value: "9091"
            - name: REDIS_ENABLED
              value: "true"
            - name: REDIS_HOST
              value: "redis-service"
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
```

**Benefits:**
- **Cluster Coverage**: One pod per node for complete cluster monitoring
- **Infrastructure Monitoring**: Node-level application insights
- **Automatic Scaling**: Scales automatically with cluster size
- **Host Network Access**: Direct access to node-level services

### Deployment Comparison

| Feature | Sidecar Deployment | DaemonSet Deployment |
|---------|-------------------|---------------------|
| **Use Case** | Application-specific monitoring | Cluster-wide infrastructure monitoring |
| **Scaling** | Manual replica scaling | Automatic (one per node) |
| **Network** | ClusterIP services | Host network access |
| **Coverage** | Specific applications | All applications on all nodes |
| **Resource** | Shared across pods | Dedicated per node |
| **Best For** | Production applications | Infrastructure monitoring, development environments |
| **Manifest Location** | `k8s/sidecar-deployment.yaml` | `k8s/sidecar-daemonset.yaml` |

### Complete Kubernetes Examples

Find complete Kubernetes manifests in the [`k8s/`](k8s/) directory:

- **Sidecar Deployment**: `k8s/sidecar-deployment.yaml`
- **DaemonSet Deployment**: `k8s/sidecar-daemonset.yaml`
- **Services**: `k8s/daemonset-service.yaml`, `k8s/daemonset-metrics-service.yaml`
- **Network Policies**: `k8s/daemonset-netpol.yaml`
- **Complete Setup**: See [`k8s/README.md`](k8s/README.md) for full deployment guide

### Future Deployment Options

We're actively testing and will add support for:
- **Helm Charts** - Kubernetes package management
- **Terraform** - Infrastructure as Code
- **Ansible** - Configuration management
- **AWS ECS/Fargate** - Container orchestration
- **Google Cloud Run** - Serverless containers
- **Azure Container Instances** - Managed containers

See the [Deployment Guide](docs/examples/deployment-guide.md) for complete deployment options and configurations.

## Testing

This project follows the Test Pyramid with comprehensive testing at all levels:

```
┌─────────────────────────────────────┐
│  E2E Tests (e2e/)                   │  ← Docker + Kubernetes
├─────────────────────────────────────┤
│  Integration Tests (integration/)   │  ← Component integration
├─────────────────────────────────────┤
│  Unit Tests (tests/)                │  ← pytest
└─────────────────────────────────────┘
```

### Quick Test (Local Development)

```bash
# Make sure Redis is running
brew services start redis  # macOS
sudo systemctl start redis  # Linux

# Run quick test
cd e2e
make quick-test
```

### Full System Test (CI/CD)

```bash
# Complete automated test (installs everything)
cd e2e
make integration-test        # Redis integration test (auto-starts Redis)
```

### Using Make Commands

```bash
cd e2e
make quick-test    # Fast local testing
make integration-test   # Redis integration test (auto-starts Redis)
make install       # Install dependencies
make clean         # Clean up
```

**Test Coverage**:

- ✅ Unit tests (`tests/`) - pytest-based function testing
- ✅ Integration tests (`integration/`) - Component integration
- ✅ E2E tests (`e2e/`) - Docker + Kubernetes deployment
- ✅ Redis integration and storage
- ✅ Multi-worker Gunicorn setup
- ✅ All metric types (counters, gauges, histograms)
- ✅ Request processing and metrics capture
- ✅ Signal handling and graceful shutdown
- ✅ CI/CD automation

See [`e2e/README.md`](e2e/README.md) for detailed E2E test documentation.

## Contributing

Contributions are welcome! Please see our [contributing guide](https://princekrroshan01.github.io/gunicorn-prometheus-exporter/contributing/) for details.

**Current Issues**: Check our [GitHub Issues](https://github.com/Agent-Hellboy/gunicorn-prometheus-exporter/issues) for known issues and feature requests.

### Development Setup

```bash
# Install dependencies
cd e2e
make install

# Run tests
make quick-test
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

> *Production recommendation*: All Docker/Kubernetes examples ship with `REDIS_ENABLED=true`. Redis-backed storage is the supported default for any multi-worker or multi-pod deployment. Only disable Redis when running a single Gunicorn worker for local demos.

See [Docker README](../docker/README.md) and [Kubernetes Guide](../k8s/README.md) for deployment details.

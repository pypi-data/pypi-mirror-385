# msgtrace - Deployment Guide

Complete guide for deploying msgtrace in various environments.

## Table of Contents

- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Local Development (Fastest)

```bash
# 1. Build the frontend
cd src/msgtrace/frontend
npm install
npm run build

# 2. Start the server (serves API + Frontend)
cd ../../..
msgtrace start --port 4321

# 3. Open browser
open http://localhost:4321
```

The server now serves both the API (`/api/v1/*`) and the frontend UI (`/`).

---

## Development Setup

### Backend Only (API Development)

```bash
# Start backend without frontend
msgtrace start --port 4321
```

### Frontend Only (UI Development)

```bash
# Terminal 1: Backend
msgtrace start --port 4321

# Terminal 2: Frontend (with hot reload)
cd src/msgtrace/frontend
npm run dev

# Access at http://localhost:3000 (proxies API to :4321)
```

### Full Stack Development

```bash
# Use the provided script
python src/msgtrace/build_frontend.py && msgtrace start
```

---

## Production Deployment

### Option 1: Standalone Server

```bash
# 1. Build frontend for production
cd src/msgtrace/frontend
npm install --production
npm run build

# 2. Install Python package
cd ../../..
pip install -e .

# 3. Run with production settings
msgtrace start \
  --host 0.0.0.0 \
  --port 4321 \
  --db-path /var/lib/msgtrace/msgtrace.db
```

### Option 2: Systemd Service

Create `/etc/systemd/system/msgtrace.service`:

```ini
[Unit]
Description=msgtrace - Trace Visualization for msgflux
After=network.target

[Service]
Type=simple
User=msgtrace
Group=msgtrace
WorkingDirectory=/opt/msgtrace
Environment="PATH=/opt/msgtrace/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/msgtrace/venv/bin/msgtrace start --host 0.0.0.0 --port 4321 --db-path /var/lib/msgtrace/msgtrace.db
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable msgtrace
sudo systemctl start msgtrace
sudo systemctl status msgtrace
```

---

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# 1. Navigate to msgtrace directory
cd src/msgtrace

# 2. Build and start
docker-compose up -d

# 3. Check status
docker-compose ps
docker-compose logs -f

# 4. Access at http://localhost:4321
```

### Using Docker Directly

```bash
# Build image
docker build -t msgtrace:latest -f src/msgtrace/Dockerfile .

# Run container
docker run -d \
  --name msgtrace \
  -p 4321:4321 \
  -v msgtrace-data:/app/data \
  -e MSGTRACE_DB_PATH=/app/data/msgtrace.db \
  msgtrace:latest

# Check logs
docker logs -f msgtrace
```

### Docker Compose with Nginx (Production)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  msgtrace:
    build:
      context: ../..
      dockerfile: src/msgtrace/Dockerfile
    expose:
      - "4321"
    volumes:
      - msgtrace-data:/app/data
    environment:
      - MSGTRACE_DB_PATH=/app/data/msgtrace.db
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - msgtrace
    restart: unless-stopped

volumes:
  msgtrace-data:
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Cloud Deployment

### AWS (ECS + Fargate)

1. **Build and Push Image**

```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t msgtrace:latest -f src/msgtrace/Dockerfile .
docker tag msgtrace:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/msgtrace:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/msgtrace:latest
```

2. **Create ECS Task Definition** (example)

```json
{
  "family": "msgtrace",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "msgtrace",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/msgtrace:latest",
      "portMappings": [
        {
          "containerPort": 4321,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MSGTRACE_DB_PATH",
          "value": "/app/data/msgtrace.db"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "msgtrace-data",
          "containerPath": "/app/data"
        }
      ]
    }
  ],
  "volumes": [
    {
      "name": "msgtrace-data",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-xxxxx"
      }
    }
  ]
}
```

### Google Cloud (Cloud Run)

```bash
# Build and push
gcloud builds submit --tag gcr.io/<project-id>/msgtrace

# Deploy
gcloud run deploy msgtrace \
  --image gcr.io/<project-id>/msgtrace \
  --platform managed \
  --port 4321 \
  --allow-unauthenticated \
  --region us-central1
```

### DigitalOcean (App Platform)

Create `app.yaml`:

```yaml
name: msgtrace
services:
  - name: web
    dockerfile_path: src/msgtrace/Dockerfile
    github:
      repo: your-org/your-repo
      branch: main
      deploy_on_push: true
    http_port: 4321
    instance_count: 1
    instance_size_slug: basic-xxs
    routes:
      - path: /
```

Deploy:
```bash
doctl apps create --spec app.yaml
```

### Heroku

```bash
# Create app
heroku create msgtrace-app

# Set buildpack
heroku buildpacks:add --index 1 heroku/nodejs
heroku buildpacks:add --index 2 heroku/python

# Deploy
git push heroku main
```

---

## Configuration

### Environment Variables

```bash
# Database
export MSGTRACE_DB_PATH="/path/to/msgtrace.db"

# Server
export MSGTRACE_HOST="0.0.0.0"
export MSGTRACE_PORT="4321"

# CORS (comma-separated origins)
export MSGTRACE_CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"

# Queue
export MSGTRACE_QUEUE_SIZE="1000"
```

### Configuration File

Create `msgtrace.config.py`:

```python
from msgtrace.core.config import MsgTraceConfig

config = MsgTraceConfig(
    host="0.0.0.0",
    port=4321,
    db_path="/var/lib/msgtrace/msgtrace.db",
    cors_origins=["https://yourdomain.com"],
    queue_size=1000,
)
```

Use with:
```python
from msgtrace.backend.api.app import create_app
from msgtrace.config import config

app = create_app(config)
```

---

## Monitoring

### Health Check

```bash
curl http://localhost:4321/health
# Response: {"status": "healthy"}
```

### Prometheus Metrics (Future)

```yaml
# Add to docker-compose.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
```

### Logging

```python
# Configure logging level
import logging
logging.basicConfig(level=logging.INFO)
```

Docker logs:
```bash
docker-compose logs -f msgtrace
```

---

## Troubleshooting

### Frontend Not Loading

**Symptom**: API works but frontend shows 404

**Solution**:
```bash
# Rebuild frontend
cd src/msgtrace/frontend
npm run build

# Verify dist exists
ls -la dist/

# Restart server
msgtrace start --port 4321
```

### Database Locked

**Symptom**: `database is locked` errors

**Solutions**:
1. Check for multiple processes accessing the database
2. Use WAL mode (default in SQLite)
3. Consider PostgreSQL for high-concurrency

### CORS Errors

**Symptom**: Browser console shows CORS errors

**Solution**:
```bash
# Add your origin to CORS settings
msgtrace start --cors-origins "http://localhost:3000,https://yourdomain.com"
```

### Port Already in Use

**Symptom**: `Address already in use`

**Solution**:
```bash
# Find process using port 4321
lsof -i :4321
# or
netstat -tulpn | grep 4321

# Kill process or use different port
msgtrace start --port 4322
```

### High Memory Usage

**Solutions**:
1. Increase Docker memory limit
2. Limit queue size: `--queue-size 500`
3. Clean old traces periodically
4. Consider PostgreSQL with retention policies

---

## Security Checklist

For production deployments:

- [ ] Use HTTPS (SSL/TLS)
- [ ] Enable authentication (future feature)
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting (via nginx)
- [ ] Regular database backups
- [ ] Keep dependencies updated
- [ ] Monitor access logs
- [ ] Use firewall rules
- [ ] Implement log rotation

---

## Backup and Restore

### Backup

```bash
# SQLite backup
sqlite3 msgtrace.db ".backup msgtrace-backup-$(date +%Y%m%d).db"

# With Docker
docker exec msgtrace sqlite3 /app/data/msgtrace.db ".backup /app/data/backup.db"
docker cp msgtrace:/app/data/backup.db ./backup.db
```

### Restore

```bash
# Copy backup
cp msgtrace-backup.db msgtrace.db

# With Docker
docker cp backup.db msgtrace:/app/data/msgtrace.db
docker-compose restart msgtrace
```

---

## Performance Tuning

### SQLite Optimizations

```python
# In storage configuration
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=-64000;  # 64MB cache
PRAGMA temp_store=MEMORY;
```

### Uvicorn Workers

```bash
# Multiple workers for production
uvicorn msgtrace.backend.api.app:app \
  --host 0.0.0.0 \
  --port 4321 \
  --workers 4 \
  --loop uvloop
```

---

## Next Steps

- Set up monitoring and alerting
- Configure automated backups
- Implement authentication
- Scale horizontally with load balancer
- Add database replication
- Set up CI/CD pipeline

For questions or issues, see the main README.md or open an issue.

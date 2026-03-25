# SentinelAI Deployment Guide

## Overview
SentinelAI is a full-stack ML monitoring application with:
- **Frontend**: React application with Nginx
- **Backend**: FastAPI with PostgreSQL and Redis
- **ML Training**: Jupyter with GPU support

## Prerequisites
- Docker and Docker Compose
- NVIDIA GPU with drivers (for model training)
- NVIDIA Container Toolkit (for GPU access in Docker)

## Quick Start

### 1. Production Deployment (All Services)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

#### Access Points:
- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Jupyter Lab**: http://localhost:8888
- **PgAdmin**: http://localhost:5050
- **Database**: localhost:5432
- **Redis**: localhost:6379

### 2. Development Mode (Frontend with Hot Reload)

For frontend development with hot reload:

```bash
# Start backend services first
docker-compose up -d backend db redis

# Start frontend in development mode
docker-compose -f docker-compose.dev.yml up
```

Frontend will be available at http://localhost:3000 with hot reload enabled.

## Service Details

### Frontend
- **Technology**: React 18 with React Router
- **Server**: Nginx (production) or Node dev server (development)
- **API Integration**: Configured to communicate with backend via nginx reverse proxy

**Configuration**:
- Production: Uses Nginx reverse proxy to `/api` -> `backend:8000`
- Development: Direct connection to `http://localhost:8000`

### Backend
- **Technology**: FastAPI with async SQLAlchemy
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Authentication**: JWT with Bearer tokens

**Environment Variables** (`.env` file required in `sentinel-ai/` directory):
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/sentinel

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=SentinelAI
APP_VERSION=1.0.0
```

### Database
- **Type**: PostgreSQL 15 Alpine
- **Default Credentials**:
  - User: `postgres`
  - Password: `postgres`
  - Database: `sentinel`

### Model Training
- **Technology**: Jupyter Lab with Python 3.10
- **GPU**: NVIDIA GPU support enabled
- **Volumes**:
  - `./model_training/images` - Training images
  - `./model_training/runs` - Model outputs
  - `./model_training/notebooks` - Jupyter notebooks

## Network Architecture

All services communicate via a Docker bridge network (`sentinelai-network`):

```
Frontend (nginx:80)
    ↓
    → /api/* → Backend (FastAPI:8000)
                  ↓
                  → Database (PostgreSQL:5432)
                  → Cache (Redis:6379)
```

## Initial Setup

### 1. Create Environment File

```bash
cd sentinel-ai
cp .env.example .env
# Edit .env with your configuration
```

### 2. Initialize Database

The database is automatically initialized on first startup via the backend's lifespan handler.

To seed initial data:
```bash
docker-compose exec backend python -m app.seeders.seed
```

### 3. Build and Start Services

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check service health
docker-compose ps
```

## Frontend Development

### Environment Variables
Create `sentinel-ai/frontend/.env` from `.env.example`:

```env
REACT_APP_API_URL=http://localhost:8000
CHOKIDAR_USEPOLLING=true
WATCHPACK_POLLING=true
```

### Available Scripts

```bash
# Development mode (in container)
docker-compose -f docker-compose.dev.yml up

# Local development (requires Node.js)
cd sentinel-ai/frontend
npm install
npm start

# Build production
npm run build

# Run tests
npm test
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/     # Reusable components
│   ├── pages/         # Page components
│   ├── services/      # API service layer
│   ├── App.js         # Main app component
│   └── index.js       # Entry point
├── public/            # Static files
├── Dockerfile         # Production build
├── Dockerfile.dev     # Development build
└── nginx.conf         # Nginx configuration
```

## Backend Development

### API Documentation
Access interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Database Migrations
```bash
# Access backend container
docker-compose exec backend bash

# Run migrations (implement with Alembic if needed)
# alembic upgrade head
```

### Testing
```bash
# Run backend tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app
```

## Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db
```

### Service Health Checks
- Backend Health: http://localhost:8000/health
- Frontend: http://localhost (should load dashboard)

## Troubleshooting

### Frontend Can't Connect to Backend
1. Check backend is running: `docker-compose ps backend`
2. Check CORS is enabled in backend
3. Verify network connectivity: `docker-compose exec frontend ping backend`

### Database Connection Issues
1. Check database is running: `docker-compose ps db`
2. Verify credentials in `.env` file
3. Check logs: `docker-compose logs db`

### GPU Not Available in Jupyter
1. Verify NVIDIA drivers: `nvidia-smi`
2. Check NVIDIA Container Toolkit is installed
3. Restart Docker daemon

### Port Conflicts
If ports are already in use, modify them in `docker-compose.yml`:
```yaml
ports:
  - "8080:80"  # Change 80 to 8080 for frontend
  - "8001:8000"  # Change 8000 to 8001 for backend
```

## Security Considerations

### Production Deployment
1. **Change Default Passwords**:
   - Database password
   - PgAdmin credentials
   - JWT secret key

2. **Configure CORS**:
   Update `backend/app/main.py` to specify allowed origins:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

3. **Use Environment Variables**:
   Never commit `.env` files to version control

4. **Enable HTTPS**:
   Configure SSL certificates in Nginx

5. **Database Backups**:
   ```bash
   docker-compose exec db pg_dump -U postgres sentinel > backup.sql
   ```

## Maintenance

### Update Services
```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Production Checklist

- [ ] Update all default passwords
- [ ] Configure CORS with specific origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure proper logging
- [ ] Set up database backups
- [ ] Configure monitoring alerts
- [ ] Review and update security settings
- [ ] Test disaster recovery procedures
- [ ] Document custom configurations

## Support

For issues and questions:
- Check logs: `docker-compose logs`
- Review API documentation: http://localhost:8000/docs
- Check database with PgAdmin: http://localhost:5050

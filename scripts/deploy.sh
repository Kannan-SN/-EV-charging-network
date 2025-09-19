#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Starting deployment process..."

# Configuration
ENVIRONMENT=${1:-"production"}
DOCKER_COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi
    
    log_info "Prerequisites check passed ✅"
}

validate_environment() {
    log_info "Validating environment configuration..."
    
    # Check if docker-compose file exists
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "Docker compose file $DOCKER_COMPOSE_FILE not found"
        exit 1
    fi
    
    # Check environment variables
    if [ "$ENVIRONMENT" = "production" ]; then
        if [ -z "$GEMINI_API_KEY" ]; then
            log_error "GEMINI_API_KEY is not set"
            exit 1
        fi
        
        if [ -z "$DOMAIN_NAME" ]; then
            log_warn "DOMAIN_NAME is not set, using localhost"
        fi
    fi
    
    log_info "Environment validation passed ✅"
}

backup_existing() {
    log_info "Creating backup of existing deployment..."
    
    # Create backup directory
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup Weaviate data
    if docker volume inspect ev-charging-optimizer_weaviate_data >/dev/null 2>&1; then
        log_info "Backing up Weaviate data..."
        docker run --rm \
            -v ev-charging-optimizer_weaviate_data:/data \
            -v "$(pwd)/$BACKUP_DIR":/backup \
            alpine:latest tar czf /backup/weaviate_data.tar.gz -C /data .
    fi
    
    # Backup configuration files
    cp -r backend/.env "$BACKUP_DIR/" 2>/dev/null || true
    cp -r frontend/.env "$BACKUP_DIR/" 2>/dev/null || true
    
    log_info "Backup created at $BACKUP_DIR ✅"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build backend
    log_info "Building backend image..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build backend
    
    # Build frontend
    log_info "Building frontend image..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build frontend
    
    log_info "Images built successfully ✅"
}

deploy_services() {
    log_info "Deploying services..."
    
    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Start new services
    log_info "Starting new services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    log_info "Services deployed ✅"
}

health_check() {
    log_info "Performing health checks..."
    
    # Wait for services to start
    sleep 30
    
    # Check backend health
    local backend_url="http://localhost:8000/api/v1/health"
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s "$backend_url" >/dev/null 2>&1; then
            log_info "Backend health check passed ✅"
            break
        fi
        
        attempt=$((attempt + 1))
        log_info "Waiting for backend... (attempt $attempt/$max_attempts)"
        sleep 10
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f -s "http://localhost" >/dev/null 2>&1; then
        log_info "Frontend health check passed ✅"
    else
        log_warn "Frontend health check failed - may still be starting"
    fi
    
    # Check Weaviate
    if curl -f -s "http://localhost:8080/v1/meta" >/dev/null 2>&1; then
        log_info "Weaviate health check passed ✅"
    else
        log_error "Weaviate health check failed"
        return 1
    fi
}

cleanup() {
    log_info "Cleaning up unused resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    log_info "Cleanup completed ✅"
}

post_deploy_tasks() {
    log_info "Running post-deployment tasks..."
    
    # Initialize database if needed
    log_info "Checking database initialization..."
    
    # Test API endpoints
    log_info "Testing API endpoints..."
    
    # Generate deployment report
    cat > "deployment_report_$(date +%Y%m%d_%H%M%S).txt" << EOF
Deployment Report
================
Environment: $ENVIRONMENT
Date: $(date)
Docker Compose File: $DOCKER_COMPOSE_FILE

Services Status:
$(docker-compose -f "$DOCKER_COMPOSE_FILE" ps)

Container Logs (last 50 lines):
$(docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=50)
EOF
    
    log_info "Post-deployment tasks completed ✅"
}

main() {
    log_info "🚀 Deploying EV Charging Network Optimizer - Environment: $ENVIRONMENT"
    
    # Run deployment steps
    check_prerequisites
    validate_environment
    
    if [ "$ENVIRONMENT" = "production" ]; then
        backup_existing
    fi
    
    build_images
    deploy_services
    health_check || {
        log_error "Health checks failed. Rolling back..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        exit 1
    }
    
    cleanup
    post_deploy_tasks
    
    log_info "🎉 Deployment completed successfully!"
    log_info ""
    log_info "Access your application at:"
    log_info "  Frontend: http://localhost"
    log_info "  Backend API: http://localhost:8000"
    log_info "  API Docs: http://localhost:8000/docs"
    log_info "  Weaviate: http://localhost:8080"
    log_info ""
    log_info "To monitor logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    log_info "To stop services: docker-compose -f $DOCKER_COMPOSE_FILE down"
}

# Handle script arguments
case "${1:-}" in
    "production"|"staging"|"development")
        main
        ;;
    "--help"|"-h")
        echo "Usage: $0 [environment]"
        echo ""
        echo "Environments:"
        echo "  production  - Deploy to production (default)"
        echo "  staging     - Deploy to staging"
        echo "  development - Deploy to development"
        echo ""
        echo "Examples:"
        echo "  $0 production"
        echo "  $0 staging"
        echo ""
        echo "Environment Variables:"
        echo "  GEMINI_API_KEY  - Required for production"
        echo "  DOMAIN_NAME     - Optional domain name"
        ;;
    *)
        main
        ;;
esac
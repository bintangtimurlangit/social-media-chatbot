#!/bin/bash

# Source the banner
source ./branding/banner.sh

# Container Health Check Script
print_compact_banner
echo "Checking container health..."

# Function to check if container is running
check_container() {
    local container_name=$1
    local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
    
    if [ "$status" = "running" ]; then
        echo "✓ $container_name: Running"
        return 0
    else
        echo "✗ $container_name: $status"
        return 1
    fi
}

# Function to check container health
check_container_health() {
    local container_name=$1
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null)
    
    if [ "$health" = "healthy" ]; then
        echo "✓ $container_name: Healthy"
        return 0
    elif [ "$health" = "unhealthy" ]; then
        echo "✗ $container_name: Unhealthy"
        return 1
    else
        echo "? $container_name: No health check"
        return 0
    fi
}

# Check all containers
containers=(
    "social-chatbot-postgres"
    "social-chatbot-qdrant"
    "social-chatbot-redis"
    "social-chatbot-n8n"
    "social-chatbot-backend"
    "social-chatbot-prometheus"
    "social-chatbot-grafana"
    "social-chatbot-loki"
    "social-chatbot-promtail"
    "social-chatbot-uptime"
    "social-chatbot-langfuse"
    "social-chatbot-node-exporter"
    "social-chatbot-cadvisor"
    "social-chatbot-postgres-exporter"
    "social-chatbot-redis-exporter"
)

echo "Container Status:"
echo "=================="

all_healthy=true
for container in "${containers[@]}"; do
    if ! check_container "$container"; then
        all_healthy=false
    fi
done

echo ""
echo "Container Health:"
echo "=================="

for container in "${containers[@]}"; do
    check_container_health "$container"
done

echo ""
if [ "$all_healthy" = true ]; then
    echo "✓ All containers are running!"
else
    echo "✗ Some containers are not running. Check with: docker-compose ps"
fi

echo ""
echo "Service URLs:"
echo "============="
echo "n8n: http://localhost:5678"
echo "Grafana: http://localhost:3000"
echo "Uptime Kuma: http://localhost:3001"
echo "Langfuse: http://localhost:3002"
echo "Backend API: http://localhost:8000"
echo "Prometheus: http://localhost:9090"
echo "Qdrant: http://localhost:6333"

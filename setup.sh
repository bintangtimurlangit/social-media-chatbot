#!/bin/bash

# Social Media Chatbot Setup Script
echo "Setting up Social Media Chatbot..."

# Preflight checks
echo "Running preflight checks..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running. Please start Docker first."
    exit 1
fi

# Check available disk space (at least 5GB)
available_space=$(df / | awk 'NR==2 {print $4}')
if [ "$available_space" -lt 5242880 ]; then
    echo "WARNING: Less than 5GB disk space available. This may cause issues."
fi

# Check available memory (at least 4GB)
total_memory=$(free -m | awk 'NR==2{print $2}')
if [ "$total_memory" -lt 4096 ]; then
    echo "WARNING: Less than 4GB RAM available. Performance may be affected."
fi

echo "Preflight checks completed successfully."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "WARNING: Please edit .env file with your actual values before running docker-compose up"
    echo "   Important: Change all default passwords!"
fi

# Create necessary directories
echo "Creating monitoring directories..."
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/prometheus
mkdir -p monitoring/loki
mkdir -p monitoring/promtail
mkdir -p init-scripts
mkdir -p backend

# Set proper permissions
echo "Setting permissions..."
chmod +x setup.sh
chmod 755 monitoring/
chmod 755 init-scripts/

# Check if .env has been modified
if grep -q "your_" .env 2>/dev/null; then
    echo "WARNING: .env file contains placeholder values!"
    echo "   Please edit .env file with your actual API keys and passwords before starting services."
    echo ""
    echo "   Required changes:"
    echo "   - POSTGRES_PASSWORD"
    echo "   - REDIS_PASSWORD" 
    echo "   - N8N_PASSWORD"
    echo "   - GRAFANA_PASSWORD"
    echo "   - DEEPSEEK_API_KEY"
    echo "   - LANGFUSE_PUBLIC_KEY"
    echo "   - LANGFUSE_SECRET_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

echo "Setup complete!"
echo ""
echo "To check container status, run: ./check-containers.sh"

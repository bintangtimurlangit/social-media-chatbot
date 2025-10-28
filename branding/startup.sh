#!/bin/bash

# Astrals Agency Startup Script
source ./branding/banner.sh

print_banner

echo "🚀 Welcome to Astrals Agency Social Media Chatbot Platform!"
echo ""
echo "This platform provides:"
echo "  • Instagram & WhatsApp integration"
echo "  • AI-powered RAG responses"
echo "  • Real-time conversation management"
echo "  • Comprehensive monitoring & analytics"
echo ""
echo "Quick Commands:"
echo "  ./setup.sh           - Initial setup"
echo "  docker-compose up -d - Start all services"
echo "  ./check-containers.sh - Check service health"
echo "  docker-compose logs -f [service] - View logs"
echo ""
echo "Service URLs (after startup):"
echo "  • n8n Workflows: http://localhost:5678"
echo "  • Grafana Dashboards: http://localhost:3000"
echo "  • Uptime Monitoring: http://localhost:3001"
echo "  • LLM Observability: http://localhost:3002"
echo "  • Backend API: http://localhost:8000"
echo "  • Prometheus Metrics: http://localhost:9090"
echo ""
echo "Ready to revolutionize customer engagement! 🌟"
echo ""

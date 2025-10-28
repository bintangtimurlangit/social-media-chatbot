# Development Phases

## Phase 1: Infrastructure Setup
- Set up VPS with Ubuntu 22.04
- Install Docker and docker-compose
- Configure Cloudflared tunnel
- Set up basic networking and security

## Phase 2: Core Services
- Deploy PostgreSQL
- Deploy Qdrant (vector database)
- Deploy Redis
- Deploy n8n
- Deploy FastAPI backend service
- Deploy monitoring stack (Prometheus, Grafana, Loki)
- Deploy Langfuse for LLM observability
- Deploy Uptime Kuma for health checks

## Phase 3: Database Schema
- Create PostgreSQL tables for knowledge base metadata
- Create tables for messages and sessions
- Create tables for variables and configuration
- Set up Qdrant collections for vector storage
- Set up database migrations

## Phase 4: Google Sheets Integration
- Set up Google Sheets API credentials
- Create knowledge base sheet template
- Build n8n workflow for sheet synchronization
- Implement embedding generation and storage in Qdrant

## Phase 5: RAG Implementation
- Implement hybrid retrieval (Qdrant semantic + PostgreSQL lexical)
- Build context assembly for LLM prompts
- Create confidence scoring system
- Implement fallback mechanisms

## Phase 6: Social Media Integration
- Set up Instagram Graph API
- Set up WhatsApp Business Cloud API
- Configure webhook verification for both platforms
- Build message handling endpoints
- Implement quick replies and buttons

## Phase 7: LLM Integration
- Integrate DeepSeek Cloud API
- Set up fallback LLM providers
- Implement prompt templates
- Add response formatting and validation

## Phase 8: n8n Workflows
- Build main conversation flow
- Create error handling workflows
- Set up monitoring dashboards in Grafana
- Configure Prometheus alerts
- Implement admin management workflows

## Phase 9: Testing & Validation
- Test end-to-end message flows for Instagram and WhatsApp
- Validate RAG accuracy across both platforms
- Test error scenarios and fallbacks
- Performance testing and optimization

## Phase 10: Deployment & Monitoring
- Production deployment
- Configure Grafana dashboards for all services
- Set up Prometheus alerting rules
- Configure backup strategies for PostgreSQL and Qdrant
- Document operational procedures

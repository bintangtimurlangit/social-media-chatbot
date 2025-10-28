## Infrastructure
- Ubuntu 22.04 VPS (4 vCPU / 8 GB RAM)
- Docker + docker-compose
- Cloudflared (tunneling to Cloudflare)

## Messaging Channels
- Instagram Graph API (DMs)
- WhatsApp Business Cloud API

## Orchestration
- n8n (self-hosted)

## Backend Service
- Python 3.11
- FastAPI + Uvicorn
- Pydantic

## Data Storage
- PostgreSQL 15
- Qdrant (vector database)

## Cache / Queue
- Redis 7 (sessions, rate limiting, caching)

## LLM & Embeddings
- Primary LLM: DeepSeek Cloud API
- Optional fallback LLM: OpenAI / Anthropic (via API)
- Embeddings: DeepSeek or OpenAI embeddings

## Retrieval (RAG)
- Vector store: Qdrant
- Hybrid retrieval: semantic (Qdrant) + lexical filtering (PostgreSQL)

## Data Source (Knowledge Base)
- Google Sheets (client-editable source of truth)
- n8n Google Sheets integration for sync

## Observability
- Prometheus (metrics collection)
- Grafana (dashboards and visualization)
- Loki (log aggregation)
- Langfuse (LLM tracing, prompts, cost)
- Uptime Kuma (service health checks)

## Security
- Webhook verification (Meta/Instagram)
- HTTPS termination (Cloudflare)
- Secrets via environment variables and n8n credentials store


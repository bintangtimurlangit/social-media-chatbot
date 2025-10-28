# Social Media Chatbot

A multi-platform social media chatbot with RAG capabilities for Instagram DMs and WhatsApp messages.

## Tech Stack

- **Infrastructure**: Docker, Cloudflared tunneling
- **Messaging**: Instagram Graph API, WhatsApp Business Cloud API
- **Orchestration**: n8n
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL 15 + Qdrant (vector database)
- **Cache**: Redis 7
- **LLM**: DeepSeek Cloud API (primary), OpenAI/Anthropic (fallback)
- **Monitoring**: Prometheus, Grafana, Loki, Langfuse, Uptime Kuma

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/bintangtimurlangit/social-media-chatbot.git
   cd social-media-chatbot
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the services**
   - n8n: https://your-domain.com:5678
   - Grafana: https://your-domain.com:3000
   - Uptime Kuma: https://your-domain.com:3001
   - Langfuse: https://your-domain.com:3002
   - Backend API: https://your-domain.com:8000

## Services

- **PostgreSQL**: Main database (port 5432)
- **Qdrant**: Vector database (port 6333)
- **Redis**: Cache and sessions (port 6379)
- **n8n**: Workflow automation (port 5678)
- **FastAPI**: Backend service (port 8000)
- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Dashboards (port 3000)
- **Loki**: Log aggregation (port 3100)
- **Uptime Kuma**: Health monitoring (port 3001)
- **Langfuse**: LLM observability (port 3002)

## Development

See [PHASES.md](PHASES.md) for development phases and [TECH_STACK.md](TECH_STACK.md) for detailed technology choices.

## License

MIT

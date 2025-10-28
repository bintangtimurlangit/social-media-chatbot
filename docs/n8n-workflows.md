# n8n Workflow Architecture - Astrals Agency Chatbot

## Overview
This document outlines the n8n workflow structure for the Astrals Agency Social Media Chatbot platform, covering Instagram DMs, WhatsApp messages, and knowledge base management.

## Workflow Categories

### 1. **Main Conversation Flow**
**Purpose**: Process incoming messages from Instagram and WhatsApp

#### **Instagram DM Workflow**
```
Instagram Webhook → Message Parser → Backend API → Response Formatter → Instagram Send
```

**Nodes:**
- **Webhook Trigger** (Instagram)
  - URL: `/webhook/instagram`
  - Method: POST
  - Authentication: Verify token

- **Message Parser**
  - Extract: `user_id`, `message_text`, `timestamp`
  - Filter: Only text messages
  - Add metadata: `channel: "instagram"`

- **Backend API Call**
  - URL: `http://backend:8000/api/v1/chat`
  - Method: POST
  - Body: `{user_id, channel, message, language}`
  - Headers: `Content-Type: application/json`

- **Response Handler**
  - Extract: `response`, `confidence_score`, `suggested_actions`
  - Error handling: Fallback message

- **Instagram Send Message**
  - API: Instagram Graph API
  - Endpoint: `/{page-id}/messages`
  - Body: `{recipient: {id: user_id}, message: {text: response}}`

#### **WhatsApp Workflow**
```
WhatsApp Webhook → Message Parser → Backend API → Response Formatter → WhatsApp Send
```

**Nodes:**
- **Webhook Trigger** (WhatsApp)
  - URL: `/webhook/whatsapp`
  - Method: POST
  - Authentication: Verify token

- **Message Parser**
  - Extract: `from`, `text.body`, `timestamp`
  - Filter: Only text messages
  - Add metadata: `channel: "whatsapp"`

- **Backend API Call**
  - URL: `http://backend:8000/api/v1/chat`
  - Method: POST
  - Body: `{user_id: from, channel, message: text.body, language}`

- **Response Handler**
  - Extract: `response`, `confidence_score`, `suggested_actions`
  - Error handling: Fallback message

- **WhatsApp Send Message**
  - API: WhatsApp Business API
  - Endpoint: `/{phone-number-id}/messages`
  - Body: `{messaging_product: "whatsapp", to: from, type: "text", text: {body: response}}`

### 2. **Knowledge Base Management**
**Purpose**: Sync knowledge base from Google Sheets to Qdrant

#### **Google Sheets Sync Workflow**
```
Google Sheets Trigger → Data Validation → Embedding Generation → Qdrant Update → Backend Sync
```

**Nodes:**
- **Google Sheets Trigger**
  - Sheet: "KnowledgeBase"
  - Trigger: On change
  - Frequency: Every 5 minutes

- **Data Validation**
  - Required fields: `id`, `category`, `canonical_answer`
  - Filter: `status = "active"`
  - Validate: Language codes, content length

- **Text Preparation**
  - Combine: `user_query_examples` + `canonical_answer` + `category`
  - Clean: Remove special characters, normalize text
  - Language detection: Auto-detect if not specified

- **Embedding Generation**
  - API: OpenAI Embeddings
  - Model: `text-embedding-3-small`
  - Input: Prepared text
  - Output: 384-dimensional vector

- **Qdrant Update**
  - Collection: `knowledge_base`
  - Operation: Upsert
  - Payload: `{id, category, language, canonical_answer, follow_up_suggestions, status}`
  - Vector: Generated embedding

- **Backend Sync Notification**
  - URL: `http://backend:8000/api/v1/knowledge/sync`
  - Method: POST
  - Body: `{source: "google_sheets", force_update: false}`

### 3. **Error Handling & Monitoring**
**Purpose**: Handle failures and send alerts

#### **Error Handler Workflow**
```
Error Trigger → Log Error → Send Alert → Fallback Response
```

**Nodes:**
- **Error Trigger**
  - Trigger: On workflow error
  - Conditions: Any error in main flows

- **Error Logger**
  - Log to: Structured logs
  - Include: Error message, stack trace, context
  - Level: ERROR

- **Alert Notification**
  - Channel: Telegram/Slack
  - Message: Error details + timestamp
  - Include: Workflow name, error type

- **Fallback Response**
  - Message: "Sorry, I'm experiencing technical difficulties. Please try again later."
  - Send to: Original user
  - Log: Fallback used

#### **Health Check Workflow**
```
Cron Trigger → Service Health Check → Alert if Down → Log Status
```

**Nodes:**
- **Cron Trigger**
  - Schedule: Every 5 minutes
  - Timezone: UTC

- **Service Health Checks**
  - Backend: `GET http://backend:8000/api/v1/health`
  - Database: `GET http://postgres:5432`
  - Redis: `GET http://redis:6379`
  - Qdrant: `GET http://qdrant:6333/collections`

- **Health Aggregator**
  - Combine: All service statuses
  - Calculate: Overall health score
  - Threshold: 80% healthy

- **Alert Logic**
  - If: Health < 80%
  - Then: Send alert
  - Include: Failed services list

### 4. **Admin Management**
**Purpose**: Administrative tasks and monitoring

#### **Admin Dashboard Workflow**
```
Manual Trigger → Service Status → Metrics Collection → Dashboard Update
```

**Nodes:**
- **Manual Trigger**
  - Type: Webhook
  - URL: `/admin/dashboard`
  - Method: GET

- **Service Status Collector**
  - Backend: Health check
  - Database: Connection test
  - Redis: Memory usage
  - Qdrant: Collection stats

- **Metrics Collector**
  - Messages processed: Last 24h
  - Response times: Average, P95, P99
  - Error rates: By service
  - User sessions: Active count

- **Dashboard Response**
  - Format: JSON
  - Include: All metrics + status
  - Cache: 30 seconds

#### **Knowledge Base Management Workflow**
```
Manual Trigger → KB Operations → Validation → Update Backend
```

**Nodes:**
- **Manual Trigger**
  - Type: Webhook
  - URL: `/admin/kb/{operation}`
  - Method: POST
  - Operations: `sync`, `validate`, `backup`

- **Operation Router**
  - Sync: Trigger Google Sheets sync
  - Validate: Check KB integrity
  - Backup: Export KB data

- **Validation Logic**
  - Check: Required fields
  - Verify: Embeddings exist
  - Test: Search functionality

- **Backend Update**
  - URL: `http://backend:8000/api/v1/knowledge-base/*`
  - Method: POST/PUT
  - Body: Operation results

## Workflow Dependencies

### **Data Flow**
```
Google Sheets → n8n Sync → Qdrant + PostgreSQL → Backend API → n8n Chat → Social Media
```

### **Error Flow**
```
Any Error → n8n Error Handler → Alerts → Fallback Response
```

### **Monitoring Flow**
```
Health Checks → n8n Monitor → Alerts → Admin Dashboard
```

## Configuration

### **Environment Variables**
```bash
# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_password
N8N_HOST=your-domain.com

# API Endpoints
BACKEND_URL=http://backend:8000
GOOGLE_SHEETS_ID=your_sheet_id
QDRANT_URL=http://qdrant:6333

# Social Media APIs
INSTAGRAM_ACCESS_TOKEN=your_token
WHATSAPP_ACCESS_TOKEN=your_token
```

### **Webhook URLs**
- Instagram: `https://your-domain.com/webhook/instagram`
- WhatsApp: `https://your-domain.com/webhook/whatsapp`
- Admin: `https://your-domain.com/admin/*`

## Security Considerations

### **Authentication**
- Webhook verification tokens
- API key authentication
- Basic auth for n8n interface

### **Rate Limiting**
- Instagram: 1000 messages/day
- WhatsApp: 1000 messages/day
- Backend API: 100 requests/minute

### **Data Privacy**
- No PII storage in n8n
- Session data in Redis only
- Message logs in PostgreSQL

## Monitoring & Alerts

### **Key Metrics**
- Message processing time
- Error rates by service
- Knowledge base sync success
- User satisfaction scores

### **Alert Conditions**
- Service down > 2 minutes
- Error rate > 5%
- Response time > 10 seconds
- Knowledge base sync failure

### **Dashboard Views**
- Real-time message flow
- Service health status
- Error logs and trends
- Performance metrics

## Troubleshooting

### **Common Issues**
1. **Webhook not receiving data**
   - Check Cloudflared tunnel
   - Verify webhook URLs
   - Check Instagram/WhatsApp app settings

2. **Backend API errors**
   - Check backend container status
   - Verify database connections
   - Check API key validity

3. **Knowledge base sync failures**
   - Check Google Sheets permissions
   - Verify Qdrant connection
   - Check embedding API limits

### **Debug Steps**
1. Check n8n execution logs
2. Verify webhook payloads
3. Test API endpoints manually
4. Check container health status

## Next Steps

1. **Deploy n8n workflows** after backend is running
2. **Configure webhook endpoints** with social media platforms
3. **Set up monitoring dashboards** in Grafana
4. **Test end-to-end message flow** with sample data
5. **Implement custom business logic** as needed

---

*This document is part of the Astrals Agency Social Media Chatbot platform documentation.*

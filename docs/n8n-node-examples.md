# n8n Node Configuration Examples - Astrals Agency

## 1. Instagram DM Processing Workflow

### **Webhook Trigger Node**
```json
{
  "name": "Instagram Webhook",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "instagram",
    "responseMode": "responseNode",
    "options": {
      "noResponseBody": false
    }
  }
}
```

### **Message Parser Node**
```json
{
  "name": "Parse Instagram Message",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": "// Extract message data from Instagram webhook\nconst entry = $input.first().json.entry[0];\nconst messaging = entry.messaging[0];\n\nreturn {\n  user_id: messaging.sender.id,\n  message: messaging.message.text,\n  timestamp: messaging.timestamp,\n  channel: 'instagram'\n};"
  }
}
```

### **Backend API Call Node**
```json
{
  "name": "Call Backend API",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://backend:8000/api/v1/chat",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "user_id": "={{ $json.user_id }}",
      "channel": "={{ $json.channel }}",
      "message": "={{ $json.message }}",
      "language": "en"
    },
    "options": {
      "timeout": 10000
    }
  }
}
```

### **Instagram Send Message Node**
```json
{
  "name": "Send Instagram Reply",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "https://graph.facebook.com/v18.0/{{ $env.INSTAGRAM_PAGE_ID }}/messages",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{ $env.INSTAGRAM_ACCESS_TOKEN }}",
      "Content-Type": "application/json"
    },
    "body": {
      "recipient": {
        "id": "={{ $('Parse Instagram Message').item.json.user_id }}"
      },
      "message": {
        "text": "={{ $json.response }}"
      }
    }
  }
}
```

## 2. WhatsApp Message Processing

### **WhatsApp Webhook Node**
```json
{
  "name": "WhatsApp Webhook",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "whatsapp",
    "responseMode": "responseNode"
  }
}
```

### **WhatsApp Message Parser**
```json
{
  "name": "Parse WhatsApp Message",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": "// Extract WhatsApp message data\nconst entry = $input.first().json.entry[0];\nconst changes = entry.changes[0];\nconst value = changes.value;\nconst message = value.messages[0];\n\nreturn {\n  user_id: message.from,\n  message: message.text.body,\n  timestamp: message.timestamp,\n  channel: 'whatsapp'\n};"
  }
}
```

### **WhatsApp Send Message Node**
```json
{
  "name": "Send WhatsApp Reply",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "https://graph.facebook.com/v18.0/{{ $env.WHATSAPP_PHONE_NUMBER_ID }}/messages",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{ $env.WHATSAPP_ACCESS_TOKEN }}",
      "Content-Type": "application/json"
    },
    "body": {
      "messaging_product": "whatsapp",
      "to": "={{ $('Parse WhatsApp Message').item.json.user_id }}",
      "type": "text",
      "text": {
        "body": "={{ $json.response }}"
      }
    }
  }
}
```

## 3. Google Sheets Knowledge Base Sync

### **Google Sheets Trigger**
```json
{
  "name": "Google Sheets Trigger",
  "type": "n8n-nodes-base.googleSheetsTrigger",
  "parameters": {
    "authentication": "oAuth2",
    "spreadsheetId": "{{ $env.GOOGLE_SHEETS_ID }}",
    "sheetName": "KnowledgeBase",
    "triggerOn": "change"
  }
}
```

### **Data Validation Node**
```json
{
  "name": "Validate KB Data",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": "// Validate knowledge base entry\nconst data = $input.first().json;\n\n// Check required fields\nif (!data.id || !data.category || !data.canonical_answer) {\n  throw new Error('Missing required fields: id, category, canonical_answer');\n}\n\n// Filter only active entries\nif (data.status !== 'active') {\n  return null;\n}\n\n// Prepare text for embedding\nconst text = [\n  data.user_query_examples || '',\n  data.canonical_answer,\n  data.category\n].join(' ').trim();\n\nreturn {\n  id: data.id,\n  category: data.category,\n  language: data.language || 'en',\n  canonical_answer: data.canonical_answer,\n  follow_up_suggestions: data.follow_up_suggestions || '',\n  status: data.status,\n  text_for_embedding: text\n};"
  }
}
```

### **OpenAI Embeddings Node**
```json
{
  "name": "Generate Embeddings",
  "type": "n8n-nodes-base.openAi",
  "parameters": {
    "resource": "embedding",
    "operation": "create",
    "model": "text-embedding-3-small",
    "input": "={{ $json.text_for_embedding }}"
  }
}
```

### **Qdrant Upsert Node**
```json
{
  "name": "Update Qdrant",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://qdrant:6333/collections/knowledge_base/points",
    "method": "PUT",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "points": [
        {
          "id": "={{ $('Validate KB Data').item.json.id }}",
          "vector": "={{ $json.data[0].embedding }}",
          "payload": {
            "id": "={{ $('Validate KB Data').item.json.id }}",
            "category": "={{ $('Validate KB Data').item.json.category }}",
            "language": "={{ $('Validate KB Data').item.json.language }}",
            "canonical_answer": "={{ $('Validate KB Data').item.json.canonical_answer }}",
            "follow_up_suggestions": "={{ $('Validate KB Data').item.json.follow_up_suggestions }}",
            "status": "={{ $('Validate KB Data').item.json.status }}"
          }
        }
      ]
    }
  }
}
```

## 4. Error Handling Workflow

### **Error Trigger Node**
```json
{
  "name": "Error Trigger",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "error-handler",
    "responseMode": "responseNode"
  }
}
```

### **Error Logger Node**
```json
{
  "name": "Log Error",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": "// Log error details\nconst error = $input.first().json;\nconst timestamp = new Date().toISOString();\n\nconsole.log(`[ERROR] ${timestamp}:`, {\n  workflow: error.workflow_name || 'Unknown',\n  node: error.node_name || 'Unknown',\n  error: error.error_message,\n  context: error.context || {}\n});\n\nreturn {\n  timestamp,\n  level: 'ERROR',\n  message: error.error_message,\n  workflow: error.workflow_name,\n  node: error.node_name,\n  context: error.context\n};"
  }
}
```

### **Telegram Alert Node**
```json
{
  "name": "Send Telegram Alert",
  "type": "n8n-nodes-base.telegram",
  "parameters": {
    "operation": "sendMessage",
    "chatId": "{{ $env.TELEGRAM_CHAT_ID }}",
    "text": "🚨 *Astrals Agency Chatbot Error*\n\n*Workflow:* {{ $('Log Error').item.json.workflow }}\n*Node:* {{ $('Log Error').item.json.node }}\n*Error:* {{ $('Log Error').item.json.message }}\n*Time:* {{ $('Log Error').item.json.timestamp }}",
    "parseMode": "Markdown"
  }
}
```

## 5. Health Check Workflow

### **Cron Trigger Node**
```json
{
  "name": "Health Check Trigger",
  "type": "n8n-nodes-base.cron",
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "minutes",
          "minutesInterval": 5
        }
      ]
    }
  }
}
```

### **Backend Health Check**
```json
{
  "name": "Check Backend",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://backend:8000/api/v1/health/detailed",
    "method": "GET",
    "options": {
      "timeout": 5000
    }
  }
}
```

### **Health Aggregator**
```json
{
  "name": "Aggregate Health",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": "// Aggregate health status from all services\nconst services = {\n  backend: $('Check Backend').item.json,\n  // Add other service checks here\n};\n\nconst healthyServices = Object.values(services).filter(service => \n  service.status === 'healthy'\n).length;\n\nconst totalServices = Object.keys(services).length;\nconst healthPercentage = (healthyServices / totalServices) * 100;\n\nreturn {\n  overall_health: healthPercentage,\n  healthy_services: healthyServices,\n  total_services: totalServices,\n  services: services,\n  timestamp: new Date().toISOString()\n};"
  }
}
```

## 6. Admin Dashboard Workflow

### **Admin Webhook**
```json
{
  "name": "Admin Dashboard",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "GET",
    "path": "admin/dashboard",
    "responseMode": "responseNode"
  }
}
```

### **Metrics Collector**
```json
{
  "name": "Collect Metrics",
  "type": "n8n-nodes-base.function",
  "parameters": {
    "functionCode": "// Collect system metrics\nconst now = new Date();\nconst last24h = new Date(now.getTime() - 24 * 60 * 60 * 1000);\n\nreturn {\n  timestamp: now.toISOString(),\n  metrics: {\n    messages_processed_24h: 0, // Query from database\n    average_response_time: 0,  // Calculate from logs\n    error_rate: 0,             // Calculate from error logs\n    active_sessions: 0,        // Query from Redis\n    knowledge_base_entries: 0  // Query from Qdrant\n  },\n  services: {\n    backend: 'healthy',\n    database: 'healthy',\n    redis: 'healthy',\n    qdrant: 'healthy'\n  }\n};"
  }
}
```

## Environment Variables Required

```bash
# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_password
N8N_HOST=your-domain.com

# Backend API
BACKEND_URL=http://backend:8000

# Google Sheets
GOOGLE_SHEETS_ID=your_sheet_id
GOOGLE_SHEETS_CREDENTIALS=your_credentials

# Qdrant
QDRANT_URL=http://qdrant:6333

# Social Media APIs
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_PAGE_ID=your_page_id
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id

# Monitoring
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# OpenAI
OPENAI_API_KEY=your_openai_key
```

## Workflow Execution Order

1. **Setup Phase**
   - Deploy all containers
   - Configure environment variables
   - Test individual services

2. **Webhook Configuration**
   - Set up Instagram webhook
   - Set up WhatsApp webhook
   - Test webhook endpoints

3. **Knowledge Base Setup**
   - Create Google Sheets template
   - Configure sync workflow
   - Test knowledge base sync

4. **Monitoring Setup**
   - Configure health checks
   - Set up error handling
   - Test alert notifications

5. **Production Testing**
   - End-to-end message flow
   - Error scenario testing
   - Performance monitoring

---

*These node configurations are part of the Astrals Agency Social Media Chatbot platform.*

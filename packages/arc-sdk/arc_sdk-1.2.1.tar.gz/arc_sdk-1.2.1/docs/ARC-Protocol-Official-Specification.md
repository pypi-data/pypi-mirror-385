# ARC Protocol Specification
**Agent Remote Communication Protocol**  
**Version 1.0**  
**Date: January 2025**

---

## Table of Contents
1. [Overview](#overview)
2. [Protocol Architecture](#protocol-architecture)
3. [Message Structure](#message-structure)
4. [Error Handling](#error-handling)
5. [Agent Discovery](#agent-discovery)
6. [Method Definitions](#method-definitions)
7. [Data Types](#data-types)
8. [Authentication & Security](#authentication--security)
9. [Implementation Examples](#implementation-examples)
10. [Comparison to Existing Protocols](#comparison-to-existing-protocols)
11. [Implementation Guidelines](#implementation-guidelines)

---

## Overview

**ARC (Agent Remote Communication)** is the first RPC protocol that solves multi-agent deployment complexity with built-in agent routing, load balancing, and workflow tracing. Deploy hundreds of different agent types on a single endpoint with zero infrastructure overhead - no service discovery, no API gateways, no orchestration engines required.

### Key Features
- **Multi-Agent Architecture**: Single endpoint supports multiple agents with built-in routing
- **Load Balancing Ready**: Multiple instances of the same agent via `requestAgent`/`targetAgent` routing
- **High-Dimensional Agent Calls**: Complex multi-agent workflows with automatic routing
- **Unified Deployment**: Host different agent types on single URL with agent-level routing
- **Workflow Tracing**: End-to-end traceability across multi-agent processes via `traceId`
- **Agent-Centric Routing**: Built-in agent identification and routing at protocol level
- **Stateless Design**: Each request is independent with no session state
- **Lightweight**: Minimal overhead with only essential fields
- **Method-Based**: Clean RPC-style method invocation
- **Transport Agnostic**: Works over HTTP, WebSockets, or any transport layer
- **Comprehensive Error Handling**: 500+ categorized error codes with detailed context for debugging and monitoring

### Why ARC?
Existing protocols require complex infrastructure for multi-agent scenarios. ARC solves this with:

#### **Multi-Agent Capabilities (Unique to ARC)**
- **Single Endpoint, Multiple Agents**: Deploy 10s or 100s of agents behind `https://company.com/arc`
- **Built-in Load Balancing**: Route to `finance-agent-01`, `finance-agent-02`, `finance-agent-03` automatically  
- **Cross-Agent Workflows**: Agent A → Agent B → Agent C with full traceability via `traceId`
- **Unified Agent Management**: No need for service discovery or complex routing infrastructure

#### **Missing in Other Protocols**
- **JSON-RPC 2.0**: No agent routing, manual endpoint management, no workflow tracing
- **gRPC**: Service-per-endpoint, complex load balancing setup, no built-in agent concepts
- **REST**: Resource-oriented, not agent-oriented, manual workflow correlation

---

### Design Goals
- **Simplicity**: Easy to understand, implement, and debug
- **Agent-Focused**: Designed specifically for autonomous agent communication
- **Performance**: Low latency and minimal bandwidth overhead
- **Scalability**: Support for large-scale agent ecosystems
- **Security**: Built-in authentication and authorization patterns
- **Observability**: Comprehensive tracing and monitoring capabilities
- **RPC Foundation**: Leverages proven RPC patterns for reliability
- **Extensible**: Optional fields allow protocol evolution without breaking changes
- **Robust Error Handling**: Detailed, categorized error codes enable precise debugging and system monitoring

---

## Protocol Architecture

### Transport Layer
- **Protocol**: HTTPS (required for production)
- **Method**: POST only
- **Endpoint**: `/arc` (recommended)
- **Content-Type**: `application/arc+json`
- **Authentication**: OAuth 2.0 Bearer tokens (recommended)

ARC follows a **stateless RPC pattern** where:
- Each request is a complete, self-contained message
- Agents are identified at the protocol level (not buried in params)
- Single endpoint handles all communication (`/arc`)
- HTTPS required for production deployments
- OAuth 2.0 Bearer tokens recommended for authentication
- Optional distributed tracing for workflow correlation

```
┌─────────────────┐    HTTP POST /arc    ┌─────────────────┐
│   Agent A       │ ────────────────────> │   Agent B       │
│ (requestAgent)  │                       │ (targetAgent)   │
└─────────────────┘ <──────────────────── └─────────────────┘
                       HTTP Response
```

### Multi-Agent Server Architecture
ARC supports single-endpoint, multi-agent deployments:
```
https://company.com/arc  ← Single endpoint
├── finance-analyzer-01
├── document-processor-03  
├── report-generator-05
└── email-sender-02
```

---

## Message Structure

### Request Object

An ARC request is represented by a JSON object with the following structure:

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `arc` | String | Yes | Protocol version. MUST be "1.0" |
| `id` | String/Number | Yes | Unique request identifier for correlation |
| `method` | String | Yes | Method name to be invoked |
| `requestAgent` | String | Yes | ID of the agent sending the request |
| `targetAgent` | String | Yes | ID of the agent that should handle the request |
| `params` | Object | Yes | Method-specific parameters |
| `traceId` | String | No | Workflow tracking ID for multi-agent processes |

### Request Structure
```json
{
  "arc": "1.0",                              // Required: Protocol version
  "id": "msg_abc123",                        // Required: Request identifier  
  "method": "task.create",                  // Required: Method to invoke
  "requestAgent": "finance-analyzer-01",     // Required: Sending agent ID
  "targetAgent": "document-processor-03",    // Required: Target agent ID
  "traceId": "trace_report_20240115_abc123", // Optional: Workflow tracking
  "params": {                                // Required: Method parameters
    "initialMessage": {
      "role": "user",
      "parts": [{"type": "TextPart", "content": "Process quarterly report"}]
    },
    "priority": "HIGH"
  }
}
```

### Response Object

An ARC response is represented by a JSON object with the following structure:

### Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `arc` | String | Yes | Protocol version. MUST be "1.0" |
| `id` | String/Number | Yes | MUST match the request ID |
| `responseAgent` | String | Yes | ID of the agent that processed the request |
| `targetAgent` | String | Yes | ID of the agent that should receive the response |
| `result` | Object/null | Yes* | Method result data (see Result Types below for structure) |
| `error` | Object/null | Yes* | Error information (null if successful) |
| `traceId` | String | No | Same workflow tracking ID from request |

*Note: Either `result` OR `error` must be present, but not both.

### Success Response Structure
```json
{
  "arc": "1.0",                              // Required: Protocol version
  "id": "msg_abc123",                        // Required: Matches request ID
  "responseAgent": "document-processor-03",  // Required: Responding agent ID
  "targetAgent": "finance-analyzer-01",      // Required: Target for response
  "traceId": "trace_report_20240115_abc123", // Optional: Same as request
  "result": {                                // Success result OR error (not both)
    "type": "task",
    "task": {
      "taskId": "task-12345",
      "status": "SUBMITTED",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  },
  "error": null                              // Error object if failed
}
```

### Result Types

ARC responses use different result structures depending on the operation type:

| Result Structure | Description | Used By Methods |
|------------------|-------------|-----------------|
| `{"type": "task"}` | Task-related operations that return data | `task.create`, `task.get`, `task.cancel`, `task.subscribe` |
| `{"type": "stream"}` | Stream-related operations that return data | `stream.start`, `stream.end` |
| `{"success": true}` | Simple acknowledgments for message operations | `task.send`, `stream.message` |

**Examples:**

```json
// Task data response
{
  "type": "task",
  "task": {"taskId": "task-123", "status": "SUBMITTED", ...}
}

// Stream data response  
{
  "type": "stream",
  "stream": {"streamId": "stream-456", "status": "ACTIVE", ...}
}

// Simple acknowledgment response
{
  "success": true,                     // Required: Operation success indicator
  "message": "Message sent successfully"  // Optional: Human-readable confirmation
}
```

---

## Error Handling

### Error Object Structure
When an error occurs, the `error` field MUST contain an object with:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | Number | Yes | Numeric error code (integer) |
| `message` | String | Yes | Human-readable error description |
| `details` | Any | No | Optional additional error information |

### Standard Error Codes

#### JSON-RPC Standard Errors
| Code | Description |
|------|-------------|
| -32700 | Parse error (invalid JSON) |
| -32600 | Invalid request (malformed ARC message) |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |

#### ARC-Specific Errors

**Agent Errors (-41000 to -41099)**
| Code | Description |
|------|-------------|
| -41001 | Agent not found |
| -41002 | Agent not available |
| -41003 | Agent unreachable |
| -41004 | Invalid agent ID |
| -41005 | Agent authentication failed |
| -41006 | Agent timeout |
| -41010 | Multiple agents with same ID |
| -41011 | Agent capacity exceeded |
| ... | *Reserved for future agent errors* |

**Task Errors (-42000 to -42099)**
| Code | Description |
|------|-------------|
| -42001 | Task not found |
| -42002 | Task already completed |
| -42003 | Task already canceled |
| -42004 | Task execution failed |
| -42005 | Task timeout |
| -42006 | Invalid task status transition |
| -42010 | Task priority invalid |
| -42011 | Task deadline exceeded |
| ... | *Reserved for future task errors* |

**Stream Errors (-43000 to -43099)**
| Code | Description |
|------|-------------|
| -43001 | Stream not found |
| -43002 | Stream already closed |
| -43003 | Stream timeout |
| -43004 | Stream participant limit exceeded |
| -43005 | Invalid stream message |
| -43006 | Stream buffer overflow |
| ... | *Reserved for future stream errors* |

**Security Errors (-44000 to -44099)**
| Code | Description |
|------|-------------|
| -44001 | Authentication failed |
| -44002 | Authorization failed |
| -44003 | Insufficient OAuth2 scope |
| -44004 | Token expired |
| -44005 | Token invalid |
| -44006 | Permission denied |
| -44007 | Rate limit exceeded |
| -44008 | IP address blocked |
| ... | *Reserved for future security errors* |

**Protocol Errors (-45000 to -45099)**
| Code | Description |
|------|-------------|
| -45001 | Invalid ARC version |
| -45002 | Missing required field |
| -45003 | Invalid field format |
| -45004 | Message too large |
| -45005 | Workflow trace invalid |
| -45006 | Circular reference detected |
| ... | *Reserved for future protocol errors* |

### Error Response Example
```json
{
  "arc": "1.0",
  "id": "msg_abc123",
  "responseAgent": "document-processor-03",
  "targetAgent": "finance-analyzer-01",
  "traceId": "trace_report_20240115_abc123",
  "result": null,
  "error": {
    "code": -41002,
    "message": "Agent not available",
    "details": {
      "agentId": "missing-agent",
      "suggestion": "Check agent registry"
    }
  }
}
```

---

## Agent Discovery

Agent discovery is handled through simple HTTP endpoints, separate from the ARC protocol:

### Agent Information Endpoint Example
```
GET /agent-info
```
```json
{
  "agentId": "finance-analyzer-01",
  "capabilities": ["document-analysis", "financial-reporting"],
  "prompt": [Finance analyzer agent used for ...]
  "version": "1.2.0",
  "status": "active",
  "endpoints": {
    "arc": "/arc"
  },
  "supportedMethods": [
    "agent.getCapabilities",
    "task.create",
    "task.execute"
  ]
}
```

---

## Method Definitions

ARC defines **10 standard methods** across three categories:

### Method Categories Overview

#### 1. Task Methods (Asynchronous)
For long-running, asynchronous agent operations where work may take time to complete:

- **`task.create`** - Initiate a new asynchronous task with an agent. Use when you want to delegate work that may take time to complete (e.g., document analysis, report generation).

- **`task.send`** - Send additional message to an existing task. **Only used when the task status is `INPUT_REQUIRED`** - meaning the agent needs more information from you to continue processing the task.

- **`task.get`** - Retrieve current task status, conversation history, and any generated artifacts. Use to check progress or get final results when task is completed.

- **`task.cancel`** - Cancel a running task before completion. Use when you no longer need the task results or want to stop processing.

- **`task.subscribe`** - Subscribe to receive webhook notifications about task status changes. Use when you want to be notified automatically instead of polling with `task.get`.

#### 2. Stream Methods (Real-time)
For real-time, interactive agent communication where you need immediate back-and-forth conversation:

- **`stream.start`** - Begin a real-time conversation with an agent, including the first message. Use for interactive scenarios like customer support, collaborative editing, or live assistance.

- **`stream.message`** - Send follow-up messages in an active stream conversation. Use to continue the real-time dialogue after the stream is established.

- **`stream.end`** - Terminate an active stream conversation. Use when the interactive session is complete or you want to free up resources.

#### 3. Notification Methods (Server-initiated)
Methods that agents use to push updates back to requesters:

- **`task.notification`** - Sent by the **processing agent** to notify about task progress, completion, or status changes. The target agent that received the task uses this to report back.

- **`stream.chunk`** - Sent by the **processing agent** to push real-time data chunks during an active stream. Used for streaming responses, live updates, or progressive results.

---

## Detailed Method Specifications

### Task Methods (Asynchronous)
For long-running, asynchronous agent operations.

#### `task.create`
Create a new asynchronous task.

**Request Params:**
```json
{
  "initialMessage": {          // Required: Initial message to start the task
    "role": "user", 
    "parts": [{"type": "TextPart", "content": "Process document"}]
  },
  "priority": "NORMAL",        // Optional: LOW, NORMAL, HIGH, URGENT
  "metadata": {                // Optional: Custom task metadata
    "deadline": "2024-01-15T17:00:00Z",
    "department": "finance",
    "EmployeeID": "35462617"
  }
}
```

**Response Result:**
```json
{
  "type": "task",               // Required: Response type indicator
  "task": {
    "taskId": "task-12345",     // Required: Server-generated unique task identifier
    "status": "SUBMITTED",      // Required: SUBMITTED, WORKING, INPUT_REQUIRED, COMPLETED, FAILED, CANCELED
    "createdAt": "2024-01-15T10:30:00Z"  // Required: ISO timestamp when task was created
  }
}
```

#### `task.send`
Send a message to an existing task.

**Request Params:**
```json
{
  "taskId": "task-12345",      // Required: Task identifier    
  "message": {                 // Required: Message object to send
    "role": "user",
    "parts": [{"type": "TextPart", "content": "Please prioritize the financial analysis"}]
  }
}
```

**Response Result:**
```json
{
  "success": true,                     // Required: Operation success indicator
  "message": "Message sent to task successfully"  // Optional: Human-readable confirmation
}
```

#### `task.get`
Retrieve task status and history.

**Request Params:**
```json
{
  "taskId": "task-12345",      // Required: Task identifier
  "includeMessages": true,     // Optional: default true – Include full conversation
  "includeArtifacts": true     // Optional: default true – Include all artifacts
}
```

**Response Result:**
```json
{
  "type": "task",
  "task": {
    "taskId": "task-12345",     // Required: Task identifier
    "status": "WORKING",        // Required: Current task status
    "createdAt": "2024-01-15T10:30:00Z",  // Required: Creation timestamp
    "updatedAt": "2024-01-15T10:35:00Z",  // Optional: Last update timestamp
    "messages": [               // Optional: Based on includeMessages parameter
      {
        "role": "user",
        "parts": [{"type": "TextPart", "content": "Process document"}],
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ],
    "artifacts": [              // Optional: Based on includeArtifacts parameter
      {
        "artifactId": "artifact-123",
        "name": "Analysis Report",
        "mimeType": "application/pdf",
        "createdAt": "2024-01-15T10:32:00Z"
      }
    ]
  }
}
```

#### `task.cancel`
Cancel an existing task.

**Request Params:**
```json
{
  "taskId": "task-12345",       // Required: Task identifier
  "reason": "Priority changed"  // Optional
}
```

**Response Result:**
```json
{
  "type": "task",
  "task": {
    "taskId": "task-12345",     // Required: Task identifier
    "status": "CANCELED",       // Required: New status after cancellation
    "canceledAt": "2024-01-15T10:40:00Z",  // Required: Cancellation timestamp
    "reason": "Priority changed"  // Optional: Cancellation reason
  }
}
```

#### `task.subscribe`
Subscribe to task notifications via webhook.

**Request Params:**
```json
{
  "taskId": "task-12345",
  "callbackUrl": "https://myserver.com/webhooks/tasks",
  "events": ["TASK_COMPLETED", "TASK_FAILED"]  // Optional: default ["TASK_COMPLETED", "TASK_FAILED"]
}
```

**Response Result:**
```json
{
  "type": "task",
  "subscription": {
    "subscriptionId": "sub-67890",  // Required: Server-generated subscription ID
    "taskId": "task-12345",         // Required: Task being monitored
    "callbackUrl": "https://myserver.com/webhooks/tasks",  // Required: Webhook URL
    "events": ["TASK_COMPLETED", "TASK_FAILED"],  // Required: Subscribed events
    "createdAt": "2024-01-15T10:30:00Z",  // Required: Subscription timestamp
    "active": true                  // Required: Subscription status
  }
}
```

**Available Events:**
- `TASK_CREATED` - Task was created  
- `TASK_STARTED` - Agent began processing
- `TASK_PAUSED` - Task paused (waiting for input)
- `TASK_RESUMED` - Task resumed processing  
- `TASK_COMPLETED` - Task finished successfully
- `TASK_FAILED` - Task failed with error
- `TASK_CANCELED` - Task was canceled
- `NEW_MESSAGE` - New message added to task
- `NEW_ARTIFACT` - New file/output generated
- `STATUS_CHANGE` - Any status transition (catch-all)

---

### Stream Methods (Real-time)
For real-time, interactive agent communication.

#### `stream.start`
Start a real-time conversation stream with an initial message.

**Request Params:**
```json
{
  "initialMessage": {              // Required: Initial message to start the conversation
    "role": "user",
    "parts": [{"type": "TextPart", "content": "Hello, I need help with my account"}]
  },
  "metadata": {                    // Optional: Custom stream metadata
    "EmployeeID": "238764638",
    "context": "customer-support"
  }
}
```

**Response Result:**
```json
{
  "type": "stream",
  "stream": {
    "streamId": "stream-67890",   // Required
    "status": "ACTIVE",           // Required: ACTIVE, PAUSED, CLOSED
    "participants": ["chat-agent-01"],  // Optional
    "createdAt": "2024-01-15T10:30:00Z" // Optional
  }
}
```

#### `stream.message`
Continue conversation in an active stream (used for follow-up messages).

**Request Params:**
```json
{
  "streamId": "stream-67890",   // Required
  "message": {                  // Required
    "role": "user",
    "parts": [{"type": "TextPart", "content": "What's the weather like?"}]
  }
}
```

**Response Result:**
```json
{
  "success": true,                     // Required: Operation success indicator  
  "message": "Message sent to stream successfully"  // Optional: Human-readable confirmation
}
```

#### `stream.end`
End an active stream.

**Request Params:**
```json
{
  "streamId": "stream-67890",   // Required
  "reason": "Conversation completed"  // Optional
}
```

**Response Result:**
```json
{
  "type": "stream",
  "stream": {
    "streamId": "stream-67890",
    "status": "CLOSED",
    "closedAt": "2024-01-15T10:45:00Z",
    "reason": "Conversation completed"
  }
}
```

---

### Notification Methods (Server-initiated)
For server-to-client notifications.

#### `task.notification`
Server-initiated task status notification.

**Request Params:**
```json
{
  "taskId": "task-12345",
  "event": "TASK_COMPLETED",    // See Available Events in task.subscribe
  "timestamp": "2024-01-15T10:35:00Z",
  "data": {
    "status": "COMPLETED",        // Required: string - current task status
    "message": "Task finished successfully",  // Required: string - human-readable description
    // ... optional event-specific fields below
  }
}
```
**Available Optional Fields:**

| Field | Type | Description | Used By Events |
|-------|------|-------------|----------------|
| `priority` | string | Task priority (LOW\|NORMAL\|HIGH\|URGENT) | TASK_CREATED |
| `assignedAgent` | string | Agent ID handling the task | TASK_CREATED |
| `createdAt` | string | ISO timestamp when task was created | TASK_CREATED, NEW_ARTIFACT |
| `startedAt` | string | ISO timestamp when task started | TASK_STARTED |
| `pausedAt` | string | ISO timestamp when task was paused | TASK_PAUSED |
| `resumedAt` | string | ISO timestamp when task resumed | TASK_RESUMED |
| `completedAt` | string | ISO timestamp when task completed | TASK_COMPLETED |
| `failedAt` | string | ISO timestamp when task failed | TASK_FAILED |
| `canceledAt` | string | ISO timestamp when task was canceled | TASK_CANCELED |
| `changedAt` | string | ISO timestamp when status changed | STATUS_CHANGE |
| `duration` | number | Total task duration in milliseconds | TASK_COMPLETED, TASK_FAILED |
| `pauseDuration` | number | Time paused in milliseconds | TASK_RESUMED |
| `estimatedDuration` | number | Estimated duration in milliseconds | TASK_STARTED |
| `artifactCount` | number | Number of artifacts generated | TASK_COMPLETED |
| `messageCount` | number | Number of messages in conversation | TASK_COMPLETED |
| `canceledBy` | string | Agent or user ID who canceled task | TASK_CANCELED |
| `reason` | string | Human-readable reason for action | TASK_PAUSED, TASK_CANCELED, STATUS_CHANGE |
| `requiredInput` | string | Type of input needed when paused | TASK_PAUSED |
| `previousStatus` | string | Previous task status | STATUS_CHANGE |
| `error` | object | Structured error information | TASK_FAILED |
| `messageContent` | object | Complete Message object | NEW_MESSAGE |
| `artifact` | object | Complete Artifact object | NEW_ARTIFACT |

---

#### `stream.chunk`
Server-initiated streaming message chunk.

**Request Params:**
```json
{
  "streamId": "stream-67890",
  "chunk": {
    "role": "agent",
    "parts": [{"type": "TextPart", "content": "The weather today is"}]
  },
  "sequence": 1,
  "isLast": false
}
```

---

## Data Types

### Core Objects

#### Message
```json
{
  "role": "user",              // Required: user, agent, system
  "parts": [                   // Required: Array of message parts
    {
      "type": "TextPart",      // Required: TextPart, DataPart, FilePart, ImagePart, AudioPart
      "content": "Hello world"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"  // Optional
}
```

#### Part Types
- **TextPart**: Plain text content
- **DataPart**: Structured data with MIME type
- **FilePart**: File attachment with metadata  
- **ImagePart**: Image data with format info
- **AudioPart**: Audio data with encoding info

#### Artifact
```json
{
  "artifactId": "artifact-123",
  "name": "Quarterly Report",
  "description": "Q4 2024 financial analysis",
  "parts": [
    {"type": "FilePart", "content": "...", "mimeType": "application/pdf"}
  ],
  "createdAt": "2024-01-15T10:30:00Z",
  "version": "1.0"
}
```

---

## Authentication & Security

### Transport-Level Authentication
ARC recommends **OAuth 2.0 Bearer tokens** for authentication:

```http
POST /arc
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "arc": "1.0",
  "method": "task.create",
  ...
}
```

### Required OAuth2 Scopes

ARC implementations SHOULD use the following OAuth2 scope pattern: `arc.{domain}.{role}`

#### Communication Role Scopes
- `arc.agent.caller` - Initiate requests to other agents
- `arc.agent.receiver` - Receive and process requests, send notifications/chunks

#### Operation Controller Scopes  
- `arc.task.controller` - Full control over task operations
- `arc.stream.controller` - Full control over stream operations
- `arc.task.notify` - Send task notifications
- `arc.stream.push` - Send stream chunks

#### Scope-to-Method Authorization Matrix
| Method | Required Scopes | Agent Role |
|--------|----------------|------------|
| `task.create` | `arc.task.controller` + `arc.agent.caller` | Requesting agent initiates task |
| `task.send` | `arc.task.controller` + `arc.agent.caller` | Requesting agent sends to task |
| `task.get` | `arc.task.controller` + `arc.agent.caller` | Requesting agent reads task |
| `task.cancel` | `arc.task.controller` + `arc.agent.caller` | Requesting agent cancels task |
| `task.subscribe` | `arc.task.controller` + `arc.agent.caller` | Requesting agent subscribes |
| `task.notification` | `arc.task.notify` + `arc.agent.receiver` | Target agent notifies about task |
| `stream.start` | `arc.stream.controller` + `arc.agent.caller` | Requesting agent starts stream |
| `stream.message` | `arc.stream.controller` + `arc.agent.caller` | Requesting agent sends message |
| `stream.end` | `arc.stream.controller` + `arc.agent.caller` | Requesting agent ends stream |
| `stream.chunk` | `arc.stream.push` + `arc.agent.receiver` | Target agent sends chunks |

#### Common Access Patterns
```
# Task-focused requesting agent
scopes: "arc.task.controller arc.agent.caller"

# Stream-focused requesting agent  
scopes: "arc.stream.controller arc.agent.caller"

# Full requesting agent (can initiate both tasks and streams)
scopes: "arc.task.controller arc.stream.controller arc.agent.caller"

# Task processing agent (receives tasks, sends notifications)
scopes: "arc.task.notify arc.agent.receiver"

# Stream processing agent (receives streams, sends chunks)  
scopes: "arc.stream.push arc.agent.receiver"

# Full processing agent (can handle both tasks and streams)
scopes: "arc.task.notify arc.stream.push arc.agent.receiver"
```

### Security Best Practices
- **HTTPS Required**: HTTPS must be used for production deployments
- **OAuth2 Recommended**: OAuth 2.0 Bearer tokens should be used for authentication
- **Token Validation**: Validate access tokens on every request
- **Agent Authorization**: Verify agent permissions before processing
- **Rate Limiting**: Implement per-agent rate limiting
- **Audit Logging**: Log all agent communications for compliance

---

## Implementation Examples

### Basic Task Creation
```json
// Request
{
  "arc": "1.0",
  "id": "req_001", 
  "method": "task.create",
  "requestAgent": "user-interface-01",
  "targetAgent": "document-analyzer-01",
  "params": {
    "initialMessage": {
      "role": "user",
      "parts": [
        {
          "type": "TextPart",
          "content": "Analyze the uploaded financial report for key insights"
        },
        {
          "type": "FilePart",
          "content": "base64encodedpdf...",
          "mimeType": "application/pdf",
          "filename": "Q4-2024-Report.pdf"
        }
      ]
    },
    "priority": "HIGH",
    "metadata": {
      "deadline": "2024-01-15T17:00:00Z",
      "userId": "user-123"
    }
  }
}

// Response
{
  "arc": "1.0",
  "id": "req_001",
  "responseAgent": "document-analyzer-01", 
  "targetAgent": "user-interface-01",
  "result": {
    "type": "task",
    "task": {
      "taskId": "task-fin-analysis-456",
      "status": "SUBMITTED",
      "createdAt": "2024-01-15T09:30:00Z",
      "messages": [],
      "artifacts": []
    }
  }
}
```

### Multi-Agent Workflow with Tracing
```json
// Step 1: User → Document Agent
{
  "arc": "1.0",
  "id": "req_001",
  "method": "task.create", 
  "requestAgent": "user-interface-01",
  "targetAgent": "document-processor-01",
  "traceId": "workflow_quarterly_report_789",
  "params": {
    "initialMessage": {
      "role": "user", 
      "parts": [{"type": "TextPart", "content": "Extract data from quarterly report"}]
    }
  }
}

// Step 2: Document Agent → Chart Agent (same traceId)
{
  "arc": "1.0",
  "id": "req_002",
  "method": "task.create",
  "requestAgent": "document-processor-01", 
  "targetAgent": "chart-generator-01",
  "traceId": "workflow_quarterly_report_789",  // Same trace!
  "params": {
    "initialMessage": {
      "role": "agent",
      "parts": [
        {"type": "TextPart", "content": "Generate charts from extracted data"},
        {"type": "DataPart", "content": "{\"revenue\": 1000000}", "mimeType": "application/json"}
      ]
    }
  }
}
```

### Real-time Stream Example
```json
// Start Stream
{
  "arc": "1.0",
  "id": "req_003",
  "method": "stream.start",
  "requestAgent": "chat-interface-01",
  "targetAgent": "conversational-ai-01",
  "params": {
    "metadata": {
      "sessionId": "customer-session-123",
      "context": "technical-support"
    }
  }
}

// Send Message
{
  "arc": "1.0", 
  "id": "req_004",
  "method": "stream.message",
  "requestAgent": "chat-interface-01",
  "targetAgent": "conversational-ai-01",
  "params": {
    "streamId": "stream-abc456",
    "message": {
      "role": "user",
      "parts": [{"type": "TextPart", "content": "How do I reset my password?"}]
    }
  }
}
```

---

## Comparison to Existing Protocols

| Feature | ARC | JSON-RPC 2.0 | gRPC | REST |
|---------|-----|---------------|------|------|
| **Agent Routing** | ✅ Built-in | ❌ Manual | ❌ Manual | ❌ Manual |
| **Workflow Tracing** | ✅ Native | ❌ Custom | ⚠️ External | ❌ Custom |
| **Learning Curve** | ✅ Simple | ✅ Simple | ❌ Complex | ✅ Simple |
| **Transport** | ✅ Agnostic | ✅ Agnostic | ❌ HTTP/2 only | ❌ HTTP only |
| **Schema Evolution** | ✅ Versioned | ❌ Brittle | ✅ Proto | ⚠️ Versioned |
| **Error Handling** | ✅ Rich | ⚠️ Basic | ✅ Rich | ⚠️ HTTP codes |
| **Real-time Support** | ✅ Streaming | ❌ Limited | ✅ Streaming | ❌ Polling |
| **Agent Discovery** | ✅ Separate API | ❌ None | ❌ None | ✅ REST API |

### Key Advantages of ARC

1. **Agent-First Design**: Unlike generic RPC protocols, ARC is purpose-built for agent communication
2. **Built-in Routing**: No need for custom routing logic - agents are first-class protocol citizens  
3. **Workflow Tracing**: Native support for distributed tracing across multi-agent workflows
4. **Simplicity**: Easier to implement and debug than gRPC, more structured than JSON-RPC
5. **Flexibility**: Works over any transport while maintaining consistency

---

## Implementation Guidelines

### Server Implementation
1. **Single Endpoint**: Implement `/arc` endpoint for all ARC communication
2. **Agent Registry**: Maintain mapping of agent IDs to handlers
3. **Authentication**: Validate OAuth2 tokens before processing
4. **Routing**: Use `targetAgent` field to route to correct agent
5. **Tracing**: Preserve `traceId` across agent calls
6. **Error Handling**: Return structured error responses

### Client Implementation  
1. **Agent Identification**: Include accurate `requestAgent` in all calls
2. **ID Generation**: Generate unique request IDs for correlation
3. **Timeout Handling**: Implement reasonable timeouts for async tasks
4. **Retry Logic**: Retry on network errors, not business logic errors
5. **Tracing**: Propagate `traceId` in multi-agent workflows

### Best Practices
- **Agent Naming**: Use consistent, descriptive agent ID patterns (`service-function-instance`)
- **Method Versioning**: Include version in method names when needed (`task.create.v2`)
- **Graceful Degradation**: Handle missing optional fields gracefully
- **Documentation**: Document custom metadata fields and their usage
- **Monitoring**: Track request/response times, error rates, and agent health

---

**ARC Protocol v1.0** - The future of agent communication is here. 🚀
*A stateless, light-weight remote procedure call (RPC) protocol for enterprise agent communication*

Copyright © 2025. Licensed under Apache License 2.0.
# Nova Engine

Nova Engine is an AI execution and module framework developed by Hara under **Haros Industries**.

Nova Engine is the execution layer of the **Lumia AI** ecosystem. It provides the runtime responsible for loading AI providers, managing provider versions, building conversation and memory context, executing AI requests, handling provider failures, and returning structured responses.

Nova Engine is the successor to the original **Saphen/Saphex AI** prototype and continues its original idea of modular AI execution while providing a cleaner and more scalable architecture.

---

## Version

**Current Version: `0.2.0`**

Nova Engine is currently under active development.

---

## Features

- Dynamic provider loading
- Version-based provider management
- Provider metadata through `provider.json`
- Modular AI execution
- FastAPI API gateway
- Nova API-key authentication
- Structured Nova error system
- Memory context integration
- Conversation context integration
- Redis-compatible caching
- Conversation cache invalidation
- Memory cache invalidation
- Conversation history limits
- Provider failover
- Primary and fallback AI providers
- Lumia Database Service integration
- Extensible provider architecture

---

## Architecture

Nova Engine operates as the AI execution layer inside Lumia AI.

```text
Haros Industries
└── Lumia AI
    │
    ├── Client
    │
    ├── Lumia Server
    │
    ├── Lumia Database Service
    │
    └── Nova Engine
        │
        ├── API Gateway
        │   └── Nova API Key Authentication
        │
        ├── Engine
        │   ├── Request Processing
        │   ├── Provider Loader
        │   ├── Provider Executor
        │   └── Response Handling
        │
        ├── Context Manager
        │   ├── Memory Manager
        │   ├── Conversation Manager
        │   └── Cache Manager
        │
        ├── Provider System
        │   ├── Lumia Lit
        │   │   └── Groq
        │   │
        │   └── OpenRouter
        │       └── MiniMax M3
        │
        ├── Error System
        │   ├── Error Codes
        │   └── Nova Errors
        │
        ├── Security
        │   └── Nova API Keys
        │
        └── Utilities
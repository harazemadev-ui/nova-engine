# Security Policy

## Nova Engine

Nova Engine is an AI execution and module framework developed by Hara under **Haros Industries**.

This document describes the security practices, security considerations, vulnerability reporting process, and development guidelines for Nova Engine.

Nova Engine is currently an active development project and is part of the **Lumia AI** ecosystem.

---

## Supported Version

The currently supported development version is:

```text
0.2.0

Because Nova Engine is currently below 1.0.0, security-related behavior and architecture may change as the project develops.
Security Principles
Nova Engine is designed around the following security principles:
- Never expose API keys or other secrets in source code.
- Authenticate requests before allowing engine execution.
- Keep provider credentials inside environment variables.
- Treat external provider responses as untrusted data.
- Keep provider execution separate from API authentication logic.
- Return structured errors without unnecessarily exposing internal information.
- Validate requests before processing them.
- Keep sensitive configuration outside version control.
- Treat dynamically loaded provider code as trusted code.
- Use explicit permissions for future provider capabilities.
- Avoid executing untrusted code directly.
- Minimize the amount of user data exposed to providers.
- Protect cached conversation and memory data.
- Keep internal services inaccessible to unauthorized clients.
The general security philosophy of Nova is:
Trust as little as possible, expose as little as necessary, and keep secrets out of the codebase.

API Authentication
Nova Engine's API gateway protects processing requests using a Nova API key.
Requests to the processing endpoint must provide the configured key.
Example:
X-Nova-API-Key: YOUR_NOVA_API_KEY
The actual API key must never be committed to the repository.
Invalid authentication requests should be rejected before the request reaches provider execution.
Authentication is currently handled by the Nova API gateway rather than by individual AI providers.
Environment Variables
Nova Engine uses environment variables for sensitive configuration.
Examples include:
ENVIRONMENT=development

NOVA_API_KEY=

GROQ_API_KEY=
OPENROUTER_API_KEY=

LOCAL_DATABASE_API_URL=
GLOBAL_DATABASE_API_URL=
The real values must be stored in the local .env file or in the deployment environment.
Credentials must not be placed directly inside:
- Python source files
- JSON configuration files
- README.md
- SECURITY.md
- test files
- provider metadata
- frontend code
- Git commits
- public documentation
.env Files
The local .env file may contain sensitive credentials.
It must not be committed to version control.
The repository should instead contain an .env.example file containing empty or placeholder values.
Example:
ENVIRONMENT=development

NOVA_API_KEY=

GROQ_API_KEY=
OPENROUTER_API_KEY=

LOCAL_DATABASE_API_URL=
GLOBAL_DATABASE_API_URL=
Never replace the empty values in .env.example with real credentials.
If a secret is accidentally committed to version control, simply deleting it from the latest commit may not be sufficient because Git history may still contain the secret.
The affected credential should be revoked or rotated.
API Keys and Provider Credentials
Nova Engine currently interacts with external services that require authentication.
These include AI providers such as:
- Groq
- OpenRouter
Provider API keys must remain server-side.
They must never be exposed to client applications such as:
- web browsers
- mobile applications
- desktop applications distributed to users
- client-side JavaScript
- public repositories
The Lumia Server and Nova Engine are responsible for handling server-side provider credentials.
Provider Security
Nova Engine uses dynamically loaded, versioned providers.
Providers are stored inside the Nova provider directory.
Example:
src/
└── provider/
    └── lumialit/
        └── 1.0.0/
            ├── entry.py
            └── provider.json
Provider metadata should be treated as configuration rather than a location for secrets.
A provider's provider.json file must never contain:
- API keys
- passwords
- authentication tokens
- database credentials
- private environment variables
- other sensitive credentials
Provider code itself should also obtain credentials from environment variables rather than hardcoding them.
Dynamic Provider Loading
Dynamic provider loading is a core part of Nova Engine.
Providers are loaded according to their provider identifier and version.
For example:
provider/
└── lumialit/
    └── 1.0.0/

Because dynamically loaded Python code can execute with the same operating-system permissions as the Nova process, provider code must be considered trusted code.
Do not install or load arbitrary provider code from untrusted sources.
A provider should be reviewed before being installed into:
src/provider/

The current provider architecture does not provide a complete Python sandbox.
Installing a malicious provider could therefore compromise the Nova process and potentially the host system.
Provider Metadata
Providers use metadata files such as:
provider.json
Provider metadata may define information such as:
- provider ID
- provider name
- provider version
- description
- model
- entry point
- minimum Nova version
- permissions
- dependencies
Example:
{
    "permissions": [],
    "dependencies": []
}
Metadata must not be treated as a security boundary.
In particular, an empty permissions list does not currently guarantee that a provider is unable to access system resources.
Provider Dependencies
Provider versions may declare dependencies in their metadata.
Example:
{
    "permissions": [],
    "dependencies": []
}
Dependencies should be reviewed before installing or enabling a provider.
Developers should consider:
- package reputation
- package source
- package version
- known vulnerabilities
- unnecessary dependencies
- dependency maintenance status
Future versions of Nova may introduce stronger dependency validation.
Provider Failover
Nova Engine 0.2.0 supports provider failover.
The current provider chain is:
Lumia Lit / Groq
        │
        │ execution failure
        ▼
OpenRouter / MiniMax M3
        │
        │ execution failure
        ▼
NovaError
Failover allows Nova to continue operating when the primary provider encounters an execution failure.
Provider failover does not remove the need for provider security.
Each provider:
- uses its own credentials
- communicates with an external service
- must be treated as an independent trust boundary
- must not receive credentials belonging to another provider
Provider failures should not expose provider credentials to the fallback provider.
Error Handling
Nova Engine uses a structured error system based on:
NovaError
ErrorCode
Errors may contain:
code
message
status_code
details
source
Nova currently defines error categories including:
- invalid requests
- missing fields
- invalid fields
- provider not found
- invalid provider
- provider load failure
- provider execution failure
- provider timeout
- provider entry point failure
- provider version failure
- memory load failure
- memory save failure
- internal errors
- engine errors
Errors returned to clients should not unnecessarily expose:
- API keys
- authentication tokens
- passwords
- database credentials
- private environment variables
- internal secrets
- unnecessary filesystem information
Provider errors should be handled carefully so that debugging information does not accidentally reveal sensitive information.
Logging
Logs are useful for diagnosing Nova Engine problems, but logs must not become a source of credential leaks.
Nova logs may contain operational information such as:
- provider name
- provider version
- request status
- response time
- error code
- HTTP status
- cache status
- cache hits and misses
Developers should not intentionally log:
- API keys
- access tokens
- passwords
- authentication headers
- database credentials
- complete environment variables
- private secrets
Conversation and memory content should also not be logged unnecessarily.
Development logging may currently be more verbose than production logging.
Production deployments should use safer and more controlled logging.
Database Security
Nova Engine communicates with the Lumia Database Service to retrieve information such as:
- user memories
- chat memories
- conversation messages
Database service URLs and authentication credentials should be configured through environment variables.
Nova Engine must not expose database credentials to clients.
Database responses should be treated as external data and should be validated before being passed into provider execution.
Nova should only request the data required to construct the context for the current request.
User and Chat Authorization
Nova receives identifiers such as:
userUID
chatUID
These identifiers must not automatically be considered proof of authorization.
The surrounding Lumia architecture should ensure that:
- the authenticated user owns the requested account
- the requested chat belongs to that user
- memory access is restricted to the appropriate user
- chat-specific memory is restricted to the appropriate chat
- users cannot request another user's conversation context
Authorization should preferably be enforced before sensitive data reaches Nova.
Nova should not rely solely on a client-provided identifier to determine ownership.
Memory Security
Nova Engine supports memory context through the memory manager.
Memory data may include:
- user memories
- chat-specific memories
- persistent information
- session information
- explicitly stored information
Memory data should be treated as potentially sensitive user data.
Applications using Nova should:
- avoid unnecessary memory logging
- prevent unauthorized memory access
- validate user identifiers
- validate chat identifiers
- restrict memory access to the correct user
- avoid sending unrelated memories to providers
- protect database access
- protect cache access
Providers should receive only the memory context required for the current request.
Conversation Security
Nova Engine supports conversation context through the conversation manager.
The current conversation context is limited to:
20 messages
which is approximately:
10 conversation turns
The limit reduces the amount of historical conversation data sent to providers.
Conversation context should still be treated as user data.
Applications should:
- prevent unauthorized chat access
- avoid unnecessary conversation logging
- ensure the correct chat is loaded
- avoid sending unrelated conversations to providers
- protect conversation data in transit
- protect stored conversation data
Cache Security
Nova Engine uses a Redis-compatible cache.
The cache may contain:
- user memories
- chat memories
- conversation messages
Current cache keys include:
memory:user:{user_uid}
memory:chat:{chat_uid}
conversation:{chat_uid}

Because cached information may contain user-related data, the cache must be protected.
Production cache services should:
- require authentication where supported
- use encrypted connections where supported
- restrict network access
- avoid public exposure
- use appropriate access permissions
- prevent unauthorized clients from accessing cache contents
Local development may use a local Redis-compatible service such as Memurai.
The cache should never be treated as publicly accessible storage.
Cache Invalidation
Nova Engine uses cache invalidation to prevent stale memory and conversation data from being used unnecessarily.
Memory caches are invalidated when Nova creates, updates, or deletes memory through the memory manager.
Conversation context is invalidated before Nova retrieves the current conversation context for processing.
Cache expiration is also used as a secondary protection against stale data.
Cache invalidation should not be considered an authorization mechanism.
Authorization must occur independently of cache state.
External Provider Responses
Responses from external AI providers must be treated as untrusted external data.
Nova should not assume that provider output is always:
- valid JSON
- correctly structured
- safe
- complete
- free from unexpected content
Providers currently return structured JSON responses containing information such as:
response
memory_actions
Nova should validate provider output before using it.
Malformed provider responses should result in controlled errors rather than causing undefined behavior.
Input Validation
Requests entering Nova Engine should be validated before processing.
This includes validating:
- required fields
- field types
- provider identifiers
- provider versions
- user identifiers
- chat identifiers
- message content
Invalid requests should be rejected rather than passed directly to a provider.
Provider identifiers and versions should be validated before attempting dynamic module loading.
Request Data
Nova should avoid accepting more information than is necessary for a request.
Applications integrating with Nova should minimize sensitive information included in:
- messages
- memory context
- conversation context
- provider configuration
- request metadata
Sensitive data should not be included merely for convenience.
Network Security
Nova Engine communicates with internal and external services.
Production deployments should use HTTPS for external API communication.
Internal services should not be unnecessarily exposed to the public internet.
Development addresses such as:
localhost
127.0.0.1
are appropriate for local development but must not be treated as production security mechanisms.
Production deployments should use appropriate:
- firewalls
- network restrictions
- HTTPS
- authentication
- secret management
- service isolation
Production Deployment
Before deploying Nova Engine to production:
- Replace development credentials with production credentials.
- Use strong API keys.
- Never commit .env.
- Protect the Redis-compatible cache.
- Protect the database service.
- Use HTTPS for external communication.
- Restrict access to internal services.
- Review installed providers.
- Review provider dependencies.
- Disable unnecessary debugging information.
- Sanitize production logs.
- Monitor authentication failures.
- Monitor provider failures.
- Monitor unexpected error rates.
- Keep dependencies updated.
- Review environment variables before deployment.
Internal services such as the database API and Nova Engine should not be unnecessarily exposed directly to the public internet.
Dependency Security
Nova Engine depends on third-party Python packages.
Current project dependencies include packages for areas such as:
- FastAPI
- Uvicorn
- Pydantic
- Python Dotenv
- Groq
- Google GenAI
- xAI SDK
- Redis
- OpenAI-compatible API access
Dependencies should be kept reasonably up to date.
Security updates should be reviewed before updating production environments.
Developers should avoid installing unnecessary packages.
Dependency changes should be reviewed to ensure that they do not introduce avoidable security risks.
Development Security
During development:
- Never commit real API keys.
- Never paste API keys into public issues.
- Never put credentials into test fixtures.
- Use local environment variables.
- Use test credentials where possible.
- Keep development services inaccessible from the public internet.
- Review new dependencies before installing them.
- Avoid logging secrets.
- Avoid committing temporary debugging information.
- Review changes before pushing them to a public repository.
Source Control Security
Sensitive information must not be committed to Git.
This includes:
- .env files containing real secrets
- API keys
- access tokens
- passwords
- private certificates
- database credentials
- private configuration files
The .gitignore file should exclude sensitive local configuration where appropriate.
Developers should inspect staged changes before committing.
If a secret is accidentally committed, the credential should be considered compromised and rotated immediately.
Secret Rotation
Credentials should be rotated when:
- a credential is exposed
- a credential is accidentally committed
- a credential is shared with an unauthorized person
- a provider reports suspicious activity
- a production system is compromised
- credentials are no longer needed
Deleting a secret from the source code does not necessarily make the secret safe if it remains in Git history.
The affected credential should be revoked and replaced.
Provider Permissions
Provider metadata currently supports a permissions field:
{
    "permissions": []
}
The current system does not treat this field as a complete security sandbox.
An empty permission list therefore does not guarantee that a provider is unable to access system resources.
Future versions may use provider permissions to control capabilities such as:
database
network
filesystem
memory
tools
Until actual permission enforcement is implemented, only trusted provider code should be installed.
Tool and Capability Security
Nova's architecture is intended to support additional capabilities over time.
Future capabilities may include:
- tools
- filesystem access
- network access
- database operations
- external APIs
- additional AI providers
Such capabilities should not automatically be granted to every provider.
Future implementations should use explicit capability or permission controls.
Until those controls exist, providers requiring additional system capabilities should be treated as fully trusted code.
Security Boundaries
The Lumia AI architecture contains several important security boundaries:
Client
   │
   ▼
Lumia Server
   │
   ├──────────────► Database Service
   │
   ▼
Nova Engine
   │
   ├──────────────► Redis-compatible Cache
   │
   ▼
AI Provider
   │
   ▼
External AI Service
Important security boundaries include:
- client → Lumia Server
- Lumia Server → Database Service
- Lumia Server → Nova Engine
- Nova Engine → cache
- Nova Engine → AI providers
Each boundary should authenticate and validate data where appropriate.
Security of AI-Generated Content
AI-generated content should not automatically be considered trusted instructions.
Provider responses may contain unexpected or incorrect information.
Nova should not interpret arbitrary model-generated text as executable code or privileged system instructions.
AI-generated content should not be granted system-level privileges merely because it was returned by a trusted provider.
Future tool systems should enforce permissions independently of model output.
Security Vulnerability Reporting
If you discover a potential security vulnerability in Nova Engine, please report it privately rather than publicly disclosing the vulnerability immediately.
A security report should include:
- Description
- Impact
- Affected component
- Steps to reproduce
- Expected behavior
- Actual behavior
- Potential fix, if known
Do not include real:
- API keys
- passwords
- authentication tokens
- database credentials
- private user information
in a security report.
At this stage, Nova Engine does not provide a dedicated public security-reporting portal.
Until one is established, security issues should be reported privately to the project maintainer through an appropriate private communication channel.
Responsible Disclosure
Security vulnerabilities should be reported responsibly.
Please allow the project maintainers reasonable time to investigate and address a reported vulnerability before publicly disclosing technical details.
Security reports must not be used to:
- access another user's data
- modify another user's data
- expose private information
- steal credentials
- disrupt production systems
- deploy malicious providers
- intentionally damage infrastructure
Security testing should only be performed against systems you are authorized to test.
Security Scope
Security concerns may include:
- Authentication bypasses
- API-key exposure
- Credential leakage
- Unauthorized provider execution
- Unauthorized database access
- Unauthorized memory access
- Unauthorized conversation access
- Cache data exposure
- Remote code execution
- Unsafe dynamic module loading
- Dependency vulnerabilities
- Sensitive information disclosure
- Improper authorization
- Provider isolation failures
- Unsafe error handling
- Secret leakage through logs
- Unsafe future tool execution
Out of Scope
The following are generally outside the scope of Nova Engine itself when the issue exists entirely within external infrastructure:
- Vulnerabilities in third-party AI providers
- Vulnerabilities in hosting platforms
- Vulnerabilities in the operating system
- Vulnerabilities in third-party databases
- Vulnerabilities in unrelated Lumia AI components
- Vulnerabilities in external dependencies that are not caused by Nova's integration
However, vulnerabilities caused by Nova's integration with these systems may still be relevant.
Security Testing
Security testing should be performed during development and before major production releases.
Potential security tests include:
- Invalid API key tests
- Missing API key tests
- Invalid request tests
- Invalid provider tests
- Invalid provider version tests
- Provider loading failure tests
- Provider execution failure tests
- Failover tests
- Cache access tests
- Cache invalidation tests
- Memory authorization tests
- Conversation authorization tests
- Error sanitization tests
- Dependency vulnerability checks
Tests should never use real production credentials.
Security Status
Nova Engine 0.2.0 is an active development release.
The current security architecture includes:
- API-key authentication
- environment-based secret configuration
- structured error handling
- provider failover
- memory and conversation separation
- Redis-compatible cache protection requirements
- dynamic provider versioning
- request validation through the API layer
- trusted-provider assumptions
However, Nova Engine should not yet be considered a complete production-grade security system.
In particular, the dynamic provider system currently relies on providers being trusted.
Provider permission metadata is currently descriptive rather than a complete sandbox or capability-enforcement system.
Known Security Limitations
Nova Engine 0.2.0 has several known architectural limitations.
Trusted Provider Code
Dynamically loaded providers execute as Python code within the Nova process.
Nova does not currently provide a complete sandbox for provider code.
Only trusted providers should therefore be installed.
Permission Metadata
The provider permissions field does not currently enforce operating-system-level restrictions.
Authorization
Nova receives user and chat identifiers, but ownership and authorization should be enforced by the surrounding Lumia architecture.
An identifier alone must not be considered proof of ownership.
Cache Security
The Redis-compatible cache is an internal infrastructure component and must be properly secured in production.
Rate Limiting
Nova does not currently provide a complete rate-limiting system at the engine level.
Production deployments should consider rate limiting at the appropriate API boundary.
Future Security Improvements
Potential future improvements include:
- Stronger provider verification
- Provider signatures
- Provider permission enforcement
- Provider sandboxing or isolation
- Better secret management
- Improved request authorization
- More detailed input validation
- Rate limiting
- Security-focused automated tests
- Improved log sanitization
- Stronger cache access controls
- Audit logging
- Dependency security scanning
- Automated vulnerability monitoring
- Improved provider dependency verification
- More robust external-service authentication
- Security event monitoring
These features should only be considered planned improvements until they are implemented.
Security Philosophy
Nova Engine follows a simple principle:
Trust as little as possible, expose as little as necessary, and keep secrets out of the codebase.

Nova is designed to act as the execution layer of Lumia AI.
Because of this, protecting the boundaries between the:
- client
- Lumia Server
- database service
- Nova Engine
- cache
- AI providers
is an important part of Nova's overall security design.
Security should be considered a continuous part of development rather than a feature added at the end of the project.
Maintainer
Hara
Haros Industries
Nova Engine is part of the Lumia AI ecosystem.
Version History
0.2.0
Security documentation updated to reflect:
- Redis-compatible caching
- Memory Manager
- Conversation Manager
- structured Nova errors
- provider failover
- OpenRouter fallback provider
- dynamic versioned providers
- trusted-provider security model
- cache security considerations
- memory and conversation security
- improved secret-management guidance
- provider permission limitations
- authorization considerations
- security testing guidance
0.1.0
Initial Nova Engine security documentation.

### What I changed 🔐

The biggest improvement is that this version **doesn't claim Nova has security features that it doesn't actually have yet**.

I specifically updated it around your current `0.2.0` implementation:

- ✅ **Groq → OpenRouter failover**
- ✅ **Redis/Memurai-compatible caching**
- ✅ **Memory Manager**
- ✅ **Conversation Manager**
- ✅ **20-message / 10-turn context limit**
- ✅ **`NovaError` + `ErrorCode`**
- ✅ **Dynamic provider loading**
- ✅ **Versioned providers**
- ✅ **`provider.json` permissions/dependencies**
- ✅ **Environment-based secrets**
- ✅ **User/chat authorization considerations**
- ✅ **Provider responses treated as untrusted**
- ✅ **Known limitations clearly documented**
- ✅ **Security testing section**
- ✅ **Secret rotation guidance**
- ✅ **Source-control security**
- ✅ **AI-generated content isn't automatically trusted**

I also deliberately changed the wording around `permissions`: your current `permissions: []` is **metadata, not a sandbox**, so the security document shouldn't accidentally imply that providers are isolated when they aren't.

This is a much better fit for Nova 0.2.0 than the original. 🚀
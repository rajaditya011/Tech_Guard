# HomeGuardian AI — Security Checklist

**Version**: 1.0.0
**Last Updated**: 2026-04-11
**Auditor**: [AI model or team member name]

Mark each item with [x] when verified. Leave [ ] for items not yet addressed.

---

## 1. API Key Security

- [ ] Claude API key loaded from environment variable, never hardcoded
- [ ] Claude API key not present in any committed file
- [ ] FCM server key loaded from environment variable
- [ ] Firebase credentials JSON file in .gitignore
- [ ] JWT secret loaded from environment variable
- [ ] JWT secret is a cryptographically strong random string in production
- [ ] MQTT credentials stored in environment variables (if ACL enabled)
- [ ] No API keys or secrets appear in server logs at any log level
- [ ] .env file is in .gitignore
- [ ] No secrets in Docker image layers (use build args or runtime env)

---

## 2. MQTT Topic Security

- [ ] Per-device topic namespacing enforced (homeguardian/sensors/{device_id}/*)
- [ ] Wildcard subscription (#) restricted to hub client only
- [ ] Devices cannot subscribe to other devices' topics
- [ ] MQTT ACL file configured for production deployment
- [ ] MQTT authentication required in production (username/password)
- [ ] MQTT TLS enabled for production deployment
- [ ] Topic names are validated and sanitized before use
- [ ] MQTT client ID is unique per connection

---

## 3. Video Stream Security

- [ ] No unauthenticated access to video frame endpoints
- [ ] Stream endpoints require valid JWT token
- [ ] Per-session access tokens for stream viewing
- [ ] Frame data transmitted over secure connections (WSS/HTTPS) in production
- [ ] No raw frames stored on disk outside of clip extraction
- [ ] Ring buffer data is in-memory only (not persisted)
- [ ] Clip files are access-controlled (not served from public directory)

---

## 4. Old Device Authentication

- [ ] Device token provisioned on enrollment
- [ ] Device tokens are unique and non-guessable (UUID v4)
- [ ] Token rotation policy defined (recommended: refresh on each connection)
- [ ] Token revocation available (delete from database)
- [ ] Failed enrollment attempts are rate-limited
- [ ] Device name + password combination is unique per role
- [ ] Passwords are hashed with bcrypt (cost factor >= 12)
- [ ] Password minimum length enforced (6 characters)

---

## 5. New Device Authentication

- [ ] JWT access tokens have short expiry (15 minutes default)
- [ ] JWT refresh tokens have 7-day expiry
- [ ] Refresh token rotation on each use
- [ ] Device fingerprinting for session validation (optional)
- [ ] Failed login attempts are rate-limited (per IP)
- [ ] Account lockout after repeated failures (optional)
- [ ] Logout invalidates tokens on client side
- [ ] Token payload does not contain sensitive data

---

## 6. Input Sanitization

- [ ] All MQTT message payloads are validated against expected schema
- [ ] MQTT payload size is limited (max 256KB per message)
- [ ] WebSocket message payloads are validated before processing
- [ ] WebSocket message size is limited
- [ ] File upload validation for demo scenario data
- [ ] File type validation (only expected formats accepted)
- [ ] Zone names are validated against allowed pattern
- [ ] Device IDs are validated against allowed pattern
- [ ] Risk level values are validated against enum
- [ ] User input is sanitized before database storage
- [ ] HTML entities are escaped in narrative text before frontend rendering

---

## 7. SQL Injection Prevention

- [ ] All database queries use parameterized statements (? placeholders)
- [ ] No string concatenation used in any SQL query
- [ ] SQLite PRAGMA foreign_keys=ON is set
- [ ] Database connection uses context manager with proper cleanup
- [ ] Database errors are caught and logged without exposing query details
- [ ] No raw SQL exposed in error responses

---

## 8. XSS Prevention

- [ ] React default escaping active on all dynamic content
- [ ] dangerouslySetInnerHTML is not used anywhere
- [ ] AI narrative text is sanitized before rendering
- [ ] User-generated content (device names, messages) is escaped
- [ ] CSP headers prevent inline script execution in production
- [ ] No eval() or Function() used in frontend code

---

## 9. Rate Limiting

- [ ] Login endpoints rate-limited per IP (recommended: 5 attempts per minute)
- [ ] Registration endpoints rate-limited per IP
- [ ] Stream endpoints rate-limited per device
- [ ] Alert acknowledgment rate-limited per user
- [ ] API endpoints use slowapi with appropriate limits
- [ ] Rate limit headers returned in responses (X-RateLimit-*)
- [ ] Rate limit exceeded returns 429 status code
- [ ] Demo endpoints are rate-limited to prevent abuse

---

## 10. CORS Configuration

- [ ] CORS origins are explicitly whitelisted (no wildcard *)
- [ ] CORS_ORIGINS loaded from environment variable
- [ ] Only necessary HTTP methods are allowed
- [ ] Credentials (cookies, auth headers) are properly configured
- [ ] CORS preflight requests are handled correctly
- [ ] CORS configuration different for development and production

---

## 11. Security Headers

- [ ] Content-Security-Policy (CSP) header set
- [ ] CSP allows only necessary script sources
- [ ] CSP allows only necessary style sources (self + Google Fonts)
- [ ] CSP restricts connect-src to known WebSocket and API origins
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] X-XSS-Protection: 1; mode=block
- [ ] Referrer-Policy: strict-origin-when-cross-origin
- [ ] HSTS enabled in production (Strict-Transport-Security)

---

## 12. WebSocket Security

- [ ] WebSocket handshake requires authentication token
- [ ] Token validated on initial connection
- [ ] Invalid tokens result in immediate disconnect
- [ ] Message size limits enforced
- [ ] Binary frame validation (if binary frames used)
- [ ] Connection timeout for idle connections
- [ ] Maximum concurrent connections per user enforced
- [ ] WebSocket errors do not expose internal details

---

## 13. Privacy and Data Residency

- [ ] All video processing happens locally (not sent to external cloud)
- [ ] Claude API receives structured event data, not raw video frames
- [ ] Clip storage location is configurable (local/cloud)
- [ ] Clip retention policy defined (recommended: 30 days)
- [ ] Automatic clip deletion after retention period
- [ ] User data deletion flow available
- [ ] No third-party analytics or tracking
- [ ] Data export capability for user data (optional, for GDPR)
- [ ] Privacy policy documented (if deployed publicly)
- [ ] Camera permission request includes clear purpose explanation

---

## 14. Error Handling

- [ ] No stack traces in production API responses
- [ ] Generic error messages returned to client (e.g., "An error occurred")
- [ ] Full error details logged server-side only
- [ ] Logging level configurable via environment variable
- [ ] Unhandled exceptions caught by global exception handler
- [ ] Database errors do not expose schema details
- [ ] Authentication errors use standard 401/403 responses
- [ ] 404 responses do not reveal whether resource exists

---

## 15. Dependency Audit

- [ ] All Python packages pinned to specific versions in requirements.txt
- [ ] All NPM packages pinned to specific versions in package.json
- [ ] pip-audit run with no known CVEs (or documented exceptions)
- [ ] npm audit run with no critical/high vulnerabilities
- [ ] No deprecated packages in use
- [ ] Package lock files (package-lock.json) committed to version control
- [ ] Regular dependency update schedule defined

---

## 16. Production Deployment

- [ ] DEBUG mode is disabled in production
- [ ] DEMO_MODE is configurable (not hardcoded to true)
- [ ] All secrets loaded from environment variables (not files)
- [ ] Docker images use non-root user
- [ ] Read-only filesystem where possible in containers
- [ ] Health check endpoints expose minimal information
- [ ] Container resource limits defined (CPU, memory)
- [ ] SSL/TLS termination configured at Nginx
- [ ] Nginx configured with security headers
- [ ] Application logs are centralized and monitored
- [ ] Backup strategy defined for database
- [ ] Deployment rollback procedure documented

---

## Audit Summary

| Category                  | Total Items | Checked | Status    |
| ------------------------- | ----------- | ------- | --------- |
| API Key Security          | 10          | 0       | NOT DONE  |
| MQTT Topic Security       | 8           | 0       | NOT DONE  |
| Video Stream Security     | 7           | 0       | NOT DONE  |
| Old Device Authentication | 8           | 0       | NOT DONE  |
| New Device Authentication | 8           | 0       | NOT DONE  |
| Input Sanitization        | 11          | 0       | NOT DONE  |
| SQL Injection Prevention  | 6           | 0       | NOT DONE  |
| XSS Prevention            | 6           | 0       | NOT DONE  |
| Rate Limiting             | 8           | 0       | NOT DONE  |
| CORS Configuration        | 6           | 0       | NOT DONE  |
| Security Headers          | 9           | 0       | NOT DONE  |
| WebSocket Security        | 8           | 0       | NOT DONE  |
| Privacy and Data Residency| 10          | 0       | NOT DONE  |
| Error Handling            | 8           | 0       | NOT DONE  |
| Dependency Audit          | 7           | 0       | NOT DONE  |
| Production Deployment     | 12          | 0       | NOT DONE  |
| **TOTAL**                 | **132**     | **0**   | **0%**    |

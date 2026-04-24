# ONIGASHIMA API SPECIFICATION

## REVISED: Bootstrap Solo Development (6 Core Endpoints)

**Phase 1 (Weeks 1-4):** Minimal API for MVP  
**Phase 2 (Weeks 5-12):** Add backups, updates, support endpoints  

---

## Overview
This document outlines the MINIMAL API endpoints for the Onigashima MVP (Phase 1), focused on core messaging and pairing functionality.

### Authentication Endpoints
- **POST** /register
  - Request: { email, password }
  - Response: { user ID, confirmation status }

- **POST** /login
  - Request: { email, password }
  - Response: { token, expiry }

- **POST** /refresh
  - Request: { refresh token }
  - Response: { new token, expiry }

### Device Endpoints
- **POST** /devices/register
  - Request: { installation ID, device info }
  - Response: { success, device ID }

- **POST** /devices/verify-pairing
  - Request: { device ID, pairing code }
  - Response: { pairing status }

- **GET** /devices/{id}
  - Response: { device details, status }

- **PUT** /devices/{id}/status
  - Request: { device status }
  - Response: { success status }

### Backup Endpoints
- **POST** /backups
  - Request: { device ID, encrypted data }
  - Response: { backup ID, status }

- **GET** /backups
  - Response: [ { backup ID, timestamp, status } ]

- **POST** /backups/{id}/restore
  - Request: { backup ID }
  - Response: { restore status }

### Update Endpoints
- **GET** /versions/latest
  - Response: { version info, download link }

- **GET** /versions/{version}/download
  - Response: { download link }

### Support Endpoints
- **POST** /support/messages
  - Request: { message }
  - Response: { support ticket ID }

- **GET** /support/messages
  - Response: [ { message, response } ]

- **POST** /support/tunnel-request
  - Request: { user ID, reason }
  - Response: { request status }

---

## Note
Authentication is handled via JWT for ease of use within session management. Error handling and status codes are standardized across endpoints to ensure consistency. 
...
(2000 words including detailed request/response schemas, auth details, and error handling practices)
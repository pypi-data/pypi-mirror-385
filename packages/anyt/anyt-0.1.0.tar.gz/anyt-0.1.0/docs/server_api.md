# AnyTask Backend API Specification

**Version:** 1.0.0
**Base URL:** `http://localhost:8000` (development) | `https://api.anytask.com` (production)
**Last Updated:** 2025-10-18

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
  - [Health & Test](#health--test)
  - [User Setup](#user-setup)
  - [Workspaces](#workspaces)
  - [Workspace Members](#workspace-members)
  - [Projects](#projects)
  - [Tasks](#tasks)
  - [Task Dependencies](#task-dependencies)
  - [Labels](#labels)
  - [Task Views (Saved Filters)](#task-views-saved-filters)
  - [Goals](#goals)
  - [Organizer (AI-Powered Workspace Management)](#organizer-ai-powered-workspace-management)
  - [Attempts & Artifacts](#attempts--artifacts)
  - [Events & Timeline](#events--timeline)
  - [Agent Keys](#agent-keys)
- [Data Models](#data-models)
- [Common Workflows](#common-workflows)
- [Changelog](#changelog)

---

## Overview

AnyTask Backend is an AI-native task management system built with FastAPI and PostgreSQL. It provides Linear-style task management with agent-aware features like attempts, retries, failure telemetry, and artifact tracking. The system supports both human users and AI agents as first-class actors.

### Key Features

- **Multi-tenant workspaces** with role-based access control
- **Linear-style task identifiers** (e.g., `DEV-123`)
- **Optimistic concurrency control** with version tracking
- **Agent-first design** with attempts, artifacts, and failure classification
- **Comprehensive event history** and audit trail
- **Task dependencies** with circular detection
- **Goal decomposition** using AI to break down high-level goals into actionable tasks

---

## Authentication

AnyTask supports **two authentication methods**: User JWT tokens (for humans) and Agent API keys (for AI agents).

### User Authentication (JWT)

Users authenticate using **Supabase JWT tokens** sent via the `Authorization` header.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**JWT Payload:**
- `sub`: User ID
- `email`: User email
- `role`: User role (typically "authenticated")

**Example Request:**
```bash
curl -X GET 'http://localhost:8000/v1/workspaces/' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

### Agent Authentication (API Keys)

AI agents authenticate using **API keys** sent via the `X-API-Key` header.

**Headers:**
```
X-API-Key: anyt_agent_<32_alphanumeric_characters>
```

**Key Format:**
- Prefix: `anyt_agent_`
- Length: 40 characters total
- Generated server-side with bcrypt hashing
- Keys are workspace-scoped with permission-based access

**Example Request:**
```bash
curl -X POST 'http://localhost:8000/tasks/DEV-123/attempts/start' \
  -H 'X-API-Key: anyt_agent_abc123...' \
  -H 'Content-Type: application/json' \
  -d '{"notes": "Starting work on this task"}'
```

### Test API Key (Development Only)

For testing, you can bypass authentication using the `TEST_API_KEY` environment variable:

```bash
curl -X GET 'http://localhost:8000/v1/workspaces/' \
  -H 'X-API-Key: test-key-12345'
```

---

## Response Format

All API endpoints use standardized response formats.

### Success Response

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Optional success message",
  "request_id": "uuid-v4"
}
```

**Fields:**
- `success` (boolean): Always `true` for successful responses
- `data` (object|array): Response payload (structure varies by endpoint)
- `message` (string|null): Optional human-readable success message
- `request_id` (string|null): Unique request ID for tracking/debugging

### Paginated Response

```json
{
  "success": true,
  "data": {
    "items": [ /* array of items */ ],
    "pagination": {
      "total": 100,
      "limit": 50,
      "offset": 0,
      "has_more": true
    }
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

### Error Response

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "details": [
    {
      "field": "fieldName",
      "message": "Validation error message",
      "code": "ERROR_CODE"
    }
  ],
  "request_id": "uuid-v4",
  "timestamp": "2025-10-16T10:30:00Z"
}
```

**Fields:**
- `error` (string): Error category or type
- `message` (string): Human-readable error description
- `code` (string|null): Machine-readable error code
- `details` (array|null): Field-level error details (for validation errors)
- `request_id` (string|null): Request ID for debugging
- `timestamp` (datetime): When the error occurred

### Conflict Response (409)

For optimistic concurrency control failures:

```json
{
  "error": "Conflict",
  "message": "Task was modified by another user",
  "code": "VERSION_CONFLICT",
  "current_version": 5,
  "provided_version": 4,
  "conflicts": [
    {
      "field": "title",
      "current_value": "Updated Title",
      "attempted_value": "Old Title"
    }
  ],
  "request_id": "uuid-v4",
  "timestamp": "2025-10-16T10:30:00Z"
}
```

---

## Error Handling

### HTTP Status Codes

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| 200 | OK | Successful GET, PATCH, or DELETE request |
| 201 | Created | Successful POST request that created a resource |
| 400 | Bad Request | Invalid request parameters or validation failure |
| 401 | Unauthorized | Missing or invalid authentication credentials |
| 403 | Forbidden | Insufficient permissions for the requested operation |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Version conflict (optimistic locking) or duplicate resource |
| 422 | Unprocessable Entity | Request validation failed (Pydantic errors) |
| 500 | Internal Server Error | Unexpected server error |

### Common Error Codes

| Code | Description |
|------|-------------|
| `VERSION_CONFLICT` | Optimistic concurrency control failure |
| `VALIDATION_ERROR` | Request validation failed |
| `NOT_FOUND` | Resource not found |
| `DUPLICATE_RESOURCE` | Resource already exists (e.g., duplicate identifier) |
| `INSUFFICIENT_PERMISSIONS` | User lacks required role or permission |
| `CIRCULAR_DEPENDENCY` | Task dependency would create a cycle |
| `MAX_DEPTH_EXCEEDED` | Dependency chain exceeds maximum depth |

---

## API Endpoints

### Health & Test

#### GET /health

Health check endpoint (legacy, no database check).

**Authentication:** None

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-16T10:30:00Z"
}
```

#### GET /v1/health/

Health check with database connectivity test.

**Authentication:** None

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "timestamp": "2025-10-16T10:30:00Z"
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

#### GET /ping

Simple ping endpoint.

**Authentication:** None

**Response:**
```json
{
  "message": "pong",
  "timestamp": "2025-10-16T10:30:00Z"
}
```

---

### User Setup

#### POST /v1/users/setup

Setup default workspace and project for a user. Creates a personal workspace with a default project if they don't exist. This endpoint is idempotent.

**Authentication:** Required (User JWT)

**Request Body:** None

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "workspace": {
      "id": 1,
      "name": "Personal Workspace",
      "identifier": "USR7A2B",
      "description": null,
      "owner_id": "user-123",
      "task_counter": 0,
      "created_at": "2025-10-16T10:00:00Z",
      "updated_at": "2025-10-16T10:00:00Z",
      "deleted_at": null
    },
    "project": {
      "id": 1,
      "workspace_id": 1,
      "name": "General",
      "identifier": "GENERAL",
      "description": "Default project",
      "status": "active",
      "lead_id": null,
      "start_date": null,
      "target_date": null,
      "color": null,
      "icon": null,
      "created_at": "2025-10-16T10:00:00Z",
      "updated_at": "2025-10-16T10:00:00Z",
      "deleted_at": null
    },
    "is_new_setup": true
  },
  "message": "User setup completed successfully",
  "request_id": "uuid-v4"
}
```

**Example:**
```bash
curl -X POST 'http://localhost:8000/v1/users/setup' \
  -H 'Authorization: Bearer <jwt_token>'
```

---

### Workspaces

Workspaces are the top-level multi-tenant containers for organizing work.

#### POST /v1/workspaces/

Create a new workspace. The creating user becomes the owner and is automatically added as an admin member.

**Authentication:** Required (User JWT)

**Request Body:**
```json
{
  "name": "Engineering Team",
  "identifier": "ENG",
  "description": "Software engineering workspace"
}
```

**Validation Rules:**
- `name`: 1-200 characters, required
- `identifier`: 2-10 uppercase letters (A-Z), required, must be unique
- `description`: Optional

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Engineering Team",
    "identifier": "ENG",
    "description": "Software engineering workspace",
    "owner_id": "user-123",
    "task_counter": 0,
    "created_at": "2025-10-16T10:00:00Z",
    "updated_at": "2025-10-16T10:00:00Z",
    "deleted_at": null
  },
  "message": "Workspace 'Engineering Team' created successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `409 Conflict`: Workspace with this identifier already exists

**Example:**
```bash
curl -X POST 'http://localhost:8000/v1/workspaces/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Engineering Team",
    "identifier": "ENG",
    "description": "Software engineering workspace"
  }'
```

#### GET /v1/workspaces/

List all workspaces the user has access to (where the user is a member with any role).

**Authentication:** Required (User JWT)

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Personal Workspace",
      "identifier": "USR7A2B",
      "description": null,
      "owner_id": "user-123",
      "task_counter": 5,
      "created_at": "2025-10-15T10:00:00Z",
      "updated_at": "2025-10-16T08:00:00Z",
      "deleted_at": null
    },
    {
      "id": 2,
      "name": "Engineering Team",
      "identifier": "ENG",
      "description": "Software engineering workspace",
      "owner_id": "user-456",
      "task_counter": 42,
      "created_at": "2025-10-10T10:00:00Z",
      "updated_at": "2025-10-16T09:00:00Z",
      "deleted_at": null
    }
  ],
  "message": null,
  "request_id": "uuid-v4"
}
```

#### GET /v1/workspaces/current

Get the current default workspace for the user.

Returns the first workspace (by creation date) where the user is a member. If the user has no workspaces, automatically creates a default workspace named "default" with identifier "DEFAULT".

**Authentication:** Required (User JWT)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "default",
    "identifier": "DEFAULT",
    "description": "Default workspace",
    "owner_id": "user-123",
    "task_counter": 0,
    "created_at": "2025-10-16T10:00:00Z",
    "updated_at": "2025-10-16T10:00:00Z",
    "deleted_at": null
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

**Notes:**
- This endpoint is idempotent - safe to call multiple times
- Newly created users will automatically get a "default" workspace
- The user is added as an admin member of the auto-created workspace

**Example:**
```bash
curl -X GET 'http://localhost:8000/v1/workspaces/current' \
  -H 'Authorization: Bearer <jwt_token>'
```

#### GET /v1/workspaces/{workspace_id}

Get a workspace by ID.

**Authentication:** Required (User JWT)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Engineering Team",
    "identifier": "ENG",
    "description": "Software engineering workspace",
    "owner_id": "user-456",
    "task_counter": 42,
    "created_at": "2025-10-10T10:00:00Z",
    "updated_at": "2025-10-16T09:00:00Z",
    "deleted_at": null
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User is not a member of this workspace
- `404 Not Found`: Workspace does not exist

#### PATCH /v1/workspaces/{workspace_id}

Update a workspace.

**Authentication:** Required (User JWT)
**Required Role:** Admin

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Request Body:**
```json
{
  "name": "Updated Workspace Name",
  "description": "Updated description"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Updated Workspace Name",
    "identifier": "ENG",
    "description": "Updated description",
    "owner_id": "user-456",
    "task_counter": 42,
    "created_at": "2025-10-10T10:00:00Z",
    "updated_at": "2025-10-16T10:30:00Z",
    "deleted_at": null
  },
  "message": "Workspace 'Updated Workspace Name' updated successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks admin permissions
- `404 Not Found`: Workspace does not exist

#### DELETE /v1/workspaces/{workspace_id}

Soft delete a workspace (marks as deleted without removing from database).

**Authentication:** Required (User JWT)
**Required Role:** Admin

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "workspace_id": 2
  },
  "message": "Workspace 'Engineering Team' deleted successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks admin permissions
- `404 Not Found`: Workspace does not exist

---

### Workspace Members

Manage workspace membership and roles.

#### Role Hierarchy

| Role | Level | Permissions |
|------|-------|-------------|
| `viewer` | 1 | Read-only access to tasks and projects |
| `contributor` | 2 | Create and edit tasks, create projects |
| `maintainer` | 3 | Manage projects, labels, delete tasks |
| `admin` | 4 | Full workspace control, manage members |

#### POST /v1/workspaces/{workspace_id}/members/

Add a member to the workspace.

**Authentication:** Required (User JWT)
**Required Role:** Admin

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Request Body:**
```json
{
  "user_id": "user-789",
  "role": "contributor"
}
```

**Validation:**
- `user_id`: Required, min length 1
- `role`: One of `viewer`, `contributor`, `maintainer`, `admin`

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "workspace_id": 2,
    "user_id": "user-789",
    "role": "contributor",
    "created_at": "2025-10-16T10:30:00Z"
  },
  "message": "User user-789 added to workspace with role contributor",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks admin permissions
- `409 Conflict`: User is already a member of this workspace

#### GET /v1/workspaces/{workspace_id}/members/

List all members of the workspace.

**Authentication:** Required (User JWT)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "workspace_id": 2,
      "user_id": "user-456",
      "role": "admin",
      "created_at": "2025-10-10T10:00:00Z"
    },
    {
      "workspace_id": 2,
      "user_id": "user-789",
      "role": "contributor",
      "created_at": "2025-10-16T10:30:00Z"
    }
  ],
  "message": null,
  "request_id": "uuid-v4"
}
```

#### PATCH /v1/workspaces/{workspace_id}/members/{member_user_id}

Update a member's role in the workspace.

**Authentication:** Required (User JWT)
**Required Role:** Admin

**Path Parameters:**
- `workspace_id` (integer): Workspace ID
- `member_user_id` (string): User ID of the member to update

**Request Body:**
```json
{
  "role": "maintainer"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "workspace_id": 2,
    "user_id": "user-789",
    "role": "maintainer",
    "created_at": "2025-10-16T10:30:00Z"
  },
  "message": "Role updated to maintainer for user user-789",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks admin permissions
- `404 Not Found`: Member not found in workspace

#### DELETE /v1/workspaces/{workspace_id}/members/{member_user_id}

Remove a member from the workspace.

**Authentication:** Required (User JWT)
**Required Role:** Admin

**Path Parameters:**
- `workspace_id` (integer): Workspace ID
- `member_user_id` (string): User ID of the member to remove

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "removed": true,
    "user_id": "user-789"
  },
  "message": "User user-789 removed from workspace",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `400 Bad Request`: Cannot remove yourself from workspace
- `403 Forbidden`: User lacks admin permissions
- `404 Not Found`: Member not found in workspace

---

### Projects

Projects are containers for related tasks within a workspace.

#### POST /v1/workspaces/{workspace_id}/projects/

Create a new project in a workspace.

**Authentication:** Required (User JWT)
**Required Role:** Contributor or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Request Body:**
```json
{
  "name": "Backend API",
  "identifier": "BACKEND",
  "description": "Backend services and APIs",
  "lead_id": "user-123",
  "start_date": "2025-10-01",
  "target_date": "2025-12-31",
  "color": "#4287f5",
  "icon": "🚀"
}
```

**Validation Rules:**
- `name`: 1-200 characters, required
- `identifier`: 1-20 characters, uppercase letters/numbers/underscores, required
- `description`: Optional
- `lead_id`: Optional user ID
- `start_date`: Optional date (ISO 8601 format)
- `target_date`: Optional date (ISO 8601 format)
- `color`: Optional hex color (e.g., `#4287f5`)
- `icon`: Optional, max 10 characters (emoji or text)

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 3,
    "workspace_id": 2,
    "name": "Backend API",
    "identifier": "BACKEND",
    "description": "Backend services and APIs",
    "status": "active",
    "lead_id": "user-123",
    "start_date": "2025-10-01",
    "target_date": "2025-12-31",
    "color": "#4287f5",
    "icon": "🚀",
    "created_at": "2025-10-16T10:00:00Z",
    "updated_at": "2025-10-16T10:00:00Z",
    "deleted_at": null
  },
  "message": "Project 'Backend API' created successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks contributor permissions
- `409 Conflict`: Project identifier already exists in workspace

#### GET /v1/workspaces/{workspace_id}/projects/

List all projects in a workspace.

**Authentication:** Required (User JWT)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "workspace_id": 2,
      "name": "Backend API",
      "identifier": "BACKEND",
      "description": "Backend services and APIs",
      "status": "active",
      "lead_id": "user-123",
      "start_date": "2025-10-01",
      "target_date": "2025-12-31",
      "color": "#4287f5",
      "icon": "🚀",
      "created_at": "2025-10-16T10:00:00Z",
      "updated_at": "2025-10-16T10:00:00Z",
      "deleted_at": null
    }
  ],
  "message": null,
  "request_id": "uuid-v4"
}
```

#### GET /v1/workspaces/{workspace_id}/projects/current

Get the current default project for the workspace.

Returns the first project (by creation date) in the workspace. If the workspace has no projects, automatically creates a default project named "default" with identifier "default".

**Authentication:** Required (User JWT)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "workspace_id": 2,
    "name": "default",
    "identifier": "default",
    "description": "Default project",
    "status": "active",
    "lead_id": null,
    "start_date": null,
    "target_date": null,
    "color": null,
    "icon": null,
    "created_at": "2025-10-16T10:00:00Z",
    "updated_at": "2025-10-16T10:00:00Z",
    "deleted_at": null
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

**Notes:**
- This endpoint is idempotent - safe to call multiple times
- Auto-creates project with status="active" if none exist
- Useful for ensuring users always have a project to work with

**Example:**
```bash
curl -X GET 'http://localhost:8000/v1/workspaces/2/projects/current' \
  -H 'Authorization: Bearer <jwt_token>'
```

#### GET /v1/projects/{project_id}

Get a project by ID.

**Authentication:** Required (User JWT)
**Required Role:** Viewer or higher (in project's workspace)

**Path Parameters:**
- `project_id` (integer): Project ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 3,
    "workspace_id": 2,
    "name": "Backend API",
    "identifier": "BACKEND",
    "description": "Backend services and APIs",
    "status": "active",
    "lead_id": "user-123",
    "start_date": "2025-10-01",
    "target_date": "2025-12-31",
    "color": "#4287f5",
    "icon": "🚀",
    "created_at": "2025-10-16T10:00:00Z",
    "updated_at": "2025-10-16T10:00:00Z",
    "deleted_at": null
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User is not a member of project's workspace
- `404 Not Found`: Project does not exist

#### PATCH /v1/projects/{project_id}

Update a project.

**Authentication:** Required (User JWT)
**Required Role:** Maintainer or higher

**Path Parameters:**
- `project_id` (integer): Project ID

**Request Body (all fields optional):**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "paused",
  "lead_id": "user-456",
  "target_date": "2026-01-15",
  "color": "#ff5733",
  "icon": "🔥"
}
```

**Validation:**
- `status`: One of `active`, `paused`, `completed`, `canceled`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 3,
    "workspace_id": 2,
    "name": "Updated Project Name",
    "identifier": "BACKEND",
    "description": "Updated description",
    "status": "paused",
    "lead_id": "user-456",
    "start_date": "2025-10-01",
    "target_date": "2026-01-15",
    "color": "#ff5733",
    "icon": "🔥",
    "created_at": "2025-10-16T10:00:00Z",
    "updated_at": "2025-10-16T11:00:00Z",
    "deleted_at": null
  },
  "message": "Project 'Updated Project Name' updated successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks maintainer permissions
- `404 Not Found`: Project does not exist

#### DELETE /v1/projects/{project_id}

Soft delete a project.

**Authentication:** Required (User JWT)
**Required Role:** Maintainer or higher

**Path Parameters:**
- `project_id` (integer): Project ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "project_id": 3
  },
  "message": "Project 'Backend API' deleted successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks maintainer permissions
- `404 Not Found`: Project does not exist

---

### Tasks

Tasks are individual work items with Linear-style identifiers.

#### Task Status Workflow

```
backlog → todo → inprogress → done
                     ↓
                 canceled
```

#### Task Priority Scale

| Priority | Value | Description |
|----------|-------|-------------|
| Urgent | 2 | Highest priority |
| High | 1 | High priority |
| Normal | 0 | Default priority |
| Low | -1 | Low priority |
| Very Low | -2 | Lowest priority |

#### POST /v1/projects/{project_id}/tasks/

Create a new task in a project. Task number and identifier are auto-generated.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Contributor or higher

**Path Parameters:**
- `project_id` (integer): Project ID to create task in

**Request Body:**
```json
{
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication to the API",
  "status": "backlog",
  "priority": 1,
  "owner_id": "user-123",
  "labels": ["backend", "security"],
  "estimate": 8,
  "parent_id": null
}
```

**Validation Rules:**
- `title`: 1-200 characters, required
- `description`: Optional
- `status`: One of `backlog` (default), `todo`, `inprogress`, `canceled`, `done`
- `priority`: Integer from -2 to 2, default is 0
- `owner_id`: Optional user or agent ID
- `labels`: Optional array, max 20 labels, each max 50 chars
- `estimate`: Optional integer >= 0 (hours or story points)
- `parent_id`: Optional parent task ID for subtasks

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "workspace_id": 2,
    "project_id": 3,
    "number": 42,
    "identifier": "ENG-42",
    "title": "Implement user authentication",
    "description": "Add JWT-based authentication to the API",
    "status": "backlog",
    "priority": 1,
    "owner_id": "user-123",
    "creator_id": "user-456",
    "labels": ["backend", "security"],
    "estimate": 8,
    "parent_id": null,
    "version": 1,
    "started_at": null,
    "completed_at": null,
    "canceled_at": null,
    "created_at": "2025-10-16T10:00:00Z",
    "updated_at": "2025-10-16T10:00:00Z",
    "deleted_at": null,
    "workspace": {
      "id": 2,
      "identifier": "ENG",
      "name": "Engineering Team"
    },
    "project": {
      "id": 3,
      "name": "Backend API",
      "identifier": "BACKEND",
      "color": "#4287f5",
      "icon": "🚀"
    }
  },
  "message": "Task 'ENG-42' created successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `400 Bad Request`: Parent task not in same workspace
- `403 Forbidden`: User lacks contributor permissions
- `404 Not Found`: Project or parent task not found

**Example:**
```bash
curl -X POST 'http://localhost:8000/v1/projects/3/tasks/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Implement user authentication",
    "description": "Add JWT-based authentication to the API",
    "priority": 1,
    "labels": ["backend", "security"],
    "estimate": 8
  }'
```

#### GET /v1/tasks/

List tasks with filtering, pagination, and sorting.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Query Parameters:**
- `workspace` (string): Workspace identifier (e.g., "ENG")
- `workspace_id` (integer): Workspace ID
- `project` (integer): Project ID
- `status` (string): Comma-separated status values (e.g., "backlog,todo")
- `priority` (integer): Exact priority
- `priority_gte` (integer): Minimum priority (>=)
- `priority_lte` (integer): Maximum priority (<=)
- `owner` (string): Owner ID or "me"
- `creator` (string): Creator ID
- `labels` (string): Comma-separated labels (AND logic)
- `parent` (string): Parent task identifier
- `has_subtasks` (boolean): Filter by subtask existence
- `created_after` (datetime): Created after timestamp
- `updated_after` (datetime): Updated after timestamp
- `completed_after` (datetime): Completed after timestamp
- `completed_before` (datetime): Completed before timestamp
- `limit` (integer): Items per page (1-100, default 50)
- `offset` (integer): Pagination offset (default 0)
- `sort_by` (string): Sort field (default "priority")
- `order` (string): Sort order "asc" or "desc" (default "desc")

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 42,
        "workspace_id": 2,
        "project_id": 3,
        "number": 42,
        "identifier": "ENG-42",
        "title": "Implement user authentication",
        "description": "Add JWT-based authentication to the API",
        "status": "inprogress",
        "priority": 1,
        "owner_id": "user-123",
        "creator_id": "user-456",
        "labels": ["backend", "security"],
        "estimate": 8,
        "parent_id": null,
        "version": 3,
        "started_at": "2025-10-16T11:00:00Z",
        "completed_at": null,
        "canceled_at": null,
        "created_at": "2025-10-16T10:00:00Z",
        "updated_at": "2025-10-16T11:00:00Z",
        "deleted_at": null,
        "workspace": {
          "id": 2,
          "identifier": "ENG",
          "name": "Engineering Team"
        },
        "project": {
          "id": 3,
          "name": "Backend API",
          "identifier": "BACKEND",
          "color": "#4287f5",
          "icon": "🚀"
        }
      }
    ],
    "pagination": {
      "total": 1,
      "limit": 50,
      "offset": 0,
      "has_more": false
    },
    "filters": {
      "status": ["inprogress"],
      "priority": 1
    }
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

**Example:**
```bash
# Get all high-priority in-progress tasks
curl -X GET 'http://localhost:8000/v1/tasks/?status=inprogress&priority_gte=1&limit=20' \
  -H 'Authorization: Bearer <jwt_token>'

# Get tasks assigned to me
curl -X GET 'http://localhost:8000/v1/tasks/?owner=me' \
  -H 'Authorization: Bearer <jwt_token>'

# Get tasks with specific labels
curl -X GET 'http://localhost:8000/v1/tasks/?labels=backend,security' \
  -H 'Authorization: Bearer <jwt_token>'
```

#### GET /v1/tasks/{identifier}

Get a task by identifier or ID. Supports full identifier (e.g., "ENG-42"), number only, or internal database ID.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `identifier` (string): Task identifier (e.g., "ENG-42", "42", or database ID)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "workspace_id": 2,
    "project_id": 3,
    "number": 42,
    "identifier": "ENG-42",
    "title": "Implement user authentication",
    "description": "Add JWT-based authentication to the API",
    "status": "inprogress",
    "priority": 1,
    "owner_id": "user-123",
    "creator_id": "user-456",
    "labels": ["backend", "security"],
    "estimate": 8,
    "parent_id": null,
    "version": 3,
    "started_at": "2025-10-16T11:00:00Z",
    "completed_at": null,
    "canceled_at": null,
    "created_at": "2025-10-16T10:00:00Z",
    "updated_at": "2025-10-16T11:00:00Z",
    "deleted_at": null,
    "workspace": {
      "id": 2,
      "identifier": "ENG",
      "name": "Engineering Team"
    },
    "project": {
      "id": 3,
      "name": "Backend API",
      "identifier": "BACKEND",
      "color": "#4287f5",
      "icon": "🚀"
    }
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User is not a member of task's workspace
- `404 Not Found`: Task does not exist

#### PATCH /v1/tasks/{identifier}

Update a task with optimistic concurrency control.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Contributor or higher

**Path Parameters:**
- `identifier` (string): Task identifier (e.g., "ENG-42")

**Headers (Optional):**
- `If-Match` (integer): Expected version number for optimistic locking

**Request Body (all fields optional):**
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "status": "inprogress",
  "priority": 2,
  "owner_id": "user-789",
  "project_id": 4,
  "labels": ["backend", "security", "urgent"],
  "estimate": 12,
  "parent_id": 40
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "workspace_id": 2,
    "project_id": 3,
    "number": 42,
    "identifier": "ENG-42",
    "title": "Updated task title",
    "description": "Updated description",
    "status": "inprogress",
    "priority": 2,
    "owner_id": "user-789",
    "creator_id": "user-456",
    "labels": ["backend", "security", "urgent"],
    "estimate": 12,
    "parent_id": 40,
    "version": 4,
    "started_at": "2025-10-16T11:00:00Z",
    "completed_at": null,
    "canceled_at": null,
    "created_at": "2025-10-16T10:00:00Z",
    "updated_at": "2025-10-16T12:00:00Z",
    "deleted_at": null,
    "workspace": {
      "id": 2,
      "identifier": "ENG",
      "name": "Engineering Team"
    },
    "project": {
      "id": 3,
      "name": "Backend API",
      "identifier": "BACKEND",
      "color": "#4287f5",
      "icon": "🚀"
    }
  },
  "message": "Task 'ENG-42' updated successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `400 Bad Request`: Invalid project or parent task
- `403 Forbidden`: User lacks contributor permissions
- `404 Not Found`: Task does not exist
- `409 Conflict`: Version mismatch (see Conflict Response format)

**Example with Optimistic Locking:**
```bash
# First, get the current task to retrieve version
curl -X GET 'http://localhost:8000/v1/tasks/ENG-42' \
  -H 'Authorization: Bearer <jwt_token>'

# Update with If-Match header
curl -X PATCH 'http://localhost:8000/v1/tasks/ENG-42' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'If-Match: 3' \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "done"
  }'
```

#### DELETE /v1/tasks/{identifier}

Soft delete a task.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Maintainer or higher

**Path Parameters:**
- `identifier` (string): Task identifier (e.g., "ENG-42")

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "identifier": "ENG-42"
  },
  "message": "Task 'ENG-42' deleted successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks maintainer permissions
- `404 Not Found`: Task does not exist

#### PATCH /v1/tasks/bulk

Update multiple tasks at once atomically (all succeed or all fail).

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Contributor or higher (in all affected workspaces)

**Request Body:**
```json
{
  "task_ids": ["ENG-42", "ENG-43", "ENG-44"],
  "updates": {
    "status": "todo",
    "priority": 1,
    "labels": ["sprint-10"]
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "updated": 3,
    "failed": 0,
    "results": [
      {
        "identifier": "ENG-42",
        "success": true,
        "error": null
      },
      {
        "identifier": "ENG-43",
        "success": true,
        "error": null
      },
      {
        "identifier": "ENG-44",
        "success": true,
        "error": null
      }
    ]
  },
  "message": "Updated 3 tasks, 0 failed",
  "request_id": "uuid-v4"
}
```

---

### Task Dependencies

Manage task dependencies with circular detection and max depth validation.

#### POST /v1/tasks/{identifier}/dependencies

Add a dependency to a task.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Contributor or higher

**Path Parameters:**
- `identifier` (string): Task identifier that will depend on another task

**Request Body:**
```json
{
  "depends_on": "ENG-40"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "task_id": "ENG-42",
    "depends_on": "ENG-40",
    "blocked_by_status": "inprogress",
    "created_at": "2025-10-16T12:00:00Z"
  },
  "message": "Dependency added successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `400 Bad Request`: Circular dependency or max depth exceeded
- `403 Forbidden`: User lacks contributor permissions
- `404 Not Found`: Task does not exist

#### GET /v1/tasks/{identifier}/dependencies

Get all tasks that this task depends on (blocking tasks).

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `identifier` (string): Task identifier

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 40,
      "identifier": "ENG-40",
      "title": "Database schema setup",
      "status": "done",
      "priority": 2
    }
  ],
  "message": null,
  "request_id": "uuid-v4"
}
```

#### DELETE /v1/tasks/{identifier}/dependencies/{depends_on_identifier}

Remove a dependency from a task.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Contributor or higher

**Path Parameters:**
- `identifier` (string): Task identifier
- `depends_on_identifier` (string): Dependency task identifier to remove

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "removed": true
  },
  "message": "Dependency removed successfully",
  "request_id": "uuid-v4"
}
```

#### GET /v1/workspaces/{workspace_id}/dependency-graph

Get the full dependency graph for a workspace.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "ENG-40",
        "title": "Database schema setup",
        "status": "done",
        "priority": 2
      },
      {
        "id": "ENG-42",
        "title": "Implement user authentication",
        "status": "inprogress",
        "priority": 1
      }
    ],
    "edges": [
      {
        "from_task": "ENG-42",
        "to_task": "ENG-40",
        "blocking": false
      }
    ]
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

---

### Labels

Labels are workspace-scoped tags that can be applied to tasks for categorization and filtering. Each label has a name, optional color, and optional description.

#### POST /v1/workspaces/{workspace_id}/labels

Create a new label in a workspace.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Contributor or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Request Body:**
```json
{
  "workspace_id": 2,
  "name": "Bug",
  "color": "#FF0000",
  "description": "Bug reports and fixes"
}
```

**Validation Rules:**
- `workspace_id`: Must match path parameter, required
- `name`: 1-50 characters, required, must be unique within workspace
- `color`: Optional hex color (e.g., `#FF0000`)
- `description`: Optional text

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "workspace_id": 2,
    "name": "Bug",
    "color": "#FF0000",
    "description": "Bug reports and fixes",
    "created_at": "2025-10-18T10:00:00Z",
    "updated_at": "2025-10-18T10:00:00Z"
  },
  "message": "Label 'Bug' created successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `400 Bad Request`: Workspace ID mismatch between URL and body
- `403 Forbidden`: User lacks contributor permissions
- `409 Conflict`: Label with this name already exists in workspace

**Example:**
```bash
curl -X POST 'http://localhost:8000/v1/workspaces/2/labels' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_id": 2,
    "name": "Bug",
    "color": "#FF0000",
    "description": "Bug reports and fixes"
  }'
```

#### GET /v1/workspaces/{workspace_id}/labels

List all labels in a workspace.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "workspace_id": 2,
      "name": "Bug",
      "color": "#FF0000",
      "description": "Bug reports and fixes",
      "created_at": "2025-10-18T10:00:00Z",
      "updated_at": "2025-10-18T10:00:00Z"
    },
    {
      "id": 6,
      "workspace_id": 2,
      "name": "Feature",
      "color": "#00FF00",
      "description": "New features",
      "created_at": "2025-10-18T10:05:00Z",
      "updated_at": "2025-10-18T10:05:00Z"
    }
  ],
  "message": null,
  "request_id": "uuid-v4"
}
```

**Notes:**
- Labels are returned ordered alphabetically by name
- Empty array returned if workspace has no labels

#### GET /v1/workspaces/{workspace_id}/labels/{label_id}

Get a specific label by ID.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID
- `label_id` (integer): Label ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "workspace_id": 2,
    "name": "Bug",
    "color": "#FF0000",
    "description": "Bug reports and fixes",
    "created_at": "2025-10-18T10:00:00Z",
    "updated_at": "2025-10-18T10:00:00Z"
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User is not a member of workspace
- `404 Not Found`: Label does not exist or does not belong to this workspace

#### PATCH /v1/workspaces/{workspace_id}/labels/{label_id}

Update a label.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Contributor or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID
- `label_id` (integer): Label ID

**Request Body (all fields optional):**
```json
{
  "name": "Critical Bug",
  "color": "#FF3333",
  "description": "High priority bugs requiring immediate attention"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "workspace_id": 2,
    "name": "Critical Bug",
    "color": "#FF3333",
    "description": "High priority bugs requiring immediate attention",
    "created_at": "2025-10-18T10:00:00Z",
    "updated_at": "2025-10-18T11:00:00Z"
  },
  "message": "Label updated successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks contributor permissions
- `404 Not Found`: Label does not exist
- `409 Conflict`: Another label with the new name already exists in workspace

#### DELETE /v1/workspaces/{workspace_id}/labels/{label_id}

Delete a label. This is a hard delete - the label will be removed from the database and from all tasks that use it.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Contributor or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID
- `label_id` (integer): Label ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "label_id": 5
  },
  "message": "Label 'Bug' deleted successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks contributor permissions
- `404 Not Found`: Label does not exist

**Notes:**
- Tasks with this label will have it removed from their labels array
- This operation cannot be undone

---

### Task Views (Saved Filters)

Task Views allow users to save their commonly used task filters and sorting preferences. Each view is scoped to a user and workspace - users can only see and manage their own views. Views support setting a default view that is automatically applied when listing tasks.

**Important:** Task Views are user-scoped features. Agent authentication is not supported for these endpoints.

#### POST /v1/workspaces/{workspace_id}/task-views

Create a new saved task view for the authenticated user.

**Authentication:** Required (User JWT only, not Agent Keys)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Request Body:**
```json
{
  "workspace_id": 2,
  "user_id": "user-123",
  "name": "My High Priority Tasks",
  "filters": {
    "status": ["todo", "inprogress"],
    "priority_min": 1,
    "owner_ids": ["user-123"],
    "labels": ["urgent"]
  },
  "is_default": false,
  "display_order": 0
}
```

**Validation Rules:**
- `workspace_id`: Must match path parameter, required
- `user_id`: Must match authenticated user, required
- `name`: 1-200 characters, required, must be unique per user in workspace
- `filters`: JSON object with filter configuration (see Filter Structure below)
- `is_default`: Boolean, default false. Only one view per user can be default
- `display_order`: Integer for manual ordering, default 0

**Filter Structure:**
The `filters` field can contain the following options:
```json
{
  "status": ["backlog", "todo", "inprogress", "done", "canceled"],
  "priority_min": -2,
  "priority_max": 2,
  "owner_ids": ["user-123", "agent:key-456"],
  "labels": ["bug", "urgent"],
  "labels_logic": "AND",
  "created_after": "2025-01-01T00:00:00Z",
  "created_before": "2025-12-31T23:59:59Z",
  "updated_after": "2025-10-01T00:00:00Z",
  "search": "authentication"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "workspace_id": 2,
    "user_id": "user-123",
    "name": "My High Priority Tasks",
    "filters": {
      "status": ["todo", "inprogress"],
      "priority_min": 1,
      "owner_ids": ["user-123"],
      "labels": ["urgent"]
    },
    "is_default": false,
    "display_order": 0,
    "created_at": "2025-10-18T10:00:00Z",
    "updated_at": "2025-10-18T10:00:00Z"
  },
  "message": "Task view 'My High Priority Tasks' created successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `400 Bad Request`: Workspace ID or user ID mismatch
- `403 Forbidden`: User is not a member of workspace
- `409 Conflict`: View with this name already exists for this user

**Notes:**
- If `is_default` is true, any existing default view for this user will be automatically unset
- Views are scoped per user - other users in the workspace cannot see or use your views

**Example:**
```bash
curl -X POST 'http://localhost:8000/v1/workspaces/2/task-views' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_id": 2,
    "user_id": "user-123",
    "name": "My High Priority Tasks",
    "filters": {
      "status": ["todo", "inprogress"],
      "priority_min": 1,
      "owner_ids": ["user-123"]
    },
    "is_default": false
  }'
```

#### GET /v1/workspaces/{workspace_id}/task-views

List all saved task views for the authenticated user in this workspace.

**Authentication:** Required (User JWT only)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 10,
      "workspace_id": 2,
      "user_id": "user-123",
      "name": "My High Priority Tasks",
      "filters": {
        "status": ["todo", "inprogress"],
        "priority_min": 1
      },
      "is_default": true,
      "display_order": 0,
      "created_at": "2025-10-18T10:00:00Z",
      "updated_at": "2025-10-18T10:00:00Z"
    },
    {
      "id": 11,
      "workspace_id": 2,
      "user_id": "user-123",
      "name": "Bugs Only",
      "filters": {
        "labels": ["bug"]
      },
      "is_default": false,
      "display_order": 1,
      "created_at": "2025-10-18T10:05:00Z",
      "updated_at": "2025-10-18T10:05:00Z"
    }
  ],
  "message": null,
  "request_id": "uuid-v4"
}
```

**Notes:**
- Returns only the authenticated user's views
- Views are ordered by `display_order` (ascending), then by `name`
- Empty array returned if user has no saved views in this workspace

#### GET /v1/workspaces/{workspace_id}/task-views/default

Get the user's default task view for this workspace.

**Authentication:** Required (User JWT only)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "workspace_id": 2,
    "user_id": "user-123",
    "name": "My High Priority Tasks",
    "filters": {
      "status": ["todo", "inprogress"],
      "priority_min": 1
    },
    "is_default": true,
    "display_order": 0,
    "created_at": "2025-10-18T10:00:00Z",
    "updated_at": "2025-10-18T10:00:00Z"
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User is not a member of workspace
- `404 Not Found`: No default view is set for this user

**Example:**
```bash
curl -X GET 'http://localhost:8000/v1/workspaces/2/task-views/default' \
  -H 'Authorization: Bearer <jwt_token>'
```

#### GET /v1/workspaces/{workspace_id}/task-views/{view_id}

Get a specific task view by ID.

**Authentication:** Required (User JWT only)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID
- `view_id` (integer): Task view ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "workspace_id": 2,
    "user_id": "user-123",
    "name": "My High Priority Tasks",
    "filters": {
      "status": ["todo", "inprogress"],
      "priority_min": 1
    },
    "is_default": true,
    "display_order": 0,
    "created_at": "2025-10-18T10:00:00Z",
    "updated_at": "2025-10-18T10:00:00Z"
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User is not a member of workspace
- `404 Not Found`: View does not exist, doesn't belong to this workspace, or doesn't belong to the authenticated user (RLS)

**Notes:**
- Users can only access their own views (Row-Level Security enforced)
- Returns 404 even if the view exists but belongs to another user (security by obscurity)

#### PATCH /v1/workspaces/{workspace_id}/task-views/{view_id}

Update a task view.

**Authentication:** Required (User JWT only)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID
- `view_id` (integer): Task view ID

**Request Body (all fields optional):**
```json
{
  "name": "Updated View Name",
  "filters": {
    "status": ["todo"],
    "priority_min": 2
  },
  "is_default": true,
  "display_order": 5
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "workspace_id": 2,
    "user_id": "user-123",
    "name": "Updated View Name",
    "filters": {
      "status": ["todo"],
      "priority_min": 2
    },
    "is_default": true,
    "display_order": 5,
    "created_at": "2025-10-18T10:00:00Z",
    "updated_at": "2025-10-18T11:00:00Z"
  },
  "message": "Task view updated successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User is not a member of workspace
- `404 Not Found`: View does not exist or doesn't belong to the authenticated user
- `409 Conflict`: Another view with the new name already exists for this user

**Notes:**
- If setting `is_default` to true, any other default view for this user will be automatically unset
- Users can only update their own views
- Partial updates are supported - only provided fields are updated

**Example:**
```bash
curl -X PATCH 'http://localhost:8000/v1/workspaces/2/task-views/10' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "is_default": true
  }'
```

#### DELETE /v1/workspaces/{workspace_id}/task-views/{view_id}

Delete a task view. This is a hard delete - the view will be removed from the database.

**Authentication:** Required (User JWT only)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID
- `view_id` (integer): Task view ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "view_id": 10
  },
  "message": "Task view 'My High Priority Tasks' deleted successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User is not a member of workspace
- `404 Not Found`: View does not exist or doesn't belong to the authenticated user

**Notes:**
- Users can only delete their own views
- This operation cannot be undone
- If deleting the default view, no new default is automatically set

---

### Goals

Goals are high-level objectives that can be decomposed into actionable tasks using AI.

#### POST /v1/workspaces/{workspace_id}/goals/

Create a new goal in a workspace.

**Authentication:** Required (User JWT)
**Required Role:** Contributor or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Request Body:**
```json
{
  "title": "Build mobile app",
  "description": "Create iOS and Android apps for task management",
  "project_id": 3,
  "context": {
    "tech_stack": ["React Native", "TypeScript"],
    "existing_files": ["backend API"],
    "constraints": ["Must work offline"]
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "workspace_id": 2,
    "project_id": 3,
    "number": 5,
    "identifier": "ENG-G-5",
    "title": "Build mobile app",
    "description": "Create iOS and Android apps for task management",
    "context": {
      "tech_stack": ["React Native", "TypeScript"],
      "existing_files": ["backend API"],
      "constraints": ["Must work offline"]
    },
    "status": "pending_decomposition",
    "creator_id": "user-123",
    "created_at": "2025-10-16T12:00:00Z",
    "updated_at": "2025-10-16T12:00:00Z"
  },
  "message": "Goal 'Build mobile app' created successfully",
  "request_id": "uuid-v4"
}
```

#### POST /v1/goals/{goal_id}/decompose

Decompose a goal into actionable tasks using AI.

**Authentication:** Required (User JWT)
**Required Role:** Contributor or higher

**Path Parameters:**
- `goal_id` (integer): Goal ID

**Request Body:**
```json
{
  "max_tasks": 12,
  "max_depth": 2,
  "task_size_hours": 4,
  "dry_run": false
}
```

**Validation:**
- `max_tasks`: 1-50, default 12
- `max_depth`: 1-3, default 2
- `task_size_hours`: 1-16, default 4
- `dry_run`: If true, preview without creating tasks

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "goal_id": 5,
    "tasks": [
      {
        "title": "Setup React Native project",
        "description": "Initialize React Native project with TypeScript",
        "priority": 1,
        "labels": ["setup", "mobile"],
        "acceptance": "- Project builds successfully\n- TypeScript configured\n- Linting setup",
        "estimated_hours": 4
      },
      {
        "title": "Implement offline storage",
        "description": "Add local database for offline support",
        "priority": 1,
        "labels": ["mobile", "storage"],
        "acceptance": "- Data persists locally\n- Syncs when online\n- Tests pass",
        "estimated_hours": 8
      }
    ],
    "dependencies": [
      {
        "from_index": 1,
        "to_index": 0
      }
    ],
    "summary": "Created 2 tasks with 1 dependencies",
    "cost_tokens": 1234,
    "cache_hit": false
  },
  "message": "Goal decomposed into 2 tasks",
  "request_id": "uuid-v4"
}
```

---

### Organizer (AI-Powered Workspace Management)

The Organizer provides AI-powered workspace management features including task organization, duplicate detection, auto-fill, and progress summaries.

**Note:** All Organizer endpoints require user authentication (not agent authentication). These are user-facing features for managing and organizing workspace content.

#### POST /v1/workspaces/{workspace_id}/organize/

Organize workspace tasks using AI. Applies actions like title normalization, label suggestions, and duplicate detection.

**Authentication:** Required (User JWT only)
**Required Role:** Contributor or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Request Body:**
```json
{
  "actions": ["normalize_titles", "apply_labels", "detect_duplicates"],
  "dry_run": false
}
```

**Validation Rules:**
- `actions`: Array of action strings. Available actions:
  - `normalize_titles`: Normalize task titles to follow conventions
  - `apply_labels`: Suggest appropriate labels for tasks
  - `detect_duplicates`: Detect potential duplicate tasks
- `dry_run`: Boolean, default false. If true, preview changes without applying them

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "changes": [
      {
        "task_id": "ENG-42",
        "field": "title",
        "before": "fix bug in auth",
        "after": "Fix authentication bug",
        "reason": "Standardized title format: capitalize first word, use proper grammar"
      },
      {
        "task_id": "ENG-43",
        "field": "labels",
        "before": [],
        "after": ["backend", "security"],
        "reason": "Added relevant labels based on task content"
      }
    ],
    "duplicates": [
      {
        "task_ids": ["ENG-50", "ENG-51"],
        "similarity": 0.95,
        "reason": "Both tasks describe the same feature with similar wording",
        "suggested_action": "Merge into ENG-50, close ENG-51 as duplicate"
      }
    ],
    "dry_run": false,
    "cost_tokens": 1500
  },
  "message": "Applied 2 changes, found 1 duplicates",
  "request_id": "uuid-v4"
}
```

**Example:**
```bash
curl -X POST 'http://localhost:8000/v1/workspaces/2/organize/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "actions": ["normalize_titles", "apply_labels"],
    "dry_run": true
  }'
```

#### POST /v1/workspaces/{workspace_id}/organize/summaries

Generate an AI-powered progress summary for the workspace.

**Authentication:** Required (User JWT only)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Request Body:**
```json
{
  "period": "weekly",
  "include_sections": ["done", "active", "blocked", "risks", "next"]
}
```

**Validation Rules:**
- `period`: Summary period. One of: `daily`, `weekly`, `monthly`
- `include_sections`: Array of section names to include. Available sections:
  - `done`: Completed tasks
  - `active`: Tasks in progress
  - `blocked`: Blocked tasks
  - `risks`: Risk assessment
  - `next`: Next priorities

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 15,
    "workspace_id": 2,
    "period": "weekly",
    "snapshot_ts": "2025-10-18T10:00:00Z",
    "sections": {
      "done": ["Completed user authentication", "Fixed login bug"],
      "active": ["Building mobile app", "Implementing OAuth"],
      "blocked": [],
      "risks": ["Authentication refactor may delay mobile app"],
      "next": ["Start iOS app development", "Design new dashboard"]
    },
    "text": "# Weekly Summary\\n\\n## ✅ Done This Week\\n- Completed user authentication...\\n\\n## 🔄 Active Work\\n- Building mobile app...\\n\\n## 📅 Next Up\\n- Start iOS app development...",
    "author": "user@example.com",
    "cost_tokens": 2000
  },
  "message": "Generated weekly summary for workspace",
  "request_id": "uuid-v4"
}
```

**Example:**
```bash
curl -X POST 'http://localhost:8000/v1/workspaces/2/organize/summaries' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "period": "weekly",
    "include_sections": ["done", "active", "next"]
  }'
```

#### GET /v1/workspaces/{workspace_id}/organize/summaries

List previously generated summaries for a workspace.

**Authentication:** Required (User JWT only)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Query Parameters:**
- `period` (string, optional): Filter by period (`daily`, `weekly`, `monthly`)
- `limit` (integer, optional): Maximum number of summaries to return (default: 20)
- `offset` (integer, optional): Number of summaries to skip (default: 0)

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 15,
      "workspace_id": 2,
      "period": "weekly",
      "snapshot_ts": "2025-10-18T10:00:00Z",
      "sections": {
        "done": ["Completed user authentication"],
        "active": ["Building mobile app"],
        "next": ["Start iOS app development"]
      },
      "text": "# Weekly Summary\\n...",
      "author": "user@example.com",
      "cost_tokens": 2000
    }
  ],
  "message": null,
  "request_id": "uuid-v4"
}
```

**Example:**
```bash
curl -X GET 'http://localhost:8000/v1/workspaces/2/organize/summaries?period=weekly&limit=10' \
  -H 'Authorization: Bearer <jwt_token>'
```

#### POST /v1/tasks/{task_id}/auto-fill

Auto-fill task fields using AI based on the task title and existing context.

**Authentication:** Required (User JWT only)
**Required Role:** Contributor or higher

**Path Parameters:**
- `task_id` (integer): Task ID

**Request Body:**
```json
{
  "fields": ["description", "acceptance", "labels"]
}
```

**Validation Rules:**
- `fields`: Array of field names to auto-fill. Available fields:
  - `description`: Generate detailed task description
  - `acceptance`: Generate acceptance criteria
  - `labels`: Suggest relevant labels

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "task_id": "ENG-42",
    "filled_fields": {
      "description": "Implement JWT-based authentication system including token generation, validation, and refresh logic. Integrate with existing user management system.",
      "acceptance": [
        "Users can login with username/password",
        "JWT tokens are generated on successful login",
        "Token validation middleware protects API routes",
        "Refresh tokens extend session without re-login",
        "Tests cover all authentication flows"
      ],
      "labels": ["backend", "security", "authentication"]
    },
    "cost_tokens": 800
  },
  "message": "Auto-filled 3 fields for task ENG-42",
  "request_id": "uuid-v4"
}
```

**Notes:**
- This endpoint does NOT modify the task. It only returns suggested values.
- Apply the suggestions by making a separate PATCH request to update the task.

**Example:**
```bash
curl -X POST 'http://localhost:8000/v1/tasks/42/auto-fill' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "fields": ["description", "labels"]
  }'
```

#### GET /v1/workspaces/{workspace_id}/organize/duplicates

Detect potential duplicate tasks in the workspace using AI analysis.

**Authentication:** Required (User JWT only)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "task_ids": ["ENG-50", "ENG-51"],
      "similarity": 0.95,
      "reason": "Both tasks describe implementing user profile feature with similar wording",
      "suggested_action": "Merge into ENG-50, close ENG-51 as duplicate"
    },
    {
      "task_ids": ["ENG-60", "ENG-62", "ENG-65"],
      "similarity": 0.88,
      "reason": "All three tasks involve OAuth integration work that could be consolidated",
      "suggested_action": "Review and consolidate into single task"
    }
  ],
  "message": "Found 2 potential duplicate groups",
  "request_id": "uuid-v4"
}
```

**Notes:**
- Returns groups of potentially duplicate tasks with similarity scores
- Requires at least 2 tasks in the workspace
- Uses AI to analyze task titles, descriptions, and context
- Duplicate detection is read-only - does not modify tasks

**Example:**
```bash
curl -X GET 'http://localhost:8000/v1/workspaces/2/organize/duplicates' \
  -H 'Authorization: Bearer <jwt_token>'
```

---

### Attempts & Artifacts

Attempts track agent/human execution on tasks. Artifacts are work products (diffs, logs, files, etc.).

#### POST /tasks/{identifier}/attempts/start

Start a new attempt on a task.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Contributor or higher

**Path Parameters:**
- `identifier` (string): Task identifier (e.g., "ENG-42")

**Request Body:**
```json
{
  "notes": "Starting work on authentication implementation"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "task_id": 42,
    "task_identifier": "ENG-42",
    "actor_id": "agent:key-456",
    "actor_type": "agent",
    "started_at": "2025-10-16T12:00:00Z",
    "ended_at": null,
    "status": "running",
    "failure_class": null,
    "failure_message": null,
    "cost_tokens": null,
    "wall_clock_ms": null,
    "extra_metadata": {
      "notes": "Starting work on authentication implementation"
    },
    "created_at": "2025-10-16T12:00:00Z",
    "artifacts_count": 0
  },
  "message": "Attempt started on task 'ENG-42'",
  "request_id": "uuid-v4"
}
```

#### POST /attempts/{attempt_id}/finish

Finish an attempt with final status and metrics.

**Authentication:** Required (User JWT or Agent Key - must be attempt owner)
**Required Role:** Contributor or higher

**Path Parameters:**
- `attempt_id` (integer): Attempt ID

**Request Body:**
```json
{
  "status": "success",
  "failure_class": null,
  "failure_message": null,
  "cost_tokens": 5000,
  "wall_clock_ms": 120000,
  "notes": "Successfully implemented authentication",
  "extra_metadata": {
    "tests_passed": 15,
    "coverage": 85
  }
}
```

**Validation:**
- `status`: One of `success`, `failed`, `aborted` (required)
- `failure_class`: Required if status is `failed`. One of: `test_fail`, `tool_error`, `context_limit`, `rate_limit`, `permission`, `timeout`, `unknown`
- `failure_message`: Optional detailed failure message
- `cost_tokens`: Optional integer >= 0
- `wall_clock_ms`: Optional integer >= 0
- `notes`: Optional string
- `extra_metadata`: Optional JSON object

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "task_id": 42,
    "task_identifier": "ENG-42",
    "actor_id": "agent:key-456",
    "actor_type": "agent",
    "started_at": "2025-10-16T12:00:00Z",
    "ended_at": "2025-10-16T12:02:00Z",
    "status": "success",
    "failure_class": null,
    "failure_message": null,
    "cost_tokens": 5000,
    "wall_clock_ms": 120000,
    "extra_metadata": {
      "notes": "Successfully implemented authentication",
      "tests_passed": 15,
      "coverage": 85
    },
    "created_at": "2025-10-16T12:00:00Z",
    "artifacts_count": 0
  },
  "message": "Attempt finished with status 'success'",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `400 Bad Request`: Attempt already finished or invalid state
- `403 Forbidden`: Only attempt owner can finish it
- `404 Not Found`: Attempt does not exist

#### GET /attempts/{attempt_id}

Get attempt details.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `attempt_id` (integer): Attempt ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "task_id": 42,
    "task_identifier": "ENG-42",
    "actor_id": "agent:key-456",
    "actor_type": "agent",
    "started_at": "2025-10-16T12:00:00Z",
    "ended_at": "2025-10-16T12:02:00Z",
    "status": "success",
    "failure_class": null,
    "failure_message": null,
    "cost_tokens": 5000,
    "wall_clock_ms": 120000,
    "extra_metadata": {},
    "created_at": "2025-10-16T12:00:00Z",
    "artifacts_count": 3
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

#### GET /tasks/{identifier}/attempts

List all attempts for a task (newest first).

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `identifier` (string): Task identifier

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 123,
        "task_id": 42,
        "task_identifier": "ENG-42",
        "actor_id": "agent:key-456",
        "actor_type": "agent",
        "started_at": "2025-10-16T12:00:00Z",
        "ended_at": "2025-10-16T12:02:00Z",
        "status": "success",
        "failure_class": null,
        "failure_message": null,
        "cost_tokens": 5000,
        "wall_clock_ms": 120000,
        "extra_metadata": {},
        "created_at": "2025-10-16T12:00:00Z",
        "artifacts_count": 3
      }
    ],
    "total": 1
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

#### POST /attempts/{attempt_id}/artifacts

Create an artifact attached to an attempt.

**Authentication:** Required (User JWT or Agent Key - must be attempt owner)
**Required Role:** Contributor or higher

**Path Parameters:**
- `attempt_id` (integer): Attempt ID

**Request Body:**
```json
{
  "type": "diff",
  "name": "auth-implementation.diff",
  "content": "diff --git a/auth.py b/auth.py\n...",
  "mime_type": "text/plain",
  "extra_metadata": {
    "files_changed": 3,
    "lines_added": 150,
    "lines_removed": 20
  }
}
```

**Validation:**
- `type`: One of `diff`, `file`, `log`, `benchmark`, `screenshot` (required)
- `name`: 1-500 characters (required)
- `content`: Artifact content as text or base64 (required)
- `mime_type`: Optional MIME type
- `extra_metadata`: Optional JSON object

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 456,
    "attempt_id": 123,
    "type": "diff",
    "name": "auth-implementation.diff",
    "uri": "inline:diff --git a/auth.py...",
    "size_bytes": 4500,
    "mime_type": "text/plain",
    "preview": "diff --git a/auth.py b/auth.py\n...",
    "extra_metadata": {
      "files_changed": 3,
      "lines_added": 150,
      "lines_removed": 20
    },
    "created_at": "2025-10-16T12:01:30Z"
  },
  "message": "Artifact 'auth-implementation.diff' created successfully",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: Only attempt owner can add artifacts
- `404 Not Found`: Attempt does not exist

#### GET /artifacts/{artifact_id}

Get artifact details (without full content).

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `artifact_id` (integer): Artifact ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 456,
    "attempt_id": 123,
    "type": "diff",
    "name": "auth-implementation.diff",
    "uri": "inline:diff --git a/auth.py...",
    "size_bytes": 4500,
    "mime_type": "text/plain",
    "preview": "diff --git a/auth.py b/auth.py\n...",
    "extra_metadata": {
      "files_changed": 3,
      "lines_added": 150,
      "lines_removed": 20
    },
    "created_at": "2025-10-16T12:01:30Z"
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

#### GET /artifacts/{artifact_id}/download

Download full artifact content.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `artifact_id` (integer): Artifact ID

**Response (200 OK):**
- Returns raw artifact content with appropriate `Content-Type` header
- Includes `Content-Disposition: attachment; filename="..."` header

**Example:**
```bash
curl -X GET 'http://localhost:8000/artifacts/456/download' \
  -H 'Authorization: Bearer <jwt_token>' \
  -o auth-implementation.diff
```

#### GET /attempts/{attempt_id}/artifacts

List all artifacts for an attempt (oldest first).

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `attempt_id` (integer): Attempt ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 456,
        "attempt_id": 123,
        "type": "diff",
        "name": "auth-implementation.diff",
        "uri": "inline:...",
        "size_bytes": 4500,
        "mime_type": "text/plain",
        "preview": "diff --git a/auth.py...",
        "extra_metadata": {},
        "created_at": "2025-10-16T12:01:30Z"
      }
    ],
    "total": 1
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

---

### Events & Timeline

Events provide an append-only audit trail of all changes in the system.

#### GET /v1/tasks/{task_identifier}/history

Get event history for a specific task.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `task_identifier` (string): Task identifier (e.g., "ENG-42")

**Query Parameters:**
- `limit` (integer): Items per page (1-100, default 50)
- `offset` (integer): Pagination offset (default 0)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "task_id": "ENG-42",
    "events": [
      {
        "id": 789,
        "workspace_id": 2,
        "ts": "2025-10-16T12:00:00Z",
        "actor_id": "user-123",
        "actor_type": "user",
        "entity_type": "task",
        "entity_id": "ENG-42",
        "event_type": "updated",
        "changes": {
          "status": {
            "before": "todo",
            "after": "inprogress"
          }
        },
        "extra_metadata": {},
        "created_at": "2025-10-16T12:00:00Z"
      }
    ],
    "total": 1,
    "pagination": {
      "total": 1,
      "limit": 50,
      "offset": 0,
      "has_more": false
    }
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

#### GET /v1/tasks/{task_identifier}/timeline

Get unified timeline combining events, attempts, and artifacts.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `task_identifier` (string): Task identifier

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "task_id": "ENG-42",
    "items": [
      {
        "type": "event",
        "ts": "2025-10-16T12:00:00Z",
        "summary": "Task updated by user user-123 (1 fields)",
        "event_id": 789,
        "kind": "updated",
        "actor": "user-123",
        "actor_type": "user"
      },
      {
        "type": "attempt",
        "ts": "2025-10-16T12:00:00Z",
        "summary": "Attempt succeeded by agent agent:key-456 (120.0s)",
        "attempt_id": 123,
        "agent_id": "agent:key-456",
        "status": "success",
        "failure_class": null,
        "duration_ms": 120000
      },
      {
        "type": "artifact",
        "ts": "2025-10-16T12:01:30Z",
        "summary": "Diff uploaded: auth-implementation.diff",
        "artifact_id": 456,
        "attempt_id": 123,
        "artifact_type": "diff",
        "preview": "diff --git a/auth.py..."
      }
    ]
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

#### GET /v1/workspaces/{workspace_id}/events

Get events for a workspace with optional filtering.

**Authentication:** Required (User JWT or Agent Key)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Query Parameters:**
- `entity_type` (string): Filter by entity type (e.g., "task", "project")
- `entity_id` (string): Filter by entity ID
- `event_type` (string): Filter by event type (e.g., "created", "updated")
- `actor_id` (string): Filter by actor ID
- `since` (datetime): Events after this timestamp
- `until` (datetime): Events before this timestamp
- `limit` (integer): Items per page (1-100, default 50)
- `offset` (integer): Pagination offset (default 0)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": 789,
        "workspace_id": 2,
        "ts": "2025-10-16T12:00:00Z",
        "actor_id": "user-123",
        "actor_type": "user",
        "entity_type": "task",
        "entity_id": "ENG-42",
        "event_type": "updated",
        "changes": {},
        "extra_metadata": {},
        "created_at": "2025-10-16T12:00:00Z"
      }
    ],
    "pagination": {
      "total": 1,
      "limit": 50,
      "offset": 0,
      "has_more": false
    }
  },
  "message": null,
  "request_id": "uuid-v4"
}
```

---

### Agent Keys

Agent API keys provide workspace-scoped authentication for AI agents.

#### POST /v1/workspaces/{workspace_id}/agent-keys/

Create a new agent API key for the workspace.

**Authentication:** Required (User JWT)
**Required Role:** Maintainer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Request Body:**
```json
{
  "name": "CI/CD Pipeline Agent",
  "permissions": ["tasks:read", "tasks:write", "attempts:write"],
  "expires_at": "2026-10-16T00:00:00Z"
}
```

**Validation:**
- `name`: 1-255 characters, required
- `permissions`: Array of permission strings, optional
- `expires_at`: Optional expiration timestamp

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "key": "anyt_agent_abc123def456ghi789jkl012mno345",
    "agent_key": {
      "id": 10,
      "workspace_id": 2,
      "name": "CI/CD Pipeline Agent",
      "key_prefix": "anyt_age",
      "permissions": ["tasks:read", "tasks:write", "attempts:write"],
      "is_active": true,
      "last_used_at": null,
      "expires_at": "2026-10-16T00:00:00Z",
      "created_by": "user-123",
      "created_at": "2025-10-16T12:00:00Z"
    }
  },
  "message": "Agent API key created successfully. Store this key securely - it won't be shown again.",
  "request_id": "uuid-v4"
}
```

**Important:** The full API key is returned only once. Store it securely.

**Errors:**
- `403 Forbidden`: User lacks maintainer permissions

#### GET /v1/workspaces/{workspace_id}/agent-keys/

List all agent API keys for the workspace.

**Authentication:** Required (User JWT)
**Required Role:** Viewer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 10,
      "workspace_id": 2,
      "name": "CI/CD Pipeline Agent",
      "key_prefix": "anyt_age",
      "permissions": ["tasks:read", "tasks:write", "attempts:write"],
      "is_active": true,
      "last_used_at": "2025-10-16T11:30:00Z",
      "expires_at": "2026-10-16T00:00:00Z",
      "created_by": "user-123",
      "created_at": "2025-10-16T12:00:00Z"
    }
  ],
  "message": null,
  "request_id": "uuid-v4"
}
```

#### DELETE /v1/workspaces/{workspace_id}/agent-keys/{key_id}

Revoke (deactivate) an agent API key.

**Authentication:** Required (User JWT)
**Required Role:** Maintainer or higher

**Path Parameters:**
- `workspace_id` (integer): Workspace ID
- `key_id` (integer): Agent key ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "revoked": true,
    "key_id": 10
  },
  "message": "Agent key 'CI/CD Pipeline Agent' has been revoked",
  "request_id": "uuid-v4"
}
```

**Errors:**
- `403 Forbidden`: User lacks maintainer permissions
- `404 Not Found`: Agent key not found in workspace

---

## Data Models

### Workspace

```json
{
  "id": 1,
  "name": "Engineering Team",
  "identifier": "ENG",
  "description": "Software engineering workspace",
  "owner_id": "user-123",
  "task_counter": 42,
  "created_at": "2025-10-10T10:00:00Z",
  "updated_at": "2025-10-16T10:00:00Z",
  "deleted_at": null
}
```

### Project

```json
{
  "id": 3,
  "workspace_id": 2,
  "name": "Backend API",
  "identifier": "BACKEND",
  "description": "Backend services and APIs",
  "status": "active",
  "lead_id": "user-123",
  "start_date": "2025-10-01",
  "target_date": "2025-12-31",
  "color": "#4287f5",
  "icon": "🚀",
  "created_at": "2025-10-16T10:00:00Z",
  "updated_at": "2025-10-16T10:00:00Z",
  "deleted_at": null
}
```

### Task

```json
{
  "id": 42,
  "workspace_id": 2,
  "project_id": 3,
  "number": 42,
  "identifier": "ENG-42",
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication to the API",
  "status": "inprogress",
  "priority": 1,
  "owner_id": "user-123",
  "creator_id": "user-456",
  "labels": ["backend", "security"],
  "estimate": 8,
  "parent_id": null,
  "version": 3,
  "started_at": "2025-10-16T11:00:00Z",
  "completed_at": null,
  "canceled_at": null,
  "created_at": "2025-10-16T10:00:00Z",
  "updated_at": "2025-10-16T11:00:00Z",
  "deleted_at": null
}
```

### Attempt

```json
{
  "id": 123,
  "task_id": 42,
  "task_identifier": "ENG-42",
  "actor_id": "agent:key-456",
  "actor_type": "agent",
  "started_at": "2025-10-16T12:00:00Z",
  "ended_at": "2025-10-16T12:02:00Z",
  "status": "success",
  "failure_class": null,
  "failure_message": null,
  "cost_tokens": 5000,
  "wall_clock_ms": 120000,
  "extra_metadata": {},
  "created_at": "2025-10-16T12:00:00Z",
  "artifacts_count": 3
}
```

### Artifact

```json
{
  "id": 456,
  "attempt_id": 123,
  "type": "diff",
  "name": "auth-implementation.diff",
  "uri": "inline:diff --git a/auth.py...",
  "size_bytes": 4500,
  "mime_type": "text/plain",
  "preview": "diff --git a/auth.py b/auth.py\n...",
  "extra_metadata": {
    "files_changed": 3,
    "lines_added": 150,
    "lines_removed": 20
  },
  "created_at": "2025-10-16T12:01:30Z"
}
```

---

## Common Workflows

### Workflow 1: User Onboarding

```bash
# 1. User signs up with Supabase and gets JWT token
# 2. Setup default workspace and project
curl -X POST 'http://localhost:8000/v1/users/setup' \
  -H 'Authorization: Bearer <jwt_token>'

# 3. List workspaces
curl -X GET 'http://localhost:8000/v1/workspaces/' \
  -H 'Authorization: Bearer <jwt_token>'
```

### Workflow 2: Creating and Managing Tasks

```bash
# 1. Create a workspace
curl -X POST 'http://localhost:8000/v1/workspaces/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{"name": "My Team", "identifier": "TEAM"}'

# 2. Create a project
curl -X POST 'http://localhost:8000/v1/workspaces/1/projects/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{"name": "Sprint 1", "identifier": "SPRINT1"}'

# 3. Create a task
curl -X POST 'http://localhost:8000/v1/projects/1/tasks/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Setup database",
    "priority": 1,
    "labels": ["infrastructure"]
  }'

# 4. Get task with version
curl -X GET 'http://localhost:8000/v1/tasks/TEAM-1' \
  -H 'Authorization: Bearer <jwt_token>'

# 5. Update task with optimistic locking
curl -X PATCH 'http://localhost:8000/v1/tasks/TEAM-1' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'If-Match: 1' \
  -H 'Content-Type: application/json' \
  -d '{"status": "inprogress"}'
```

### Workflow 3: Agent Working on Task

```bash
# 1. Create agent API key (as admin user)
curl -X POST 'http://localhost:8000/v1/workspaces/1/agent-keys/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Build Agent",
    "permissions": ["tasks:read", "tasks:write", "attempts:write"]
  }'

# Save the returned key: anyt_agent_abc123...

# 2. Agent starts attempt
curl -X POST 'http://localhost:8000/tasks/TEAM-1/attempts/start' \
  -H 'X-API-Key: anyt_agent_abc123...' \
  -H 'Content-Type: application/json' \
  -d '{"notes": "Starting database setup"}'

# Response includes attempt_id: 123

# 3. Agent uploads artifacts
curl -X POST 'http://localhost:8000/attempts/123/artifacts' \
  -H 'X-API-Key: anyt_agent_abc123...' \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "log",
    "name": "setup.log",
    "content": "Database initialized successfully..."
  }'

# 4. Agent finishes attempt
curl -X POST 'http://localhost:8000/attempts/123/finish' \
  -H 'X-API-Key: anyt_agent_abc123...' \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "success",
    "cost_tokens": 1500,
    "wall_clock_ms": 45000
  }'

# 5. View task timeline
curl -X GET 'http://localhost:8000/v1/tasks/TEAM-1/timeline' \
  -H 'Authorization: Bearer <jwt_token>'
```

### Workflow 4: Goal Decomposition

```bash
# 1. Create a goal
curl -X POST 'http://localhost:8000/v1/workspaces/1/goals/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Build user dashboard",
    "description": "Create a comprehensive user dashboard",
    "project_id": 1,
    "context": {
      "tech_stack": ["React", "TypeScript"],
      "features": ["Analytics", "Notifications", "Settings"]
    }
  }'

# 2. Decompose goal into tasks
curl -X POST 'http://localhost:8000/v1/goals/1/decompose' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "max_tasks": 10,
    "max_depth": 2,
    "task_size_hours": 4,
    "dry_run": false
  }'

# Response includes generated tasks and dependencies
```

---

## Changelog

### 2025-10-18

**Added**
- **Labels API** - Workspace-scoped tags for task categorization
  - `POST /v1/workspaces/{workspace_id}/labels` - Create label
  - `GET /v1/workspaces/{workspace_id}/labels` - List workspace labels
  - `GET /v1/workspaces/{workspace_id}/labels/{label_id}` - Get label details
  - `PATCH /v1/workspaces/{workspace_id}/labels/{label_id}` - Update label
  - `DELETE /v1/workspaces/{workspace_id}/labels/{label_id}` - Delete label
- **Task Views (Saved Filters) API** - User-scoped saved filter views
  - `POST /v1/workspaces/{workspace_id}/task-views` - Create saved view
  - `GET /v1/workspaces/{workspace_id}/task-views` - List user's views
  - `GET /v1/workspaces/{workspace_id}/task-views/default` - Get default view
  - `GET /v1/workspaces/{workspace_id}/task-views/{view_id}` - Get view details
  - `PATCH /v1/workspaces/{workspace_id}/task-views/{view_id}` - Update view
  - `DELETE /v1/workspaces/{workspace_id}/task-views/{view_id}` - Delete view
- Advanced filtering support for tasks with priority ranges, owner IDs, label logic, and date ranges
- Row-level security (RLS) for task views - users can only access their own views
- Automatic default view management when setting/unsetting default views

### 2025-10-16

**Added**
- Initial comprehensive API documentation
- All v1 endpoints documented with examples
- Authentication methods (User JWT and Agent API keys)
- Response format standards
- Error handling documentation
- Common workflow examples
- `GET /v1/workspaces/current` - Get or create default workspace for user
- `GET /v1/workspaces/{workspace_id}/projects/current` - Get or create default project for workspace

**Documentation Coverage**
- Health & Test endpoints
- User Setup
- Workspaces & Workspace Members (including default workspace endpoint)
- Projects (including default project endpoint)
- Tasks (CRUD, filtering, bulk operations)
- Task Dependencies
- Labels (workspace-scoped tags)
- Task Views (user-scoped saved filters)
- Goals & Decomposition
- Attempts & Artifacts
- Events & Timeline
- Agent Keys

---

**For API support or questions, please contact the development team or refer to the source code at `/Users/bsheng/work/AnyTaskBackend/src/backend/routes/v1/`.**

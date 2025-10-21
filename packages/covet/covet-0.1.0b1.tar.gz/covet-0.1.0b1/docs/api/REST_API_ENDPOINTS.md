# CovetPy REST API Endpoints Documentation

**Version:** 0.2.0-sprint1
**Last Updated:** 2025-10-11
**Base URL:** `https://api.yourdomain.com` or `http://localhost:8000`

This document provides complete REST API endpoint documentation for production deployments of CovetPy applications.

## Table of Contents

1. [Authentication](#authentication)
2. [Users](#users)
3. [Posts & Content](#posts--content)
4. [Comments](#comments)
5. [Categories & Tags](#categories--tags)
6. [File Uploads](#file-uploads)
7. [Admin Operations](#admin-operations)
8. [Health & Metrics](#health--metrics)

---

## Authentication

### POST /api/auth/register

Register a new user account.

**Request:**
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-10-11T10:00:00Z",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- `400` - Invalid input data
- `409` - Username or email already exists

---

### POST /api/auth/login

Authenticate user and obtain access tokens.

**Request:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "roles": ["user"]
  }
}
```

**Errors:**
- `400` - Missing credentials
- `401` - Invalid credentials
- `403` - Account deactivated

---

### POST /api/auth/logout

Invalidate current session.

**Request:**
```http
POST /api/auth/logout
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

### POST /api/auth/refresh

Refresh access token using refresh token.

**Request:**
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "new_access_token_here",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

---

### POST /api/auth/password-reset

Request password reset email.

**Request:**
```http
POST /api/auth/password-reset
Content-Type: application/json

{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset email sent"
}
```

---

### POST /api/auth/password-reset/confirm

Confirm password reset with token.

**Request:**
```http
POST /api/auth/password-reset/confirm
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password updated successfully"
}
```

---

## Users

### GET /api/users/me

Get current authenticated user's profile.

**Request:**
```http
GET /api/users/me
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "avatar": "https://cdn.example.com/avatars/1.jpg",
  "bio": "Software developer",
  "is_active": true,
  "is_verified": true,
  "email_verified": true,
  "two_factor_enabled": false,
  "roles": ["user"],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-10-11T10:00:00Z",
  "last_login": "2025-10-11T09:00:00Z"
}
```

---

### PATCH /api/users/me

Update current user's profile.

**Request:**
```http
PATCH /api/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "bio": "Senior software developer",
  "avatar": "https://cdn.example.com/avatars/new.jpg"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "Jane",
  "bio": "Senior software developer",
  "avatar": "https://cdn.example.com/avatars/new.jpg",
  "updated_at": "2025-10-11T10:30:00Z"
}
```

---

### GET /api/users

List all users (paginated).

**Request:**
```http
GET /api/users?page=1&limit=20&sort=created_at&order=desc&search=john
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `limit` (int, default: 20, max: 100) - Items per page
- `sort` (string, default: created_at) - Sort field
- `order` (string, default: desc) - Sort order (asc/desc)
- `search` (string) - Search username, email, or name
- `is_active` (boolean) - Filter by active status
- `is_verified` (boolean) - Filter by verified status
- `role` (string) - Filter by role

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "avatar": "https://cdn.example.com/avatars/1.jpg",
      "is_active": true,
      "is_verified": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### GET /api/users/{user_id}

Get user by ID.

**Request:**
```http
GET /api/users/123
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 123,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "avatar": "https://cdn.example.com/avatars/123.jpg",
  "bio": "Software developer",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Errors:**
- `404` - User not found

---

### DELETE /api/users/{user_id}

Delete user (admin only).

**Request:**
```http
DELETE /api/users/123
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

**Errors:**
- `403` - Insufficient permissions
- `404` - User not found

---

## Posts & Content

### GET /api/posts

List all posts (paginated).

**Request:**
```http
GET /api/posts?page=1&limit=20&published=true&category=technology&sort=created_at&order=desc
```

**Query Parameters:**
- `page` (int) - Page number
- `limit` (int) - Items per page
- `published` (boolean) - Filter by published status
- `category` (string) - Filter by category slug
- `tag` (string) - Filter by tag slug
- `author` (int) - Filter by author ID
- `search` (string) - Search in title and content
- `sort` (string) - Sort field (created_at, updated_at, views, title)
- `order` (string) - Sort order (asc/desc)

**Response (200 OK):**
```json
{
  "posts": [
    {
      "id": 1,
      "title": "Getting Started with Python",
      "slug": "getting-started-with-python",
      "excerpt": "Learn Python basics in this comprehensive guide...",
      "author": {
        "id": 1,
        "username": "johndoe",
        "avatar": "https://cdn.example.com/avatars/1.jpg"
      },
      "category": {
        "id": 1,
        "name": "Technology",
        "slug": "technology"
      },
      "tags": [
        {"id": 1, "name": "Python", "slug": "python"},
        {"id": 2, "name": "Tutorial", "slug": "tutorial"}
      ],
      "published": true,
      "published_at": "2025-10-01T10:00:00Z",
      "view_count": 1234,
      "comment_count": 45,
      "created_at": "2025-10-01T09:00:00Z",
      "updated_at": "2025-10-11T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 250,
    "pages": 13,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### GET /api/posts/{post_id}

Get single post by ID.

**Request:**
```http
GET /api/posts/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Getting Started with Python",
  "slug": "getting-started-with-python",
  "content": "Full post content here...",
  "excerpt": "Learn Python basics...",
  "author": {
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "avatar": "https://cdn.example.com/avatars/1.jpg",
    "bio": "Software developer"
  },
  "category": {
    "id": 1,
    "name": "Technology",
    "slug": "technology",
    "description": "Technology articles"
  },
  "tags": [
    {"id": 1, "name": "Python", "slug": "python"},
    {"id": 2, "name": "Tutorial", "slug": "tutorial"}
  ],
  "published": true,
  "published_at": "2025-10-01T10:00:00Z",
  "view_count": 1235,
  "comment_count": 45,
  "created_at": "2025-10-01T09:00:00Z",
  "updated_at": "2025-10-11T10:00:00Z",
  "meta": {
    "reading_time": 5,
    "word_count": 1200
  }
}
```

**Errors:**
- `404` - Post not found

---

### GET /api/posts/slug/{slug}

Get post by slug.

**Request:**
```http
GET /api/posts/slug/getting-started-with-python
```

**Response:** Same as GET /api/posts/{post_id}

---

### POST /api/posts

Create new post (authenticated).

**Request:**
```http
POST /api/posts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "My New Post",
  "content": "Full post content here...",
  "excerpt": "Brief description",
  "category_id": 1,
  "tags": ["python", "tutorial"],
  "published": true
}
```

**Response (201 Created):**
```json
{
  "id": 42,
  "title": "My New Post",
  "slug": "my-new-post",
  "content": "Full post content here...",
  "excerpt": "Brief description",
  "author": {
    "id": 1,
    "username": "johndoe"
  },
  "category": {
    "id": 1,
    "name": "Technology",
    "slug": "technology"
  },
  "tags": [
    {"id": 1, "name": "Python", "slug": "python"},
    {"id": 2, "name": "Tutorial", "slug": "tutorial"}
  ],
  "published": true,
  "published_at": "2025-10-11T10:00:00Z",
  "created_at": "2025-10-11T10:00:00Z",
  "message": "Post created successfully"
}
```

**Errors:**
- `400` - Invalid input data
- `401` - Authentication required

---

### PUT /api/posts/{post_id}

Update post (author or admin only).

**Request:**
```http
PUT /api/posts/42
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content..."
}
```

**Response (200 OK):** Updated post object

**Errors:**
- `401` - Authentication required
- `403` - Insufficient permissions
- `404` - Post not found

---

### DELETE /api/posts/{post_id}

Delete post (author or admin only).

**Request:**
```http
DELETE /api/posts/42
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

## Comments

### GET /api/posts/{post_id}/comments

Get comments for a post.

**Request:**
```http
GET /api/posts/1/comments?page=1&limit=20
```

**Response (200 OK):**
```json
{
  "comments": [
    {
      "id": 1,
      "content": "Great article!",
      "author": {
        "id": 2,
        "username": "janedoe",
        "avatar": "https://cdn.example.com/avatars/2.jpg"
      },
      "parent_id": null,
      "reply_count": 3,
      "created_at": "2025-10-11T10:00:00Z",
      "updated_at": "2025-10-11T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

---

### POST /api/posts/{post_id}/comments

Add comment to post (authenticated).

**Request:**
```http
POST /api/posts/1/comments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Great article!",
  "parent_id": null
}
```

**Response (201 Created):**
```json
{
  "id": 46,
  "content": "Great article!",
  "author": {
    "id": 1,
    "username": "johndoe"
  },
  "parent_id": null,
  "created_at": "2025-10-11T10:30:00Z",
  "message": "Comment added successfully"
}
```

---

### PUT /api/comments/{comment_id}

Update comment (author only).

**Request:**
```http
PUT /api/comments/46
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Updated comment text"
}
```

**Response (200 OK):** Updated comment object

---

### DELETE /api/comments/{comment_id}

Delete comment (author or admin).

**Request:**
```http
DELETE /api/comments/46
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

## Categories & Tags

### GET /api/categories

List all categories.

**Request:**
```http
GET /api/categories
```

**Response (200 OK):**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Technology",
      "slug": "technology",
      "description": "Technology related articles",
      "post_count": 42
    }
  ],
  "count": 10
}
```

---

### GET /api/categories/{category_id}

Get category with posts.

**Request:**
```http
GET /api/categories/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Technology",
  "slug": "technology",
  "description": "Technology related articles",
  "post_count": 42,
  "recent_posts": [
    {
      "id": 1,
      "title": "Getting Started with Python",
      "slug": "getting-started-with-python",
      "published_at": "2025-10-01T10:00:00Z"
    }
  ]
}
```

---

### POST /api/categories

Create category (admin only).

**Request:**
```http
POST /api/categories
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Web Development",
  "description": "Web development articles"
}
```

**Response (201 Created):**
```json
{
  "id": 11,
  "name": "Web Development",
  "slug": "web-development",
  "description": "Web development articles",
  "created_at": "2025-10-11T10:00:00Z"
}
```

---

### GET /api/tags

List all tags.

**Request:**
```http
GET /api/tags?sort=post_count&order=desc
```

**Response (200 OK):**
```json
{
  "tags": [
    {
      "id": 1,
      "name": "Python",
      "slug": "python",
      "post_count": 25
    }
  ],
  "count": 50
}
```

---

## File Uploads

### POST /api/upload

Upload file (authenticated).

**Request:**
```http
POST /api/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file=@/path/to/file.jpg
```

**Response (201 Created):**
```json
{
  "id": "abc123",
  "filename": "file.jpg",
  "original_filename": "my-photo.jpg",
  "mime_type": "image/jpeg",
  "size": 245678,
  "url": "https://cdn.example.com/uploads/abc123.jpg",
  "thumbnail_url": "https://cdn.example.com/uploads/abc123_thumb.jpg",
  "uploaded_at": "2025-10-11T10:00:00Z"
}
```

**Errors:**
- `400` - Invalid file type or size
- `413` - File too large

---

## Admin Operations

### GET /api/admin/stats

Get application statistics (admin only).

**Request:**
```http
GET /api/admin/stats
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "users": {
    "total": 1500,
    "active": 1200,
    "new_today": 45
  },
  "posts": {
    "total": 250,
    "published": 200,
    "draft": 50,
    "new_today": 10
  },
  "comments": {
    "total": 1234,
    "new_today": 89
  },
  "system": {
    "uptime": 864000,
    "cpu_usage": 45.5,
    "memory_usage": 62.3,
    "disk_usage": 38.2
  }
}
```

---

## Health & Metrics

### GET /health

Health check endpoint (no auth required).

**Request:**
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-11T10:00:00Z",
  "version": "0.2.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "storage": "healthy"
  },
  "uptime": 864000
}
```

---

### GET /metrics

Prometheus metrics (no auth required).

**Request:**
```http
GET /metrics
```

**Response (200 OK):** Prometheus text format
```
# HELP covet_http_requests_total Total HTTP requests
# TYPE covet_http_requests_total counter
covet_http_requests_total{method="GET",status="200"} 12345

# HELP covet_http_request_duration_seconds HTTP request duration
# TYPE covet_http_request_duration_seconds histogram
covet_http_request_duration_seconds_bucket{le="0.1"} 1000
```

---

## Common Patterns

### Error Response Format

All error responses follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional information"
  },
  "request_id": "req_abc123",
  "timestamp": "2025-10-11T10:00:00Z"
}
```

### Pagination

All list endpoints support pagination with these parameters:
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20, max: 100)

Response includes pagination metadata:
```json
{
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 250,
    "pages": 13,
    "has_next": true,
    "has_prev": false
  }
}
```

### Filtering

Use query parameters for filtering:
- Exact match: `?field=value`
- Greater than: `?field_gt=value`
- Less than: `?field_lt=value`
- Contains: `?field_contains=value`
- In list: `?field_in=value1,value2`

### Sorting

Use `sort` and `order` parameters:
- `?sort=created_at&order=desc`
- Multiple fields: `?sort=category,created_at&order=asc,desc`

---

## Rate Limiting

All endpoints are rate limited:
- Anonymous: 10 req/min
- Authenticated: 60 req/min
- Premium: 300 req/min

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 55
X-RateLimit-Reset: 1633888800
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-11

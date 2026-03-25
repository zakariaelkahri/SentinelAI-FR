# JWT Authentication System

Simple JWT-based authentication system for SentinelAI.

## Overview

The authentication system provides:
- **JWT token-based authentication**
- **Role-based access control (RBAC)**
- **Password hashing with bcrypt**
- **Protected routes**
- **User session management**

## Components

### Core Modules

1. **`app/core/security.py`** - Password hashing and JWT token utilities
2. **`app/core/auth.py`** - Authentication dependencies
3. **`app/schemas/auth.py`** - Authentication schemas (requests/responses)
4. **`app/api/auth.py`** - Authentication routes (login, logout, me)
5. **`app/api/users.py`** - Protected route examples

## API Endpoints

### Authentication Endpoints

#### POST `/auth/login`
Login with username and password to get a JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "username": "admin",
    "status": "active",
    "role_name": "admin",
    "created_at": "2024-03-24T10:00:00"
  }
}
```

#### GET `/auth/me`
Get current authenticated user information (requires authentication).

**Headers:**
```
Authorization: Bearer <your_token>
```

**Response:**
```json
{
  "id": "uuid",
  "username": "admin",
  "status": "active",
  "role_name": "admin",
  "created_at": "2024-03-24T10:00:00"
}
```

#### POST `/auth/logout`
Logout endpoint (client should discard the token).

**Headers:**
```
Authorization: Bearer <your_token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## Usage Examples

### 1. Login and Get Token

```bash
# Using curl
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Access Protected Route

```bash
# Using curl with token
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <your_token>"
```

### 3. Using in Python/JavaScript

**Python (httpx):**
```python
import httpx

# Login
response = httpx.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "admin123"}
)
data = response.json()
token = data["access_token"]

# Access protected route
response = httpx.get(
    "http://localhost:8000/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)
user = response.json()
```

**JavaScript (fetch):**
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const { access_token } = await loginResponse.json();

// Access protected route
const userResponse = await fetch('http://localhost:8000/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const user = await userResponse.json();
```

## Creating Protected Routes

### Basic Protection (Requires Authentication)

```python
from fastapi import APIRouter, Depends
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}"}
```

### Role-Based Protection

```python
from fastapi import APIRouter, Depends
from app.core.auth import require_role

router = APIRouter()

# Admin only
@router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
async def admin_only():
    return {"message": "Admin only"}

# Multiple roles allowed
@router.get("/staff-only", dependencies=[Depends(require_role("admin", "supervisor"))])
async def staff_only():
    return {"message": "Admin or Supervisor only"}
```

### Custom Access Control

```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/custom-check")
async def custom_check(current_user: User = Depends(get_current_active_user)):
    # Custom business logic
    if not some_condition(current_user):
        raise HTTPException(status_code=403, detail="Access denied")

    return {"message": "Access granted"}
```

## Configuration

### Environment Variables (.env)

```env
# JWT Authentication
SECRET_KEY=your-secret-key-here  # Change in production!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**⚠️ IMPORTANT:** Change the `SECRET_KEY` in production! Generate a secure key:

```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Using OpenSSL
openssl rand -hex 32
```

## Default Users (from seeders)

| Username   | Password      | Role       |
|------------|---------------|------------|
| admin      | admin123      | admin      |
| supervisor | supervisor123 | supervisor |
| operator1  | operator123   | operator   |
| operator2  | operator123   | operator   |

**⚠️ WARNING:** Change these default passwords in production!

## Security Best Practices

1. **Change default SECRET_KEY** in production
2. **Change default user passwords** after deployment
3. **Use HTTPS** in production
4. **Set appropriate token expiration** times
5. **Implement token refresh** for long-lived sessions (optional)
6. **Store tokens securely** on the client (httpOnly cookies or secure storage)
7. **Validate and sanitize** all user inputs
8. **Implement rate limiting** on login endpoint

## Token Expiration

- Default token expiration: **60 minutes** (configurable)
- Tokens are stateless and cannot be revoked (logout happens client-side)
- For token revocation, consider adding a token blacklist with Redis

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Inactive user"
}
// or
{
  "detail": "Role 'operator' not authorized. Required: admin"
}
```

## Testing

### Using FastAPI Docs (Swagger)

1. Go to `http://localhost:8000/docs`
2. Click on `/auth/login` endpoint
3. Click "Try it out"
4. Enter credentials and execute
5. Copy the `access_token` from the response
6. Click the "Authorize" button at the top
7. Enter: `Bearer <your_token>`
8. Now you can test all protected endpoints

### Using pytest

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_protected_route(client: AsyncClient, auth_token: str):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
```

## Troubleshooting

### "Could not validate credentials"
- Token is expired or invalid
- Check if the token is correctly formatted: `Bearer <token>`
- Verify SECRET_KEY matches between token creation and validation

### "Inactive user"
- User account status is not "active"
- Check user status in database

### "Role not authorized"
- User doesn't have the required role
- Check user's role assignment in database

# API Standardization Guide for ResumeRocket

This guide documents the standardized API implementation for ResumeRocket's Next.js integration. We've created a dedicated API blueprint with consistent endpoints focused solely on serving JSON responses.

## 1. API Response Format

All API responses follow this standard format:

```json
{
  "status": "success|error",
  "data": { ... },
  "error": "Error message (only present when status is error)"
}
```

## 2. Available Utilities

### In extensions.py:

- `api_response(data=None, error=None, status_code=200)`: Creates standardized API responses

## 3. API Implementation Approach

Instead of dual-purpose routes that handle both HTML templates and JSON responses, we've implemented:

1. A dedicated API blueprint (`api_bp`) with the `/api` prefix
2. Endpoints that only return standardized JSON responses
3. JWT authentication for all protected endpoints
4. Clear permission checks and error handling

## 4. API Endpoints Overview

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Log in and get a JWT token |
| `/api/auth/register` | POST | Register a new user |
| `/api/auth/refresh` | POST | Refresh an existing JWT token |
| `/api/auth/me` | GET | Get current user information |

### Dashboard

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard` | GET | Get dashboard data with optional search parameter |

### Resumes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resumes` | GET | List all user's resumes |
| `/api/resumes/:id` | GET | Get a specific resume |
| `/api/resumes/:id` | DELETE | Delete a resume |
| `/api/process-resume` | POST | Upload and process a resume |
| `/api/customize-resume` | POST | Customize a resume for a job |
| `/api/compare/:id` | GET | Get comparison data for a resume |

### Jobs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/jobs` | GET | List all user's job descriptions |
| `/api/jobs/:id` | GET | Get a specific job description |
| `/api/jobs/url` | POST | Submit a job URL |
| `/api/jobs/text` | POST | Submit job description text |

### Statistics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/statistics` | GET | Get usage statistics |

## 5. Example API Usage

### Authentication

```javascript
// Login
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

const { status, data, error } = await response.json();
if (status === 'success') {
  // Store token
  localStorage.setItem('token', data.token);
}
```

### API Request with Authentication

```javascript
// Get dashboard data
const response = await fetch('/api/dashboard', {
  headers: { 
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const { status, data, error } = await response.json();
if (status === 'success') {
  // Use dashboard data
  const { dashboard_data, total_resumes, avg_improvement } = data;
}
```

## 6. Key Pattern: Permission Checking

Each endpoint includes appropriate permission checks:

```python
@api_bp.route('/resumes/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    user_id = get_jwt_identity()
    
    # Query for the specific resume
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the user
    if resume.user_id != user_id:
        return api_response(error="Permission denied", status_code=403)
    
    # Continue with the request...
```

## 7. Error Handling

Each endpoint includes comprehensive error handling:

```python
try:
    # Operation that might fail
    db.session.add(entity)
    db.session.commit()
    return api_response(data={...})
except Exception as e:
    db.session.rollback()
    logger.error(f"Operation error: {str(e)}")
    return api_response(error="Operation failed", status_code=500)
```

## 8. Transitioning from HTMX to Next.js

When connecting the Next.js frontend to these endpoints:

1. Use the fetch API or a client like axios to make requests
2. Store the JWT token in localStorage or a secure HTTP-only cookie
3. Include the token in the Authorization header for all authenticated requests
4. Handle API responses consistently by checking the status field
5. Implement proper error handling and loading states in the UI

By following these patterns, the Next.js frontend will seamlessly integrate with the Flask backend through the standardized APIs, providing a modern and responsive user experience.
# Next.js Frontend Integration Plan

## Overview
This document outlines the plan for integrating the new Next.js frontend with the existing Flask backend. The goal is to create a modern, responsive user interface while retaining the existing backend functionality.

## Current Architecture
- **Backend**: Flask with SQLite/SQLAlchemy
- **Frontend**: Template-based with HTMX, Tailwind CSS, Alpine.js
- **API Communication**: Mix of standard API calls and streaming with Anthropic API

## New Architecture
- **Backend**: Retain Flask with SQLite/SQLAlchemy
- **Frontend**: Next.js with React, Tailwind CSS
- **API Communication**: Standard REST API calls (no streaming for initial implementation)

## Integration Steps

### 1. Backend Preparation

#### 1.1 Create REST API Endpoints
- Modify existing Flask routes to serve as pure API endpoints
- Ensure all endpoints return proper JSON responses
- Document API response formats for frontend consumption

#### 1.2 Enable CORS
```python
from flask_cors import CORS

# Add to app initialization
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
```

#### 1.3 Authentication
- Create JWT-based authentication endpoints
- Return tokens for frontend to store and use

### 2. Frontend Implementation

#### 2.1 API Client
- Create API client utilities in Next.js for communicating with Flask backend
- Implement authentication token management
- Handle error states and loading states

#### 2.2 Page-by-Page Implementation
1. **Landing Page**: Simple static page with authentication links
2. **Dashboard**: Display user's resume history and statistics
3. **Resume Upload**: Form for uploading resume and job description
4. **Customization Results**: Display customization results with loading indicator
5. **User Profile**: User settings and management

#### 2.3 State Management
- Use React context or state management library for app-wide state
- Implement loading indicators during API calls

### 3. Deployment Considerations

#### 3.1 Development Environment
- Next.js running on port 3000
- Flask running on port 8080
- Local development with proxy configuration

#### 3.2 Production Options
1. **Separate Deployments**: Deploy Next.js to Vercel and Flask to Fly.io
2. **Combined Deployment**: Serve Next.js static build through Flask

### 4. Implementation Phases

#### Phase 1: Basic Setup
- Setup Next.js project structure
- Implement authentication flow
- Create API client utilities

#### Phase 2: Core Functionality
- Implement dashboard
- Resume upload and processing
- Basic customization workflow

#### Phase 3: Enhanced Features
- User settings
- History and analytics
- Export options

#### Phase 4: Performance Optimization
- Implement caching strategies
- Optimize API payloads
- Consider bringing back streaming functionality

## API Endpoints Reference

### Authentication
- `/auth/login` (POST): User login, returns JWT token
- `/auth/register` (POST): User registration
- `/auth/me` (GET): Get current user details

### Resume Operations
- `/api/process_resume` (POST): Upload and process resume
- `/api/customize-resume` (POST): Customize resume against job description 
- `/api/save_customized_resume` (POST): Save customization result

### User Dashboard
- `/api/dashboard` (GET): Get user dashboard data
- `/api/resume/:id` (GET): Get specific resume details
- `/api/resume/:id/delete` (DELETE): Delete a resume

## Timeline
- Setup and Authentication: 1 week
- Core Functionality: 2 weeks
- Enhanced Features: 1 week
- Testing and Refinement: 1 week
- Total Estimated Time: 5 weeks
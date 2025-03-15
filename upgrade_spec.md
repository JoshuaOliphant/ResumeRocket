# ResumeRocket Next.js Integration Plan

This document outlines a focused plan to connect the existing Next.js frontend with the existing Flask backend for ResumeRocket. The plan also incorporates Anthropic prompt caching to optimize API usage and reduce costs.

## Current State Analysis

### Frontend (Next.js)
- UI components are mostly built using Shadcn/UI
- Basic pages exist (dashboard, homepage)
- API utilities are implemented (api-services.ts, api-types.ts, utils.ts)
- Component structure is in place
- Missing auth implementation and data fetching

### Backend (Flask)
- Complete Flask backend with all necessary routes
- Routes already return JSON for API requests in some places
- JWT authentication partially implemented
- CORS configuration exists but may need updates
- Missing standardized API response format

## Integration Approach

The integration will focus on:
1. Creating missing API endpoints in the backend
2. Implementing authentication in the frontend
3. Connecting frontend components to backend data
4. Implementing Anthropic prompt caching

## Implementation Phases

### Phase 1: Backend API Standardization

Ensure all backend routes can serve both HTML templates and JSON API responses with a consistent format.

#### Tasks

1. **Create API Response Handler**
   - Create a utility function for standardized API responses
   - Implement error handling for API requests
   - Add content negotiation to detect API vs web requests

2. **Enhance Existing Routes**
   - Update dashboard route to support API response format
   - Add missing API endpoints for authentication and dashboard data
   - Ensure consistent error handling

3. **Implement JWT Refresh**
   - Add token refresh endpoint
   - Configure proper token expiration
   - Implement token validation

#### Prompt for Implementation

```
I need to standardize the API responses in my Flask backend to support the Next.js frontend. I already have some API routes but need to ensure all core functionality can be accessed via JSON API.

1. Create a utility function for standardized API responses
2. Add a dashboard API endpoint at /api/dashboard
3. Update the resume routes to ensure they all support JSON
4. Implement proper JWT token refresh

My backend is organized with blueprint-based routes, and I already have JWT support configured in app.py. Some routes already handle JSON responses, but I need to make it consistent across all routes.

Please provide the implementation for:
1. An api_response utility function
2. An updated dashboard API endpoint
3. A JWT token refresh endpoint
4. Examples of how to update existing routes
```

### Phase 2: Anthropic Prompt Caching Implementation

Implement prompt caching to optimize Claude API usage, based on the existing prompt_caching_plan.md.

#### Tasks

1. **Create Claude API Client**
   - Update the existing services to use the latest Anthropic SDK
   - Implement a centralized client with caching support
   - Add metrics tracking for cache performance

2. **Refactor Core Services**
   - Update ResumeCustomizer to use cache_control
   - Update AISuggestions for prompt caching
   - Add caching for resume analysis

#### Prompt for Implementation

```
I need to implement Anthropic's prompt caching feature in my ResumeRocket application. I already have the services implemented (resume_customizer.py and ai_suggestions.py), but need to update them to use prompt caching.

Based on the prompt_caching_plan.md, I need to:

1. Create a centralized Claude API client that supports prompt caching
2. Refactor my existing services to use this client
3. Structure prompts for optimal caching efficiency

The backend uses Python Flask and the Anthropic Python SDK. Please provide the implementation for:
1. A Claude client class that supports prompt caching
2. Updates to resume_customizer.py to use cache_control
3. Updates to ai_suggestions.py to use cache_control
```

### Phase 3: Authentication Implementation

Implement authentication in the Next.js frontend to connect with the Flask backend.

#### Tasks

1. **Create Auth Context**
   - Implement React Context for authentication state
   - Add token management
   - Create protected route wrapper

2. **Build Auth Pages**
   - Create login page
   - Create registration page
   - Implement token refresh logic

3. **Connect to Backend**
   - Implement API calls to authentication endpoints
   - Add token storage and management
   - Handle auth errors and redirects

#### Prompt for Implementation

```
I need to implement authentication in my Next.js frontend to connect with my Flask backend. I already have:
- API utility functions in lib/utils.ts
- API service functions for auth in lib/api-services.ts
- Type definitions in lib/api-types.ts

The backend supports both session-based auth and JWT tokens. For the frontend, I need to:
1. Create an AuthContext provider 
2. Build login and registration pages
3. Implement token storage and refresh
4. Create protected route components

Please provide the implementation for:
1. An AuthContext and AuthProvider component
2. A login page component
3. A registration page component
4. A protected route wrapper
```

### Phase 4: Data Fetching Implementation

Connect frontend components to backend data sources.

#### Tasks

1. **Dashboard Data Fetching**
   - Connect dashboard components to API
   - Implement loading states
   - Add error handling

2. **Resume Management**
   - Connect resume upload and viewing
   - Add resume selection component
   - Implement resume deletion

3. **Job Description Management**
   - Connect job description input
   - Add job listing display
   - Implement job selection

#### Prompt for Implementation

```
I need to connect my Next.js frontend components to the backend API data. I already have the UI components built (with mock data), and the API endpoints exist, but I need to implement data fetching.

For the dashboard page, I need to:
1. Connect RecentOptimizations component to real data
2. Connect StatisticsSection component to real data
3. Connect SavedJobs component to real data
4. Add loading and error states

I have these API services defined in lib/api-services.ts but they need to be connected to the components.

Please provide the implementation for:
1. Updated dashboard page with real data fetching
2. Updated component implementations with loading states
3. Error handling for API requests
```

### Phase 5: Resume Processing Implementation

Implement resume upload and customization functionality.

#### Tasks

1. **Resume Upload**
   - Create resume upload page
   - Implement file upload functionality
   - Add resume parsing and display

2. **Resume Customization**
   - Create customization options form
   - Implement job selection
   - Add customization process with loading state

3. **Results Display**
   - Create comparison view
   - Implement before/after display
   - Add export functionality

#### Prompt for Implementation

```
I need to implement the resume upload and customization pages in my Next.js frontend. The backend APIs for these features already exist.

For resume management, I need:
1. A resume upload page with file upload or text input
2. A resume management page to view/delete saved resumes
3. A resume customization form with job selection and customization options
4. A results page with before/after comparison

I have API endpoints for:
- Resume upload: POST /api/process_resume
- Resume customization: POST /api/customize-resume
- Resume comparison: GET /api/compare/:id

Please provide the implementation for:
1. A resume upload page component
2. A resume customization form component
3. A results comparison component
```

### Phase 6: Job Management Implementation

Create job description input and management functionality.

#### Tasks

1. **Job Input Methods**
   - Implement job URL input
   - Create job text input
   - Add job parsing and display

2. **Job Management**
   - Create job listing page
   - Implement job deletion
   - Add job details view

3. **Job Selection**
   - Create job selection for resume customization
   - Add job search and filtering
   - Implement job save/bookmark functionality

#### Prompt for Implementation

```
I need to implement job description management in my Next.js frontend. The backend APIs for these features already exist.

For job management, I need:
1. A job input page that accepts URL or direct text input
2. A job management page to view saved jobs
3. A job selection component for the resume customization flow

I have API endpoints for:
- Job URL submission: POST /api/job/url
- Job text submission: POST /api/job/text
- Job listing: GET /api/jobs

Please provide the implementation for:
1. A job input page with URL and text options
2. A job management page
3. A job selection component for customization
```

### Phase 7: Navigation and Layout

Implement site-wide navigation and layout components.

#### Tasks

1. **Navigation Structure**
   - Create main navigation component
   - Implement sidebar with proper routing
   - Add mobile responsive navigation

2. **Page Layouts**
   - Implement authenticated layout
   - Create public layout
   - Add page transitions

3. **User Profile**
   - Create user profile page
   - Implement settings
   - Add account management

#### Prompt for Implementation

```
I need to implement the navigation and layout structure for my Next.js application. I already have some components like the sidebar, but need to connect them with proper routing and authentication state.

For navigation and layout, I need:
1. A main navigation component that adapts based on auth state
2. A layout component that wraps authenticated pages
3. A public layout for unauthenticated pages
4. Mobile-responsive navigation

Please provide the implementation for:
1. An authenticated layout component
2. A public layout component
3. A connected navigation component
4. Mobile navigation implementation
```

### Phase 8: Enhanced Features

Add advanced features beyond the basic functionality.

#### Tasks

1. **Resume Comparison**
   - Implement side-by-side comparison
   - Add diff highlighting
   - Create detailed analysis display

2. **Analytics Dashboard**
   - Create enhanced analytics
   - Add usage statistics
   - Implement performance tracking

3. **Export Options**
   - Implement PDF export
   - Add DOCX export
   - Create formatting options

#### Prompt for Implementation

```
I need to implement enhanced features for my Next.js resume application. The basic functionality is working, but I want to add more advanced capabilities.

For enhanced features, I need:
1. A detailed resume comparison view with diff highlighting
2. An analytics dashboard for users to track their progress
3. Enhanced export options with formatting controls

I already have API endpoints for comparison data and exports. Please provide the implementation for:
1. A detailed comparison component with diff highlighting
2. An analytics dashboard page with charts
3. An export options component with format selection
```

### Phase 9: Testing and Optimization

Implement tests and optimize performance.

#### Tasks

1. **Component Testing**
   - Create unit tests for key components
   - Add integration tests
   - Implement E2E testing

2. **Performance Optimization**
   - Implement code splitting
   - Add image optimization
   - Optimize API requests

3. **Error Handling**
   - Create global error boundary
   - Implement retry logic
   - Add offline support

#### Prompt for Implementation

```
I need to implement testing and performance optimization for my Next.js application. The app is functional but needs better reliability and performance.

For testing and optimization, I need:
1. Unit tests for key components like authentication and data fetching
2. Performance optimizations for faster loading
3. Comprehensive error handling

Please provide the implementation for:
1. Test setup and examples for key components
2. Performance optimization techniques
3. Global error handling implementation
```

### Phase 10: Deployment Configuration

Prepare the application for production deployment.

#### Tasks

1. **Build Configuration**
   - Set up production build process
   - Configure environment variables
   - Create deployment scripts

2. **Deployment Documentation**
   - Create setup instructions
   - Document environment variables
   - Add troubleshooting guide

3. **Monitoring Setup**
   - Implement error tracking
   - Add performance monitoring
   - Create health checks

#### Prompt for Implementation

```
I need to prepare my Next.js and Flask application for production deployment. The application is fully functional but needs production configuration.

For deployment, I need:
1. Build configuration for the Next.js frontend
2. Environment variable setup for both frontend and backend
3. Deployment documentation

Please provide the implementation for:
1. A production build configuration
2. Deployment scripts for both frontend and backend
3. Comprehensive deployment documentation
```

## Technical Considerations

### 1. Authentication Flow

The system will maintain dual authentication:
- JWT tokens stored in localStorage for the Next.js frontend
- Session-based auth maintained for backward compatibility

### 2. API Communication

- All frontend-backend communication will use REST API endpoints
- Responses will follow a consistent format: `{ data, error, status }`
- Content negotiation will determine whether to return HTML or JSON

### 3. Prompt Caching Strategy

The implementation will use Anthropic's prompt caching to optimize costs:
- Separate static and dynamic content in prompts
- Use cache_control parameters for static content
- Track cache performance metrics

### 4. Error Handling

Implement proper error handling across the application:
- Standard error responses from backend
- Retry logic for transient failures
- User-friendly error messages in the frontend

## Implementation Timeline

This project can be completed in approximately 2 weeks with the following timeline:

1. Backend API Standardization (1-2 days)
2. Anthropic Prompt Caching (1 day)
3. Authentication Implementation (1-2 days)
4. Data Fetching Implementation (1-2 days)
5. Resume Processing Implementation (1-2 days)
6. Job Management Implementation (1 day)
7. Navigation and Layout (1 day)
8. Enhanced Features (2 days)
9. Testing and Optimization (1-2 days)
10. Deployment Configuration (1 day)

## Success Criteria

The integration will be considered successful when:

1. Users can authenticate and access all features through the Next.js frontend
2. All data is correctly fetched and displayed from the backend
3. Resume customization works end-to-end with proper loading states
4. Anthropic prompt caching reduces API costs by at least 30%
5. The application performs well in production-like conditions

## Post-Launch Considerations

After the initial launch, consider these enhancements:

1. **Progressive Web App** capabilities for offline support
2. **Mobile optimization** for better small-screen experience
3. **Performance profiling** for identifying bottlenecks
4. **Analytics integration** for tracking user behavior
5. **A/B testing framework** for feature optimization
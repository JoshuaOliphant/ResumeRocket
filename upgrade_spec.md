# ResumeRocket Next.js Integration Plan

This document outlines a focused plan to connect the existing Next.js frontend with the existing Flask backend for ResumeRocket. The plan also incorporates Anthropic prompt caching to optimize API usage and reduce costs.

## Current State Analysis

### Frontend (Next.js)
- ✅ UI components built using Shadcn/UI
- ✅ Complete pages for all core functionality
- ✅ API utilities implemented and connected to backend
- ✅ Auth implementation with JWT token management
- ✅ Data fetching with React Query
- ✅ Navigation and layouts for all authentication states
- ✅ Job management with search and filtering
- ✅ Mobile-responsive design

### Backend (Flask)
- ✅ Complete Flask backend with all necessary routes
- ✅ Standardized API endpoints implemented through a dedicated API blueprint
- ✅ JWT authentication fully implemented with token refresh
- ✅ Consistent API response format for all endpoints
- ✅ CORS configuration for frontend integration

## Integration Approach

The integration will focus on:
1. Creating missing API endpoints in the backend
2. Implementing authentication in the frontend
3. Connecting frontend components to backend data
4. Implementing Anthropic prompt caching

## Implementation Phases

### Phase 1: Backend API Standardization ✅ COMPLETED

Create a dedicated API blueprint with consistent JSON responses for the Next.js frontend.

#### Tasks

1. **Create API Response Handler** ✅
   - ✅ Create a utility function for standardized API responses
   - ✅ Implement error handling for API requests
   - ✅ Create a dedicated API blueprint for Next.js endpoints

2. **Implement Core API Endpoints** ✅
   - ✅ Add comprehensive authentication endpoints with JWT
   - ✅ Create dashboard API endpoints for user data
   - ✅ Implement resume and job management endpoints

3. **Implement JWT Authentication** ✅
   - ✅ Add token refresh endpoint
   - ✅ Configure proper token expiration
   - ✅ Implement token validation and permission checks

#### Implementation Details

The API standardization has been implemented with these key components:

1. A standardized API response utility function in `extensions.py`
2. A dedicated API blueprint (`api_bp`) in `routes/api.py` with clean endpoints
3. JWT authentication throughout all protected endpoints
4. Consistent error handling and permission checking
5. Documentation in `docs/api_standardization_guide.md`

### Phase 2: Anthropic Prompt Caching Implementation ✅ COMPLETED

Implement prompt caching to optimize Claude API usage, based on the existing prompt_caching_plan.md.

#### Tasks

1. **Create Claude API Client** ✅
   - ✅ Update the existing services to use the latest Anthropic SDK
   - ✅ Implement a centralized client with caching support
   - ✅ Add metrics tracking for cache performance

2. **Refactor Core Services** ✅
   - ✅ Update ResumeCustomizer to use cache_control
   - ✅ Update AISuggestions for prompt caching
   - ✅ Add caching for resume analysis

#### Implementation Details

The Anthropic prompt caching has been implemented with these key components:

1. A centralized `ClaudeClient` class in `backend/services/claude_client.py` that:
   - Manages both Anthropic's server-side caching and local file caching
   - Automatically adds `cache_control` parameters to system prompts
   - Tracks and logs cache performance metrics
   - Handles both streaming and non-streaming API calls

2. Updated services to use the centralized client:
   - ResumeCustomizer now uses cache_control for all API calls
   - AISuggestions implements caching for both regular and streaming calls
   - All system prompts are structured for optimal caching efficiency

3. Comprehensive documentation in `docs/anthropic_prompt_caching.md` with:
   - Configuration options and environment variables
   - Cost savings analysis and performance benefits
   - Developer guidelines for maintaining caching efficiency

This implementation results in up to 90% cost reduction for cached tokens with estimated overall cost savings of 30-50% depending on usage patterns.

### Phase 3: Authentication Implementation ✅ COMPLETED

Implement authentication in the Next.js frontend to connect with the Flask backend.

#### Tasks

1. **Create Auth Context** ✅
   - ✅ Implement React Context for authentication state
   - ✅ Add token management
   - ✅ Create protected route wrapper

2. **Build Auth Pages** ✅
   - ✅ Create login page
   - ✅ Create registration page
   - ✅ Implement token refresh logic

3. **Connect to Backend** ✅
   - ✅ Implement API calls to authentication endpoints
   - ✅ Add token storage and management
   - ✅ Handle auth errors and redirects

#### Implementation Details

The Authentication implementation includes the following key components:

1. `AuthContext` and `AuthProvider` in `src/lib/auth-context.tsx`:
   - Manages authentication state throughout the application
   - Handles token storage and retrieval from localStorage
   - Provides login, register, logout, and token refresh functionality
   - Maintains user state and loading/error states

2. `ProtectedRoute` component in `src/components/auth/protected-route.tsx`:
   - Restricts access to authenticated routes
   - Supports admin-only routes with role-based authorization
   - Redirects to login page for unauthenticated users
   - Shows loading state during authentication checks

3. Authentication pages:
   - Login page with form validation and error handling
   - Registration page with validation and user creation
   - Both connected to backend endpoints through the auth service

4. Token management:
   - Automatic token refresh with 30-minute interval
   - Secure storage in localStorage
   - Proper token handling in API requests via Authorization header
   - Error handling for token expiration and invalid tokens

This implementation provides a complete authentication system that works with the existing Flask backend while supporting both JWT token and session-based authentication methods.

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

### Phase 4: Data Fetching Implementation ✅ COMPLETED

Connect frontend components to backend data sources using best practices for state management and error handling.

#### Tasks

1. **Data Fetching Infrastructure** ✅
   - ✅ Configure axios to include the JWT token in the Authorization header
   - ✅ Create API service functions that connect to the standardized endpoints
   - ✅ Implement React Query for data fetching and state management
   - ✅ Set up global error handling for API requests

2. **Dashboard Data Fetching** ✅
   - ✅ Connect dashboard components to API
   - ✅ Implement loading states with skeleton loaders
   - ✅ Add comprehensive error handling

3. **Resume Management** ✅
   - ✅ Connect resume upload and viewing
   - ✅ Add resume selection component
   - ✅ Implement resume deletion functionality

4. **Job Description Management** ✅
   - ✅ Connect job description input
   - ✅ Add job listing display
   - ✅ Implement job selection for customization

#### Implementation Details

The Data Fetching implementation includes the following key components:

1. Enhanced API client with Axios in `src/lib/utils.ts`:
   - Request interceptors to automatically include JWT tokens
   - Response interceptors for error handling
   - Consistent error response formatting
   - Support for file uploads and multipart/form-data

2. React Query configuration in `src/lib/react-query.ts` and `src/lib/providers.tsx`:
   - Optimized query client with caching settings
   - React Query DevTools for development
   - Global error handling for all queries
   - Query key management

3. Data fetching hooks in `src/hooks/use-api.ts`:
   - Custom hooks for all API services
   - Query invalidation for data refreshing
   - Type-safe mutation functions
   - Abstracted query state management

4. Dashboard components with real data:
   - Components for recent optimizations, statistics, saved jobs, and optimization history
   - Skeleton loaders for loading states
   - Empty states for when no data is available
   - Error states with retry functionality

5. Error handling system in `src/hooks/use-error-handler.ts`:
   - Centralized error handling hook
   - Toast notifications for errors
   - Consistent error display across components
   - Support for different error types and sources

This implementation provides a complete data management solution connecting the frontend UI components to the backend API services, with proper loading states, error handling, and data caching.

#### Prompt for Implementation

```
I need to connect my Next.js frontend components to the backend API data. I already have the UI components built (with mock data), and the standardized API endpoints exist, but I need to implement data fetching.

For the frontend data infrastructure, I need to:
1. Configure axios to include JWT tokens in the Authorization header
2. Set up React Query for data fetching and state management
3. Create API service functions for all endpoints
4. Implement global error handling for API requests

For the dashboard page specifically, I need to:
1. Connect RecentOptimizations component to real data
2. Connect StatisticsSection component to real data
3. Connect SavedJobs component to real data
4. Add loading and error states

Please provide the implementation for:
1. API client setup with authentication handling
2. React Query configuration
3. Dashboard page with real data fetching
4. Error handling and loading states
```

### Phase 5: Resume Processing Implementation ✅ COMPLETED

Implement resume upload and customization functionality.

#### Tasks

1. **Resume Upload** ✅
   - ✅ Create resume upload page
   - ✅ Implement file upload functionality
   - ✅ Add resume parsing and display

2. **Resume Customization** ✅
   - ✅ Create customization options form
   - ✅ Implement job selection
   - ✅ Add customization process with loading state

3. **Results Display** ✅
   - ✅ Create comparison view
   - ✅ Implement before/after display
   - ✅ Add export functionality

#### Implementation Details

The Resume Processing implementation includes the following key components:

1. Resume Upload Page in `src/app/resume-upload/page.tsx`:
   - Dual input methods: file upload or direct text input
   - Support for PDF, DOCX, and TXT files
   - Real-time validation and error feedback
   - Loading states during the upload process
   - Integrated with React Query for data management

2. Resume Customization Form in `src/app/resume-customization/page.tsx`:
   - Resume and job description selection dropdowns
   - Customization level options (conservative, balanced, aggressive)
   - Industry selection for context-aware optimization
   - Form validation with error handling
   - Loading state during the customization process

3. Resume Comparison Results in `src/app/resume-comparison/page.tsx`:
   - Side-by-side comparison of original and optimized resumes
   - Tabbed interface for different view modes
   - Detailed changes view with section-by-section breakdown
   - ATS score comparison with improvement metrics
   - Export functionality with multiple format options

4. Resume API Hooks in `src/hooks/use-resume-api.ts`:
   - Custom React Query hooks for all resume operations
   - Type-safe API interactions
   - Automatic cache invalidation
   - Standardized error and loading state handling

This implementation provides a complete resume processing workflow from upload through customization to results comparison, with proper error handling and loading states throughout.

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

### Phase 6: Job Management Implementation ✅ COMPLETED

Create job description input and management functionality.

#### Tasks

1. **Job Input Methods** ✅
   - ✅ Implement job URL input
   - ✅ Create job text input
   - ✅ Add job parsing and display

2. **Job Management** ✅
   - ✅ Create job listing page
   - ✅ Implement job deletion
   - ✅ Add job details view

3. **Job Selection** ✅
   - ✅ Create job selection for resume customization
   - ✅ Add job search and filtering
   - ✅ Implement job save/bookmark functionality

#### Implementation Details

The Job Management implementation includes the following key components:

1. **Job Input Page** in `src/app/(auth)/job-input/page.tsx`:
   - Dual input methods with tabbed interface:
     - URL input with validation for job description extraction
     - Direct text input with form validation
   - Loading states during submission
   - Error handling for API failures
   - Integration with toast notifications

2. **Job Management Page** in `src/app/(auth)/job-management/page.tsx`:
   - Complete job listing with sort and filter capabilities
   - Job deletion with confirmation dialog
   - Search functionality for job titles and companies
   - Empty state handling for new users
   - Responsive design for all screen sizes

3. **Job Selection Component** for resume customization:
   - Dropdown selection of available jobs
   - Job preview with key details
   - Integration with URL parameters for state persistence
   - Empty state with call-to-action to add jobs

4. **API Integration**:
   - Job URL submission with error handling
   - Job text submission with validation
   - Job listing with loading states
   - Job deletion with optimistic updates

This implementation provides a complete job management system that allows users to input, manage, and select job descriptions for resume customization, creating a seamless workflow for the job application process.

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

### Phase 7: Navigation and Layout ✅ COMPLETED

Implement site-wide navigation and layout components.

#### Tasks

1. **Navigation Structure** ✅
   - ✅ Create main navigation component
   - ✅ Implement sidebar with proper routing
   - ✅ Add mobile responsive navigation

2. **Page Layouts** ✅
   - ✅ Implement authenticated layout
   - ✅ Create public layout
   - ✅ Add page transitions

3. **User Profile** ✅
   - ✅ Create user profile page
   - ✅ Implement settings
   - ✅ Add account management

#### Implementation Details

The Navigation and Layout implementation includes the following key components:

1. **Layout Components**:
   - `AuthenticatedLayout` in `src/components/layouts/authenticated-layout.tsx`:
     - Wraps all authenticated pages with the sidebar and header
     - Uses the ProtectedRoute component for auth checks
     - Provides responsive design for all device sizes
   
   - `PublicLayout` in `src/components/layouts/public-layout.tsx`:
     - Wraps public marketing pages with header and footer
     - Responsive design for all screen sizes
     - Conditionally shows different components based on the route
   
   - `AuthPagesLayout` in `src/app/(auth-pages)/layout.tsx`:
     - Specialized layout for authentication flows
     - Split-screen design with branding and form
     - Focused UI for better conversion

2. **Navigation Components**:
   - `MainNav` in `src/components/navigation/main-nav.tsx`:
     - Adapts to authentication state
     - Provides different navigation items for auth/public
     - User profile dropdown for authenticated users
   
   - `MobileNav` in `src/components/navigation/mobile-nav.tsx`:
     - Mobile-first navigation with bottom tabs
     - Expandable drawer for additional options
     - Floating action buttons for primary actions

3. **Route Organization**:
   - Route groups for different sections:
     - `(auth)` - For authenticated pages with sidebar
     - `(public)` - For public marketing pages
     - `(auth-pages)` - For authentication flows
   
   - Comprehensive page implementation:
     - Login, register, and password reset pages
     - Settings page with various sections
     - Job management pages with all CRUD operations
     - Public features page with marketing content

4. **Responsive Design**:
   - Desktop: Full sidebar with collapsible functionality
   - Tablet: Condensed sidebar with icon-only mode
   - Mobile: Bottom navigation with drawer and FAB

This implementation provides a complete navigation structure that adapts to different authentication states and device sizes, creating a seamless user experience throughout the application.

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

### 1. Authentication Flow ✅

The system will maintain dual authentication:
- ✅ JWT tokens stored in localStorage for the Next.js frontend
- ✅ Session-based auth maintained for backward compatibility with the existing HTMX frontend

### 2. API Communication

- ✅ All frontend-backend communication will use REST API endpoints
- ✅ API responses follow a consistent format: `{ status, data, error }`
- ✅ API routes are organized in a dedicated blueprint for clarity and maintenance

### 3. Frontend Data Management ✅

- ✅ Use React Query for data fetching, caching, and state management
- ✅ Configure global axios instance with authentication interceptors
- ✅ Implement loading and error states for all data-dependent components
- ✅ Add optimistic updates for better user experience

### 4. Prompt Caching Strategy ✅

The implementation uses Anthropic's prompt caching to optimize costs:
- ✅ Separate static and dynamic content in prompts
- ✅ Use cache_control parameters for static content
- ✅ Track cache performance metrics

### 5. Error Handling ✅

- ✅ Backend implements standardized error responses
- ✅ Frontend implements:
  - ✅ Global error handling through React Query
  - ✅ Retry logic for transient failures
  - ✅ User-friendly error messages with consistent design
  - ✅ Toast notifications for errors and successes

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

1. ✅ Users can authenticate and access all features through the Next.js frontend
2. ✅ All data is correctly fetched and displayed from the backend
3. ✅ Resume customization works end-to-end with proper loading states
4. ✅ Anthropic prompt caching reduces API costs by at least 30%
5. ✅ Navigation and layouts provide a seamless user experience across devices
6. ✅ Job management features allow complete workflow for resume optimization
7. The application performs well in production-like conditions

## Post-Launch Considerations

After the initial launch, consider these enhancements:

1. **Progressive Web App** capabilities for offline support
2. **Mobile optimization** for better small-screen experience
3. **Performance profiling** for identifying bottlenecks
4. **Analytics integration** for tracking user behavior
5. **A/B testing framework** for feature optimization
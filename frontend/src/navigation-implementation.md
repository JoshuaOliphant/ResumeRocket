# ResumeRocket Navigation and Layout Implementation

This document describes the navigation and layout components implementation for the ResumeRocket Next.js application.

## Overview

The navigation and layout structure consists of:

1. **Authenticated Layout** - For pages that require user authentication
2. **Public Layout** - For public-facing pages like homepage, login, etc.
3. **Navigation Components** - Reusable components that handle desktop/mobile navigation
4. **Route Groups** - Next.js route groups for organizing pages by authentication requirements

## Component Structure

### Layout Components

1. **AuthenticatedLayout** (`/components/layouts/authenticated-layout.tsx`)
   - Wraps all authenticated pages
   - Uses ProtectedRoute component for auth checks
   - Includes desktop sidebar (collapsible)
   - Includes mobile header and navigation
   - Handles user profile display and logout

2. **PublicLayout** (`/components/layouts/public-layout.tsx`)
   - Wraps all public pages
   - Includes public header and footer
   - Displays login/register buttons
   - Shows marketing content on homepage

### Navigation Components

1. **Main Navigation** (`/components/navigation/main-nav.tsx`)
   - Primary navigation component
   - Adapts based on authentication state
   - Provides desktop menu for both auth and public states
   - Contains dropdown for user profile/settings

2. **Mobile Navigation** (`/components/navigation/mobile-nav.tsx`)
   - Mobile-specific navigation
   - Provides bottom tab bar for main navigation
   - Includes Sheet drawer for additional menu items
   - Handles FAB (Floating Action Button) for primary actions
   - Adapts based on authentication state

### Route Groups

1. **Auth Routes** (`/app/(auth)/`)
   - Dashboard page
   - Job management pages
   - Settings page
   - Resume management pages
   - All wrapped in AuthenticatedLayout

2. **Public Routes** (`/app/(public)/`)
   - Landing page
   - About/features pages
   - All wrapped in PublicLayout
   
3. **Auth Pages Routes** (`/app/(auth-pages)/`)
   - Login page
   - Registration page
   - Password reset pages
   - All wrapped in a specialized AuthPagesLayout

## Authentication Flow

1. **AuthContext** (`/lib/auth-context.tsx`)
   - Provides authentication state
   - Handles login/logout
   - Manages JWT tokens
   - Refreshes tokens automatically

2. **ProtectedRoute** (`/components/auth/protected-route.tsx`)
   - Wraps authenticated routes
   - Redirects to login if not authenticated
   - Shows loading state during auth check
   - Supports admin-only routes

## Mobile Responsiveness

- **Desktop**: Full sidebar with collapsible options
- **Tablet**: Collapsible sidebar with icon-only mode
- **Mobile**: 
  - Bottom navigation for primary actions
  - Top header for branding and user profile
  - Sheet drawer for additional menu items
  - FAB for primary create actions

## Implementation Notes

1. **Sidebar Component**: Uses Shadcn UI's sidebar component, customized for ResumeRocket
2. **Route Organization**: Uses Next.js App Router with route groups for clean separation of concerns:
   - `(auth)` - For authenticated content requiring the sidebar layout
   - `(public)` - For public marketing pages
   - `(auth-pages)` - For authentication flows with a specialized, focused layout
3. **Responsive Design**: Mobile-first approach with different navigation patterns:
   - Desktop: Full sidebar with content
   - Tablet: Collapsible sidebar with icon mode
   - Mobile: Bottom tab bar + sheet drawer for navigation
4. **User Experience**:
   - Consistent navigation patterns across the application
   - Visual indicators for active routes
   - Smooth transitions between navigation states
   - Context-aware layouts that adapt based on authentication state
5. **Theming**: Supports both light and dark modes with consistent styling
6. **Performance**: Lazy-loaded components for better performance
7. **Authentication Integration**: Navigation changes based on auth state for conditional interfaces

## Future Enhancements

1. **Breadcrumbs**: Add breadcrumbs for better navigation in nested pages
2. **Recent Items**: Add recent items in navigation for quick access
3. **User Preferences**: Allow users to customize navigation preferences
4. **Nested Navigation**: Support for nested navigation items in sidebar
5. **Search Integration**: Global search accessible from navigation
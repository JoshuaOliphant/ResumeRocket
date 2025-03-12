# ResumeRocket Component Architecture

This directory contains reusable UI components for the ResumeRocket application. The components are organized into a logical structure to make them easy to find and use.

## Directory Structure

```
templates/components/
├── resume/             # Resume-specific components
│   ├── analysis_results.html
│   ├── content_display.html
│   ├── customization_status.html
│   ├── export_options.html
│   ├── job_input.html
│   ├── optimization_details.html
│   ├── resume_input.html
│   └── section_collapsible.html
├── shared/             # Shared components used across the application
│   ├── alert.html
│   └── loading_indicator.html
└── README.md           # This file
```

## Usage Guidelines

When including components, use the following pattern:

```jinja2
{% include "components/[component-type]/[component-name].html" with context %}
```

For components that require specific variables, set them before including the component:

```jinja2
{% set category = 'success' %}
{% set message = 'Operation completed successfully' %}
{% include "components/shared/alert.html" with context %}
```

## Component Documentation

### Shared Components

#### alert.html
Displays an alert message with optional action button.

**Parameters:**
- `category`: 'success', 'error', 'warning', 'info' - Controls the color theme
- `message`: The alert message
- `back_url` (optional): URL for the action button
- `back_text` (optional): Text for the action button, defaults to "Return to Home"

#### loading_indicator.html
Displays a loading spinner with optional text.

**Parameters:**
- `message` (optional): Text to display next to the spinner
- `class` (optional): Additional CSS classes
- `text_class` (optional): CSS classes for the text and spinner color

### Resume Components

#### analysis_results.html
Displays ATS analysis results including score, keywords, and suggestions.

**Parameters:**
- `ats_score`: Object containing analysis results
- `suggestions`: List of AI suggestions
- `resume_id` (optional): ID of the resume
- `job_id` (optional): ID of the job
- `error` (optional): Error message if analysis failed

#### content_display.html
Displays a content box with title and content, useful for showing resume text.

**Parameters:**
- `title`: Title for the content box
- `content`: The content to display
- `content_id` (optional): ID for the content div
- `content_class` (optional): Additional CSS classes for the content
- `badges` (optional): List of badge objects with `text` and `class` properties

#### customization_status.html
Shows the current status of resume customization with progress indicator.

**Parameters:**
- `resume`: The resume object with status information

#### export_options.html
Dropdown menu for exporting resume in different formats.

**Parameters:**
- `resume_id`: ID of the resume to export

#### job_input.html
Input form for job description (text or URL).

**Parameters:**
- `type`: 'text' or 'url' to determine input type

#### optimization_details.html
Displays optimization details and improvements made to a resume.

**Parameters:**
- `resume`: The resume object containing optimization data
- `hidden` (optional): Boolean to control initial visibility

#### resume_input.html
Input form for resume (text or file).

**Parameters:**
- `type`: 'text' or 'file' to determine input type

#### section_collapsible.html
Collapsible section component with toggle functionality.

**Parameters:**
- `title`: Section title
- `content`: Section content
- `expanded` (optional): Boolean to control initial state (default: true)
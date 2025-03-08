# Resume Comparison Feature Implementation Plan

## Overview
This specification outlines the implementation of an enhanced resume comparison feature that displays the original and customized resumes side-by-side with visual diff highlighting. The plan includes support for markdown, DOCX, and PDF file formats, with a focus on creating an intuitive and helpful user experience.

## High-Level Architecture
1. Extract and process resume content from various formats (MD, DOCX, PDF)
2. Store both original and customized versions
3. Implement side-by-side comparison with diff highlighting
4. Provide summary of changes and interactive controls
5. Support section-by-section comparison

## Phased Implementation Plan

### Phase 1: Foundation and Markdown Support
- Set up basic comparison view layout
- Implement markdown side-by-side display
- Add basic diff highlighting
- Create summary of changes

### Phase 2: DOCX Support
- Implement DOCX parsing and conversion to structured text
- Integrate with existing comparison view

### Phase 3: PDF Support
- Implement PDF extraction using unstructured.io
- Integrate with existing comparison view

### Phase 4: UI/UX Enhancements
- Add interactive controls (toggle views, expand/collapse sections)
- Improve diff visualization
- Add analytics to track feature usage

## Detailed Implementation Steps

### Phase 1: Foundation and Markdown Support

#### Step 1.1: Set up basic comparison view template
- Create HTML/CSS template for side-by-side comparison
- Implement responsive layout
- Add placeholder for summary section

#### Step 1.2: Basic side-by-side display for Markdown
- Update the customized resume storage to keep both versions
- Modify the resume customization endpoint to return both versions
- Update the template to display both versions

#### Step 1.3: Add diff highlighting for Markdown
- Research and select a JavaScript diff library
- Implement highlighting of changes between versions
- Style the diff display for readability

#### Step 1.4: Add summary of changes
- Generate a summary of changes made to the resume
- Display count of additions, modifications, and improvements
- Add section indicators to show which parts were changed

### Phase 2: DOCX Support

#### Step 2.1: DOCX parsing and structure extraction
- Implement DOCX parsing using python-docx
- Extract structured content while preserving formatting
- Convert to markdown or HTML for comparison

#### Step 2.2: Integrate DOCX comparison with existing view
- Update the file parser to handle DOCX specifically
- Connect DOCX processing to the comparison view
- Test with various DOCX formats

### Phase 3: PDF Support

#### Step 3.1: Implement PDF extraction with unstructured.io
- Set up unstructured.io library integration
- Implement PDF content extraction with structure preservation
- Convert extracted content to markdown or HTML

#### Step 3.2: Integrate PDF comparison with existing view
- Update the file parser to handle PDF specifically
- Connect PDF processing to the comparison view
- Test with various PDF layouts

### Phase 4: UI/UX Enhancements

#### Step 4.1: Add interactive controls
- Implement view toggle options (side-by-side, original only, etc.)
- Add section collapsing/expanding functionality
- Create animation for smooth transitions

#### Step 4.2: Improve diff visualization
- Enhance color scheme and styling for better readability
- Add inline comments explaining key changes
- Implement hover effects to highlight matching changes

#### Step 4.3: Finalize and polish
- Conduct user testing
- Make adjustments based on feedback
- Add documentation and help tooltips

## Implementation Prompts

### Prompt 1: Setting up the basic template
```
Please create a Flask template for displaying original and customized resumes side by side. The template should:

1. Use Bootstrap for responsive layout
2. Have a header with a summary section
3. Divide the page into two equal columns (original and customized)
4. Include placeholders for both resume contents
5. Have a footer with action buttons
6. Be compatible with the existing application structure

The template should be saved as "templates/customized_resume_comparison.html" and inherit from the base template. Make it mobile-responsive so columns stack on smaller screens.
```

### Prompt 2: Storing and retrieving both resume versions
```
Update the resume customization endpoint to store and retrieve both the original and customized resume versions. Specifically:

1. Modify the CustomizedResume model to ensure it properly stores both the original_content and customized_content
2. Update the customize_resume_endpoint function to return both versions
3. Pass both versions to the template
4. Update the template to display both versions in their respective columns

Please ensure the database model is properly set up and the endpoint correctly handles the data flow.
```

### Prompt 3: Basic side-by-side display
```
Implement a basic side-by-side display for the resume comparison. The implementation should:

1. Take both the original and customized markdown content
2. Render both using a markdown renderer (like markdown-it or similar)
3. Display them in the two columns created earlier
4. Add a simple title and timestamp for when the customization was performed
5. Add a button to download either version

Make sure the styling looks professional and maintains the proper formatting of the resumes.
```

### Prompt 4: Adding JavaScript diff library
```
Integrate a JavaScript diff library to highlight the differences between the original and customized resumes. Please:

1. Research and recommend a suitable JavaScript diff library (like diff2html, jsdiff, or Monaco Editor)
2. Add the library to the project
3. Create a JavaScript function that takes both resume texts and highlights the differences
4. Update the template to include the necessary scripts
5. Style the diff highlighting with appropriate colors (green for additions, red for deletions, yellow for changes)

The implementation should be clean, with minimal dependencies, and should work for markdown-formatted resumes.
```

### Prompt 5: Generating a summary of changes
```
Implement a functionality to generate and display a summary of changes made to the resume. The summary should:

1. Count the number of additions, deletions, and modifications
2. Identify which sections of the resume were modified
3. Create a human-readable summary (e.g., "12 improvements made across 4 sections")
4. Display this summary at the top of the comparison page
5. Include a small badge next to each section that was changed

The implementation should analyze the diff results from the previous step to generate this information.
```

### Prompt 6: DOCX file parsing and integration
```
Implement DOCX file parsing and integration with the comparison view. The implementation should:

1. Use python-docx library to parse DOCX files
2. Extract the content while preserving structure (headings, paragraphs, lists)
3. Convert the extracted content to markdown format
4. Update the existing file parser to handle DOCX files
5. Connect this functionality to the comparison view
6. Test with various DOCX formats to ensure reliability

Ensure that the parsing preserves enough structure to make the diff meaningful.
```

### Prompt 7: PDF extraction with unstructured.io
```
Implement PDF extraction using the unstructured.io library. The implementation should:

1. Set up unstructured.io library in the project
2. Create a function to extract structured content from PDF files
3. Convert the extracted content to markdown or HTML for comparison
4. Preserve document structure (headings, paragraphs, sections)
5. Handle common resume layouts effectively
6. Update the file parser to use this for PDF files

Focus on extracting content in a way that maintains the logical structure of the resume for effective comparison.
```

### Prompt 8: Adding interactive controls
```
Implement interactive controls for the resume comparison view. The controls should include:

1. Toggle buttons to switch between different view modes:
   - Side-by-side view
   - Original only
   - Customized only
   - Unified diff view
2. Section collapsing/expanding functionality for easier navigation
3. A search function to find specific content in either version
4. Smooth animations for transitions between views
5. Button to copy the customized resume to clipboard

These controls should enhance the user experience without cluttering the interface.
```

### Prompt 9: Enhancing the diff visualization
```
Improve the diff visualization to make it more intuitive and useful. The enhancements should include:

1. Refined color scheme that's easy on the eyes and accessible
2. Inline comments or tooltips explaining key changes
3. Hover effects to highlight corresponding changes in both versions
4. Line numbers for easier reference
5. Option to toggle the level of detail in the diff
6. Small indicators in the scrollbar showing where changes are located

The goal is to make it immediately clear what has changed and why, helping users understand the improvements to their resume.
```

### Prompt 10: Final integration and testing
```
Complete the final integration and testing of the resume comparison feature. This should:

1. Ensure all components work together seamlessly
2. Add proper error handling for all edge cases
3. Implement logging for tracking usage and errors
4. Create comprehensive tests for all file formats and scenarios
5. Add user documentation and tooltips
6. Optimize performance for large resumes
7. Ensure accessibility compliance

Also, create a simple onboarding overlay that explains the feature to first-time users.
```

## Implementation Guidelines

1. **Incremental Development**: Each step builds on the previous one
2. **Testing**: Test each component thoroughly before moving to the next step
3. **User Focus**: Keep the end-user experience as the primary consideration
4. **Accessibility**: Ensure the comparison is accessible to all users
5. **Performance**: Optimize for speed, especially when handling large documents
6. **Mobile Compatibility**: Ensure the feature works well on all device sizes

## Technical Stack Recommendations

1. **Diff Visualization**: diff2html or react-diff-viewer
2. **DOCX Parsing**: python-docx
3. **PDF Extraction**: unstructured.io
4. **Frontend Framework**: Continue with existing (HTMX + Bootstrap)
5. **CSS Framework**: Bootstrap (already in use)

This plan provides a comprehensive roadmap for implementing the resume comparison feature with a focus on incremental development and user experience. 
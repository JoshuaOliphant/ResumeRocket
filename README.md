# ResumeRocket 🚀

An AI-powered resume customization tool that helps job seekers optimize their resumes for specific job descriptions.

## Features

- **ATS Analysis**: Evaluate how well your resume matches a job description
- **Smart Keyword Detection**: Identify matching and missing keywords 
- **AI-Powered Suggestions**: Get personalized recommendations to improve your resume
- **Resume Customization**: Generate tailored versions of your resume for specific job postings
- **Multiple File Formats**: Upload resumes in PDF, DOCX, or Markdown formats
- **Job URL Support**: Analyze job descriptions directly from URL
- **Feedback Loop**: Continuous improvement through user feedback and A/B testing

## Technology Stack

- **Backend**: Python, Flask
- **AI**: Anthropic Claude API for content generation
- **Frontend**: HTML, CSS, JavaScript with HTMX for dynamic interactions
- **Authentication**: Flask-Login for user management
- **Database**: SQLAlchemy with SQLite

## Getting Started

### Prerequisites

- Python 3.11+
- Anthropic API key (get one from [Anthropic Console](https://console.anthropic.com/))
- Jina AI API key (get one from [Jina AI](https://jina.ai/))

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ResumeRocket.git
   cd ResumeRocket
   ```

2. Install dependencies using uv (faster alternative to pip):
   ```
   # Install uv if not already installed
   curl -sSf https://install.ultraviolet.dev | bash
   # Install dependencies
   uv sync
   ```

3. Set up environment variables:
   
   Create a `.env` file in the root directory with the following content:
   ```
   # API Keys
   JINA_API_KEY=your_jina_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here

   # Database Configuration
   DATABASE_URL=sqlite:///resumerocket.db

   # Flask Configuration
   FLASK_SECRET_KEY=your_secret_key_here
   FLASK_ENV=development
   FLASK_DEBUG=1

   # Other Configuration
   MAX_CONTENT_LENGTH=5242880  # 5MB in bytes
   ```
   
   Replace the placeholder values with your actual API keys.

4. Run the application:
   ```
   # Make sure you're in the project root directory
   cd ResumeRocket  # adjust if necessary
   
   # Run the app
   python main.py
   ```
   
   The application automatically creates the SQLite database file in the project root directory.
   
   If you encounter any database issues, try removing the database file and letting the application recreate it:
   ```
   rm resumerocket.db  # Only if you need to reset the database
   ```

5. Open your browser and navigate to `http://localhost:8080`

   Note: The application runs on port 8080 by default to avoid conflicts with AirPlay on macOS, which uses port 5000.

## Usage

1. **Register/Login** to your account
2. **Upload your resume** via text input or file upload (PDF, DOCX, or Markdown)
3. **Provide a job description** by pasting text or entering a job URL
4. **Analyze your resume** to see ATS score and suggestions
5. **Generate a customized version** with one click
6. **Export or download** your optimized resume

## Understanding ATS Scores

ResumeRocket uses a sophisticated algorithm to evaluate how well your resume matches a specific job description. Here's how to interpret the scores:

### Score Range and Meaning

ATS scores operate on a 0-100% scale, with higher scores indicating better alignment:

- **Below 40%**: Poor match, likely to be filtered out by ATS systems
- **40-60%**: Average match, may pass initial ATS screening but not stand out
- **60-75%**: Good match, competitive for ATS systems
- **75-85%**: Excellent match, high likelihood of passing ATS screening
- **85%+**: Exceptional match, optimized for both ATS and human reviewers

### Score Improvements

After customization, the system shows the improvement from your original resume:

- **1-3%**: Minimal improvement, may not significantly impact ATS outcome
- **3-8%**: Meaningful improvement, typical range for authentic customization
- **8-15%**: Substantial improvement, significantly increases chances of ATS success
- **15%+**: Exceptional improvement, transforms a poor match into a competitive one

Note that smaller improvements (3-5%) can still make a critical difference in passing ATS thresholds, especially if they move your resume from one category to the next (e.g., from 58% to 63%).

### Section Scores

The system also evaluates individual resume sections:

- **Skills Section**: Typically weighted most heavily (1.8-2.0x), improvements here have the largest impact
- **Experience Section**: Also weighted heavily (1.5-1.6x), especially for mid-career and senior roles
- **Education Section**: More important for entry-level and academic positions (1.0-1.8x)
- **Summary Section**: Moderate weight but read first by humans (0.7-1.3x)
- **Projects/Publications**: Importance varies by job type (0.6-1.5x)

Section improvements are displayed as absolute score changes. For example, "Skills: 2.6 → 12.9 (+10.4)" indicates a nearly 5x improvement in the Skills section.

### Keyword Matching

The ATS score is heavily influenced by keyword matching:

- **Exact matches**: When your resume uses identical terms as the job description
- **Semantic matches**: When your resume uses synonyms or related terms
- **Missing keywords**: Key terms from the job description not found in your resume

The customization process identifies missing keywords that match your actual experience and incorporates them authentically. This is why improvements are typically in the 3-8% range—the system avoids "keyword stuffing" and only adds terms that reflect your real qualifications.

## Administrator Dashboard & Feedback Loop

ResumeRocket includes a powerful feedback loop system that continuously improves resume customization through user feedback and A/B testing.

### Accessing the Admin Dashboard

1. Log in with an administrator account (by default, user ID 1 is considered the admin)
2. Navigate to `/admin/feedback-loop/dashboard` in your browser (e.g., `http://localhost:5000/admin/feedback-loop/dashboard`)

### Dashboard Features

The admin dashboard provides:

- **Statistics Overview**: View metrics on total customizations, average ATS score improvements, feedback rates, and user satisfaction
- **Optimization Suggestions**: AI-generated recommendations for improving the system based on user feedback
- **A/B Testing**: Create and manage tests to compare different optimization approaches

### Using the Feedback Loop System

1. **Collecting User Feedback**: 
   - Users can provide feedback on their resume customizations through the comparison view
   - Feedback includes ratings, text comments, and outcome tracking (interviews secured, job offers)

2. **Generating Optimization Suggestions**:
   - From the admin dashboard, click "Run Optimization" to analyze user feedback
   - The system requires at least 50 feedback entries to generate meaningful insights
   - Optimization suggestions include prompt improvements, keyword strategies, and section-specific approaches

3. **Implementing A/B Tests**:
   - For each optimization suggestion, click "Create A/B Test" to test it against the current system
   - The system creates variants of the customization algorithm to test the suggestion
   - Tests run automatically for new resume customizations

4. **Analyzing Test Results**:
   - Once sufficient data is collected, click "Analyze Results" on an active test
   - The system determines the winning variant based on ATS score improvements, user ratings, and interview outcomes
   - You can then apply the winning variant to make it the new default

5. **Applying Improvements**:
   - After a test completes, the system allows you to apply the winning variant
   - This updates the AI prompts and strategies used for resume customization
   - The feedback loop continues to collect data on the improved system

## Development

### Package Management with UV

This project uses [UV](https://github.com/astral-sh/uv) instead of pip for Python package management. UV offers several advantages:

- **Significantly faster installation**: UV can install packages 10-100x faster than pip
- **Reliable dependency resolution**: Avoids dependency conflicts and ensures consistent environments
- **Performance optimized**: Uses Rust under the hood for better performance
- **Compatible with pip**: Uses the same commands and works with existing requirements

To update dependencies or add new ones:
```
uv pip install [package-name]
```

## Database Migrations

This project uses Flask-Migrate to manage database migrations. Here are the basic commands:

### Installing Flask-Migrate

First, make sure you have Flask-Migrate installed:

```bash
# Using UV (recommended for speed)
uv pip install flask-migrate

# Or using pip
pip install flask-migrate
```

### Initialize the database (first time)

```bash
flask --app app db upgrade
```

This will create all necessary tables based on the migrations.

### Creating new migrations

After making changes to your models, generate a new migration:

```bash
flask --app app db migrate -m "Description of changes"
```

Review the generated migration script in `migrations/versions/` before applying it.

### Applying migrations

To apply pending migrations:

```bash
flask --app app db upgrade
```

### Rolling back migrations

To roll back the most recent migration:

```bash
flask --app app db downgrade
```

### Getting migration status

To check the current migration status:

```bash
flask --app app db current
```

For more details on using Flask-Migrate, refer to the [official documentation](https://flask-migrate.readthedocs.io/).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Anthropic Claude API](https://www.anthropic.com/) for AI-powered text generation
- [Flask](https://flask.palletsprojects.com/) web framework
- [HTMX](https://htmx.org/) for dynamic frontend interactions
- [UV](https://github.com/astral-sh/uv) for fast Python package management
# ResumeRocket 🚀

An AI-powered resume customization tool that helps job seekers optimize their resumes for specific job descriptions.

## Features

- **ATS Analysis**: Evaluate how well your resume matches a job description
- **Smart Keyword Detection**: Identify matching and missing keywords 
- **AI-Powered Suggestions**: Get personalized recommendations to improve your resume
- **Resume Customization**: Generate tailored versions of your resume for specific job postings
- **Multiple File Formats**: Upload resumes in PDF, DOCX, or Markdown formats
- **Job URL Support**: Analyze job descriptions directly from URL

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
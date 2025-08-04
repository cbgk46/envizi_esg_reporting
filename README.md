# FastAPI Login & Questionnaire Application

A FastAPI application with user authentication and questionnaire functionality, featuring separated HTML templates and CSS for better maintainability.

## Features

- 🔐 Secure login system with session management
- 📋 Interactive questionnaire with multiple question types
- 🤖 AI-powered sustainability insights with real-time web search
- 🕷️ Spider chart visualization for sustainability dimensions
- 📊 Comprehensive sustainability maturity reports
- 🎨 Beautiful, modern UI with glassmorphism design
- 📚 Auto-generated API documentation
- ❤️ Health check endpoint
- 🚀 Easy to run and deploy
- 📁 Organized file structure with separated templates and styles

## Default User Credentials

- **Username:** `faiz`
- **Password:** `envizi`

## API Keys Required

This application requires the following API keys:

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Tavily API Key**: Get from [Tavily](https://tavily.com/) (Free tier: 1,000 searches/month)

Copy the `.env.example` file to `.env` and add your API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

## Installation

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Production Deployment

For deployment to remote servers (handles Kaleido Chrome and Playwright browser installation):

**Option 1: Using the Python setup script**
```bash
# Install Python dependencies first
pip install -r requirements.txt

# Run the deployment setup script
python setup_deployment.py

# Start the application
python main.py
```

**Option 2: Using the bash setup script (recommended)**
```bash
# Make the script executable
chmod +x setup_deployment.sh

# Run the complete setup
./setup_deployment.sh

# The script handles everything including starting instructions
```

**Option 3: Manual setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (Chromium only for production)
playwright install chromium

# Initialize Kaleido Chrome
python -c "import kaleido; kaleido.get_chrome_sync()"

# Start the application
python main.py
```

**Environment Variables for Production:**
- Set `ENVIRONMENT=production` for optimized browser installation (Chromium only)

## Usage

Once the application is running, you can access:

- **Login Page:** http://localhost:8000/ - Beautiful login form
- **Questionnaire:** http://localhost:8000/questionnaire - Survey form (requires login)
- **Success Page:** http://localhost:8000/success - Confirmation after submission
- **API Documentation:** http://localhost:8000/docs - Interactive API documentation (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc - ReDoc documentation
- **Health Check:** http://localhost:8000/health - Health status

## User Flow

1. **Login:** Visit the application and log in with the provided credentials
2. **Questionnaire:** After successful login, you'll be redirected to the questionnaire
3. **Submit:** Complete the survey and submit your responses
4. **Success:** View the confirmation page and optionally take another survey or logout

## API Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/` | GET | Redirects to login page | No |
| `/login` | GET | Login page | No |
| `/login` | POST | Handle login form | No |
| `/logout` | GET | Logout user | No |
| `/questionnaire` | GET | Questionnaire page | Yes |
| `/submit-questionnaire` | POST | Submit questionnaire | Yes |
| `/success` | GET | Success page | Yes |
| `/hello` | GET | Hello message | No |
| `/health` | GET | Health check | No |

## Questionnaire Questions

The questionnaire includes 29 questions across 8 sustainability dimensions:
1. **Sustainability Leadership** (3 questions)
2. **Organization** (2 questions)
3. **Sustainability Risk Management** (3 questions)
4. **Data & Systems** (3 questions)
5. **People & Competency** (2 questions)
6. **Direct Asset Management** (3 questions)
7. **Product Management** (4 questions)
8. **Vendor Management** (3 questions)
9. **Metrics & Reporting** (3 questions)
10. **Managing Change** (3 questions)

All questions use the standardized 5-point response scale:
- **1** - Resist - Minimal or no sustainability practices, reactive approach
- **2** - Comply - Basic regulatory compliance, limited proactive measures
- **3** - Optimize - Proactive sustainability improvements, some integration into business
- **4** - Reinvent - Sustainability as core business driver, comprehensive approach
- **5** - Lead - Industry leadership in sustainability, market shaping activities

## Security Features

- Session-based authentication using secure cookies
- Password validation
- Protected routes requiring login
- Automatic session expiration (1 hour)

## Development

The application uses:
- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server for running the application
- **python-multipart** - For handling form data
- **Jinja2** - Template engine for HTML rendering
- **Static Files** - For serving CSS and other static assets
- **Session Management** - Simple in-memory session storage

## Project Structure

```
.
├── main.py                    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── questions.json             # Questionnaire questions and responses
├── README.md                  # This file
├── static/                    # Static files directory
│   └── css/
│       └── styles.css         # All CSS styles
└── templates/                 # HTML templates directory
    ├── login.html             # Login page template
    ├── questionnaire.html     # Questionnaire page template
    └── success.html           # Success page template
```

## File Organization Benefits

- **Separation of Concerns**: HTML, CSS, and Python logic are separated
- **Maintainability**: Easier to modify styles and templates independently
- **Reusability**: CSS can be reused across multiple templates
- **Performance**: Static files are served efficiently by FastAPI
- **Scalability**: Easy to add new templates and styles

## Customization

To add more users, modify the `USERS` dictionary in `main.py`:

```python
USERS = {
    "faiz": {
        "password": "envizi",
        "name": "Faiz"
    },
    "newuser": {
        "password": "newpassword",
        "name": "New User"
    }
}
```

To modify the questionnaire, edit the `questions.json` file.

To change styles, edit `static/css/styles.css`.

To modify page layouts, edit the corresponding template in the `templates/` directory.

Enjoy your FastAPI Login & Questionnaire application! 🚀 
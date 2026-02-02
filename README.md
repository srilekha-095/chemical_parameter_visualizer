# Chemical Parameter Visualizer

A comprehensive application for visualizing and analyzing chemical equipment parameters across multiple platforms.

## Table of Contents

- [Project Description](#project-description)
- [Technology Stack](#technology-stack)
- [Architecture Overview](#architecture-overview)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [Development](#development)
- [Contributing](#contributing)

## Project Description

Chemical Parameter Visualizer is a multi-platform application designed to collect, visualize, and analyze data from chemical equipment. It provides real-time monitoring capabilities through a web interface, desktop application, and RESTful API backend.

### Features

- Real-time data visualization and monitoring
- User authentication and access control
- Data upload and import functionality
- Analytics and reporting
- Cross-platform support (Web, Desktop)

## Technology Stack

### Backend

- **Framework**: Django
- **Database**: SQLite (db.sqlite3)
- **API**: Django REST Framework
- **Language**: Python 3.x

### Frontend

- **Web**: React.js with Tailwind CSS
- **Desktop**: PyQt5
- **Build Tool**: Create React App
- **Styling**: PostCSS

### Core Technologies

- Python for backend development
- JavaScript/React for web frontend
- PyQt5 for desktop application
- SQLite for data persistence

## Architecture Overview

The application is organized into three main components:

### 1. Backend (`/backend`)

Django-based REST API server handling:
- User authentication and authorization
- Data storage and retrieval
- Analytics calculations
- CSV data import/export

**Key Modules:**
- `analytics/` - Core business logic and data models
- `backend/` - Django project configuration
- `media/` - User uploads and media files

### 2. Web Frontend (`/web-frontend`)

React-based web application providing:
- Dashboard for data visualization
- User login interface
- Real-time data monitoring
- Responsive design with Tailwind CSS

### 3. Desktop App (`/desktop-app`)

PyQt5-based desktop application for:
- Local data visualization
- API integration with backend
- Standalone usage capability

## Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://localhost:8000`

### Web Frontend Setup

1. Navigate to the web frontend directory:
   ```bash
   cd web-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```
   The app will open at `http://localhost:3000`

### Desktop App Setup

1. Navigate to the desktop app directory:
   ```bash
   cd desktop-app
   ```

2. Install PyQt5:
   ```bash
   pip install PyQt5
   ```

3. Run the application:
   ```bash
   python main.py
   ```
   Or use the batch script:
   ```bash
   run_app.bat
   ```

## Usage Guide

### Web Application

1. **Login**: Access the login page at `/login` with your credentials
2. **Dashboard**: View real-time data visualizations and analytics
3. **Upload Data**: Import CSV files for analysis

### Desktop Application

1. Launch the application using `main.py` or the batch script
2. Connect to the backend API using the API client
3. View and analyze data locally

### API Endpoints

The backend provides RESTful endpoints for:
- User authentication
- Dataset management
- Analytics queries
- Data upload/download

Access the API documentation at `http://localhost:8000/api/`

## Development

### Project Structure

```
chemical-parameter-visualizer/
├── backend/                  # Django project
│   ├── analytics/           # App with models and views
│   ├── backend/             # Project settings
│   └── manage.py
├── web-frontend/            # React application
│   ├── src/
│   ├── public/
│   └── package.json
├── desktop-app/             # PyQt5 application
│   ├── main.py
│   └── api_client.py
├── requirements.txt         # Python dependencies
└── README.md
```

### Running All Services

For full development setup, run each service in separate terminals:

```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend
cd web-frontend
npm start

# Terminal 3: Desktop App (optional)
cd desktop-app
python main.py
```

### Database

The SQLite database is located at `backend/db.sqlite3`. To reset the database:

```bash
cd backend
rm db.sqlite3
python manage.py migrate
```

## Contributing

### Guidelines

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit: `git commit -m "Description of changes"`
3. Push to the branch: `git push origin feature/your-feature`
4. Submit a pull request

### Code Standards

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React
- Write descriptive commit messages
- Include tests for new features

### Reporting Issues

Please report bugs and feature requests through the project's issue tracker.

---

**Last Updated**: February 2, 2026
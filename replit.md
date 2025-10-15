# Service Booking Platform

## Overview
This is a Flask-based web application for booking services. It allows users to browse and book services from service providers, with role-based access for users, service providers, and administrators.

## Tech Stack
- **Backend**: Python 3.11, Flask 3.0.0
- **Data Storage**: JSON-based file system (data_manager.py)
- **Forms**: Flask-WTF, WTForms
- **Authentication**: bcrypt for password hashing
- **Template Engine**: Jinja2

## Project Structure
- `app.py` - Main Flask application setup and dashboard routes
- `auth.py` - Authentication blueprint (login, register, logout)
- `services.py` - Service management blueprint
- `bookings.py` - Booking management blueprint
- `chat.py` - Chat messaging between users and providers
- `admin.py` - Admin panel blueprint
- `profile.py` - User profile management
- `data_manager.py` - JSON-based database abstraction layer
- `models.py` - Data model classes
- `forms.py` - WTForms definitions
- `config.py` - Configuration settings
- `templates/` - Jinja2 HTML templates
- `static/` - CSS and JavaScript files
- `data/` - JSON data files

## Features
- User registration and authentication with role-based access (user, service provider, admin)
- Service browsing and booking
- Real-time chat between users and service providers
- Payment processing integration
- Review and rating system
- Admin dashboard for platform management
- User and provider dashboards

## Development Setup
- Python 3.11
- Flask development server running on 0.0.0.0:5000
- Debug mode enabled for development

## Database
Uses a custom JSON-based data management system with the following tables:
- Users
- Categories
- Services
- Bookings
- Payments
- Chat_Messages
- Reviews
- Notifications
- Support_Tickets
- Platform_Metrics

## Recent Changes
- October 15, 2025: Initial Replit environment setup
  - Created requirements.txt with Flask dependencies
  - Fixed syntax errors in models.py
  - Configured Python 3.11 environment
  - Added .gitignore for Python projects

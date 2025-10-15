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

### User Features
- User registration and authentication with role-based access (user, service provider, admin)
- Service browsing and booking
- Real-time chat between users and service providers
- Payment processing (manual handling, no automated payment provider)
- Review and rating system
- User and provider dashboards

### Admin Features (Comprehensive)
- **Enhanced Dashboard**: Real-time metrics with key stats for users, bookings, revenue, and support tickets
- **Platform Configuration**: Manage platform settings (fee percentage, payment methods, terms of service, privacy policy)
- **User Management**: 
  - View, search, filter, suspend, ban, verify, and flag user accounts
  - **Edit User Details**: Full admin ability to edit name, email, contact, NID, role, status, and verification flags
  - **Password Reset**: Admin can reset any user's password securely with bcrypt hashing
  - All user actions properly CSRF protected
- **Service Management**: Approve/reject services, flag inappropriate content, edit service details, manage service status
- **Category Management**: Full CRUD operations for service categories with display ordering
- **Booking Management**: Cancel bookings with refunds, manual completion, view all bookings by status
- **Review Moderation**: Flag inappropriate reviews, delete reviews, add admin responses
- **Fraud Detection System**:
  - Duplicate account detection (by email, phone, payment method)
  - Low-rated provider monitoring (< 2.5 stars)
  - Suspicious payment pattern detection
  - Fake review account detection
  - Multiple cancellation tracking (≥ 3 cancellations)
- **Analytics & Reporting**: User stats, booking stats, revenue stats, service popularity, top providers, payment method distribution
- **Support Ticket Management**: View and update ticket status
- **Activity Logging**: Complete audit trail of all admin actions
- **Creative UI Design**: All admin pages use consistent purple-blue gradient design matching main app with glassmorphism effects

## Development Setup
- Python 3.11
- Flask development server running on 0.0.0.0:5000
- Debug mode enabled for development

## Database
Uses a custom JSON-based data management system with the following tables:
- **Users**: User accounts with authentication, roles (user/service_provider/admin), status tracking, and fraud flags
- **Categories**: Service categories with display ordering and active status
- **Services**: Service listings with approval workflow, pricing, and status management
- **Bookings**: Service bookings with status tracking and cancellation handling
- **Payments**: Manual payment records with transaction tracking
- **Chat_Messages**: Real-time messaging between users and providers
- **Reviews**: Service reviews with ratings, comments, and moderation flags
- **Notifications**: User notifications system
- **Support_Tickets**: Customer support ticket management
- **Platform_Metrics**: System-wide metrics and statistics
- **Platform_Settings**: Configurable platform settings (fee %, payment methods, terms)
- **Admin_Activity_Log**: Complete audit trail of all administrative actions

## Test Credentials
- **Admin**: admin@test.com / password123
- **Service Provider**: alice@example.com / password
- **Regular User**: john@example.com / password

## Recent Changes
- October 15, 2025: Admin Panel UI/UX Enhancement & User Management Upgrades
  - **Fixed Critical CSRF Bugs**: Resolved 400 errors on user suspend/verify/ban operations by adding proper CSRF tokens to all admin forms
  - **User Edit Functionality**: Created AdminUserEditForm and edit_user route allowing admins to modify all user details (name, email, contact, NID, role, status, verification flags)
  - **Password Reset Feature**: Added AdminPasswordResetForm and reset_user_password route for secure admin password resets with bcrypt hashing
  - **Creative UI Design Implementation**: 
    - Created base_admin.html with purple-blue gradient design matching main app's creative system
    - Updated ALL 23 admin templates to extend base_admin.html with consistent styling
    - Applied glassmorphism effects, modern cards, and creative navigation sidebar
    - Fixed CSRF tokens across all templates (settings, services, categories, bookings, reviews, fraud, analytics, support, activity log)
  - **Auth Flow Improvement**: Modified auth.py to automatically redirect admin users to admin dashboard after login
  - All changes passed architect review with no security issues

- October 15, 2025: Comprehensive Admin Panel Implementation
  - Implemented complete admin dashboard with real-time metrics and activity feeds
  - Added platform configuration system (fee %, payment methods, terms, privacy)
  - Built extensive fraud detection system (duplicate accounts, suspicious patterns, fake reviews)
  - Created user management system (view, search, suspend, ban, verify, flag)
  - Implemented service management with approval workflow and content moderation
  - Added category management with CRUD operations and display ordering
  - Built booking management with cancellation and completion capabilities
  - Created review moderation system with flagging and admin responses
  - Implemented comprehensive analytics and reporting dashboard
  - Added admin activity logging for complete audit trail
  - Created 19 admin templates with consistent UI design
  - Extended forms.py with all admin forms
  - Updated JSON data structures with new fields for admin features
  - All features passed architect review with no critical issues

- October 15, 2025: Initial Replit environment setup
  - Created requirements.txt with Flask dependencies
  - Fixed syntax errors in models.py
  - Configured Python 3.11 environment
  - Added .gitignore for Python projects

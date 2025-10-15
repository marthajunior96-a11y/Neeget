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
- October 15, 2025: **Complete Admin Interface Redesign** - World-Class UI/UX
  - **Standalone Admin Design System**:
    - Created completely new base_admin.html with professional layout, fixed sidebar navigation, and top header bar
    - Designed from scratch - no longer extends main app base template
    - Modern glassmorphism effects with animated gradient background (3 floating orbs)
    - Professional sidebar with icon navigation, collapsible sections, and smooth transitions
    - Sleek header with breadcrumbs, quick actions, user menu dropdown
  - **Custom Admin Styling (static/css/admin.css - 1000+ lines)**:
    - Professional color palette (Indigo, Purple, Success Green, Warning Orange, Danger Red)
    - Smooth animations and transitions throughout (fade-in, slide-in, hover effects)
    - Modern card designs with hover lift effects and shadow depth
    - Enhanced stat cards with gradient icons and animated number counting
    - Beautiful table design with gradient headers and row hover states
    - Modern form controls with focus states and validation styling
    - Responsive grid system for all screen sizes
    - Custom badges, buttons, and alert components
  - **Interactive JavaScript (static/js/admin.js)**:
    - Smooth sidebar toggle for mobile devices
    - Animated statistics with count-up effects
    - Custom tooltips and dropdown interactions
    - Search and filter functionality for tables
    - Auto-hiding flash messages with fade animations
    - Scroll-triggered animations for cards
    - Utility functions for currency formatting and date handling
  - **Updated Templates (21 templates)**:
    - dashboard.html - Enhanced metrics dashboard with animated stat cards and data visualization
    - users.html - Modern table design with advanced search and filtering
    - services.html, categories.html, bookings.html - Consistent card layouts with smooth transitions
    - All form pages - Modern form design with enhanced validation and styling
    - All admin templates now use consistent breadcrumbs, page headers, and modern layouts
  - **Professional Design Features**:
    - Fixed sidebar navigation (280px) with smooth hover effects
    - Sticky header (72px) with glassmorphism backdrop blur
    - Animated gradient background with floating orbs
    - Modern stat cards with gradient top borders and hover animations
    - Enhanced tables with gradient headers and interactive rows
    - Beautiful alerts with icons, smooth animations, and auto-dismiss
    - Responsive design for desktop, tablet, and mobile devices
  - **Color Scheme & Visual Appeal**:
    - Primary: Indigo gradient (#6366f1 to #4f46e5)
    - Success: Emerald gradient (#10b981 to #059669)
    - Warning: Amber gradient (#f59e0b to #d97706)
    - Danger: Red gradient (#ef4444 to #dc2626)
    - Neutral grays from 50 to 900 for perfect contrast and readability
    - All colors tested for accessibility and visual hierarchy
  - **Smooth Animations & Transitions**:
    - 0.15s fast transitions for interactions
    - 0.3s normal transitions for state changes
    - Floating orb animations (20s infinite loop)
    - Fade-in animations for content loading
    - Hover lift effects on cards and buttons
    - Slide-in animations for alerts and modals
  - Server running without errors, all CSS and JS files loaded successfully

- October 15, 2025: **Admin Controls Integration with Platform Flows** - Complete Dynamic System
  - **Authentication Security**: 
    - Login now blocks suspended/banned users with clear error messages
    - Session middleware automatically clears sessions for suspended/banned users
    - Admin users automatically redirected to admin dashboard after login
  - **Service Filtering & Management**:
    - Browse page filters to show only active services from active providers
    - Service forms show only active categories dynamically
    - Service detail pages hide flagged reviews from public view
    - Provider status checks throughout service management
  - **Booking Pipeline Security**:
    - Dynamic platform fee calculation from Platform_Settings.platform_fee_percentage
    - Dynamic payment methods loaded from Platform_Settings.payment_methods
    - User status check before allowing bookings (blocked if suspended/banned)
    - Provider status check when booking services (blocked if inactive)
    - Service status check (only active services can be booked)
  - **Admin Notification System**:
    - All admin actions create in-app notifications for affected users/providers
    - Notifications created for: suspend, ban, activate, verify, flag user operations
    - Service approval/rejection notifications sent to providers
    - Complete notification integration with Notifications table
  - **Currency Localization**:
    - Changed all currency displays from $ to ৳ (BDT Taka) across 21 template files
    - Consistent currency formatting throughout platform
  - **System-Wide Enforcement**:
    - Inactive categories filtered from all forms and listings
    - Complete status validation throughout booking pipeline
    - All changes passed architect review with no security issues

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

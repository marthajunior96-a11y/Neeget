# Service Booking Platform

## Overview
This Flask-based web application facilitates service bookings between users and service providers, featuring role-based access for users, providers, and administrators. It aims to provide a comprehensive platform for service discovery, booking, and management, including robust administrative controls and a focus on user experience and security. The platform supports dynamic content, real-time interactions, and detailed analytics to drive market potential and project ambitions.

## User Preferences
I prefer detailed explanations. Ask before making major changes. Do not make changes to the folder `Z`. Do not make changes to the file `Y`.

## System Architecture
The application is built on Python 3.11 with Flask 3.0.0.
**UI/UX Decisions:**
- **Dynamic Home Page:** Features a hero section with "Trusted by 10,000+ Users" badge, enhanced typography, upgraded search bar, and floating decorative elements. Section headers are standardized with subtitle badges, larger titles, and improved descriptions. Category and service cards are redesigned with hover effects, animated elements, and consistent visual feedback. The "How It Works" section includes large decorative step numbers and enhanced card designs. A stats section with animated number counters and interactive hover effects is included. The CTA section has improved button designs and gradient backgrounds.
- **Admin Interface:** A professional, standalone design system with `base_admin.html`, fixed sidebar navigation, and a top header bar. It utilizes modern glassmorphism effects with an animated gradient background and floating orbs. The styling (`admin.css`) includes a professional color palette, smooth animations, modern card designs, enhanced stat cards, and beautiful table designs. Interactive JavaScript (`admin.js`) provides smooth sidebar toggles, animated statistics, custom tooltips, search/filter functionality, and auto-hiding flash messages. All admin templates extend `base_admin.html` for consistent UI.
- **General UI/UX:** Extensive use of smooth transitions and animations (fade-in, slide-in, hover lift effects). Typography is carefully chosen for readability with improved font weights and line-heights. Color contrast is optimized for accessibility. Responsive design is implemented across all interfaces.

**Technical Implementations:**
- **Backend**: Python 3.11, Flask 3.0.0.
- **Data Storage**: JSON-based file system (`data_manager.py`) for data persistence.
- **Forms**: Flask-WTF and WTForms for form handling and validation.
- **Authentication**: bcrypt for secure password hashing.
- **Template Engine**: Jinja2 for dynamic content rendering.
- **Project Structure**: Modular design with blueprints for `auth`, `services`, `bookings`, `chat`, `admin`, and `profile`. `data_manager.py` handles JSON data abstraction, and `models.py` defines data structures.
- **Authentication & Authorization**: Role-based access (user, service provider, admin) with secure login, registration, and logout. Suspended/banned users are blocked from logging in, and sessions are cleared accordingly. Admin users are redirected to the admin dashboard post-login.
- **Admin Features**:
    - **Dashboard**: Real-time metrics, key stats for users, bookings, revenue, and support tickets.
    - **Platform Configuration**: Manage platform settings (fee percentage, payment methods, terms of service, privacy policy).
    - **User Management**: View, search, filter, suspend, ban, verify, flag, edit details (name, email, contact, NID, role, status, verification), and securely reset passwords using bcrypt.
    - **Service Management**: Approve/reject services, flag inappropriate content, edit details, manage status.
    - **Category Management**: Full CRUD operations with display ordering.
    - **Booking Management**: Cancel bookings with refunds, manual completion, view all bookings by status.
    - **Review Moderation**: Flag inappropriate reviews, delete, add admin responses.
    - **Fraud Detection**: Duplicate account detection, low-rated provider monitoring, suspicious payment patterns, fake review detection, multiple cancellation tracking.
    - **Analytics & Reporting**: User, booking, revenue stats; service popularity; top providers; payment method distribution.
    - **Support Ticket Management**: View and update ticket status.
    - **Activity Logging**: Audit trail of all admin actions.
- **Platform Flow Integration**: Login blocks suspended/banned users. Service browsing filters for active services/providers. Service forms dynamically show active categories. Booking pipeline checks user, provider, and service status; calculates platform fees dynamically; and loads payment methods from `Platform_Settings`.
- **Notifications**: Admin actions (suspend, ban, activate, verify, flag user; service approval/rejection) trigger in-app notifications for affected users/providers.
- **Security**: CSRF protection implemented across all forms, especially in admin functionalities for user management (suspend, verify, ban, edit, password reset).
- **Localization**: Currency display changed to ৳ (BDT Taka) with consistent formatting.

**Feature Specifications:**
- User registration and authentication.
- Service browsing and booking.
- Real-time chat between users and service providers.
- Manual payment processing.
- Review and rating system.
- User and provider dashboards.
- Comprehensive admin panel with advanced user, service, category, booking, and review management.

## External Dependencies
- Python 3.11
- Flask 3.0.0
- Flask-WTF
- WTForms
- bcrypt
- Jinja2
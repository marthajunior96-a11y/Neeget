from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, jsonify
from auth import login_required
from datetime import datetime
import json

bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_db():
    return current_app.db

def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if not g.user or g.user['role'] != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with platform metrics"""
    db = get_db()
    
    # Calculate current metrics
    users = db.get_all('Users')
    services = db.get_all('Services')
    bookings = db.get_all('Bookings')
    payments = db.get_all('Payments')
    
    total_users = len([u for u in users if u['role'] == 'user'])
    total_providers = len([u for u in users if u['role'] == 'service_provider'])
    total_bookings = len(bookings)
    
    # Calculate total revenue (completed payments)
    total_revenue = sum(p['total_amount'] for p in payments if p['payment_status'] == 'completed')
    
    # Service popularity by category
    categories = db.get_all('Service_Categories')
    service_popularity = {}
    for category in categories:
        category_services = [s for s in services if s['category_id'] == category['id']]
        category_bookings = 0
        for service in category_services:
            category_bookings += len([b for b in bookings if b['service_id'] == service['id']])
        service_popularity[category['category_name']] = category_bookings
    
    # Recent activity
    recent_bookings = sorted(bookings, key=lambda x: x.get('booking_date', ''), reverse=True)[:10]
    recent_users = sorted(users, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
    
    # Support tickets
    support_tickets = db.get_all('Support_Tickets')
    open_tickets = [t for t in support_tickets if t['status'] == 'open']
    
    metrics = {
        'total_users': total_users,
        'total_providers': total_providers,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'service_popularity': service_popularity,
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'open_tickets': len(open_tickets)
    }
    
    return render_template('admin/dashboard.html', metrics=metrics)

@bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users and providers"""
    db = get_db()
    users = db.get_all('Users')
    
    # Filter by role if specified
    role_filter = request.args.get('role')
    if role_filter:
        users = [u for u in users if u['role'] == role_filter]
    
    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_user(user_id):
    """Suspend a user"""
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    if user['role'] == 'admin':
        flash('Cannot suspend admin users.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        db.update('Users', user_id, {'status': 'suspended'})
        flash(f'User {user["name"]} has been suspended.', 'success')
    except Exception as e:
        flash(f'Error suspending user: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/users/<int:user_id>/ban', methods=['POST'])
@login_required
@admin_required
def ban_user(user_id):
    """Ban a user"""
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    if user['role'] == 'admin':
        flash('Cannot ban admin users.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        db.update('Users', user_id, {'status': 'banned'})
        flash(f'User {user["name"]} has been banned.', 'success')
    except Exception as e:
        flash(f'Error banning user: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/users/<int:user_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_user(user_id):
    """Activate a user"""
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        db.update('Users', user_id, {'status': 'active'})
        flash(f'User {user["name"]} has been activated.', 'success')
    except Exception as e:
        flash(f'Error activating user: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/users/<int:user_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_user(user_id):
    """Verify a user's email and NID"""
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        db.update('Users', user_id, {
            'email_verified': True,
            'nid_verified': True
        })
        flash(f'User {user["name"]} has been verified.', 'success')
    except Exception as e:
        flash(f'Error verifying user: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/support')
@login_required
@admin_required
def support_tickets():
    """Manage support tickets"""
    db = get_db()
    tickets = db.get_all('Support_Tickets')
    
    # Sort by created_at (newest first)
    tickets.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Enrich with user information
    for ticket in tickets:
        user = db.get_by_id('Users', ticket.get('user_id'))
        ticket['user'] = user
    
    return render_template('admin/support.html', tickets=tickets)

@bp.route('/support/<int:ticket_id>/update', methods=['POST'])
@login_required
@admin_required
def update_ticket_status(ticket_id):
    """Update support ticket status"""
    db = get_db()
    ticket = db.get_by_id('Support_Tickets', ticket_id)
    
    if not ticket:
        flash('Ticket not found.', 'error')
        return redirect(url_for('admin.support_tickets'))
    
    new_status = request.form.get('status')
    if new_status not in ['open', 'in_progress', 'resolved', 'closed']:
        flash('Invalid status.', 'error')
        return redirect(url_for('admin.support_tickets'))
    
    try:
        db.update('Support_Tickets', ticket_id, {
            'status': new_status,
            'updated_at': datetime.now().isoformat()
        })
        
        # Notify user
        db.add('Notifications', {
            'user_id': ticket['user_id'],
            'notification_type': 'in_app',
            'message': f'Your support ticket status has been updated to: {new_status}'
        })
        
        flash('Ticket status updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating ticket: {str(e)}', 'error')
    
    return redirect(url_for('admin.support_tickets'))

@bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """View detailed analytics"""
    db = get_db()
    
    # Get all data
    users = db.get_all('Users')
    services = db.get_all('Services')
    bookings = db.get_all('Bookings')
    payments = db.get_all('Payments')
    categories = db.get_all('Service_Categories')
    
    # User analytics
    user_stats = {
        'total_users': len([u for u in users if u['role'] == 'user']),
        'total_providers': len([u for u in users if u['role'] == 'service_provider']),
        'verified_users': len([u for u in users if u.get('email_verified', False)]),
        'active_users': len([u for u in users if u.get('status') == 'active'])
    }
    
    # Booking analytics
    booking_stats = {
        'total_bookings': len(bookings),
        'pending_bookings': len([b for b in bookings if b['booking_status'] == 'pending']),
        'completed_bookings': len([b for b in bookings if b['booking_status'] == 'completed']),
        'cancelled_bookings': len([b for b in bookings if b['booking_status'] == 'cancelled'])
    }
    
    # Revenue analytics
    revenue_stats = {
        'total_revenue': sum(p['total_amount'] for p in payments if p['payment_status'] == 'completed'),
        'platform_fees': sum(p['platform_fee'] for p in payments if p['payment_status'] == 'completed'),
        'pending_payments': sum(p['total_amount'] for p in payments if p['payment_status'] == 'pending')
    }
    
    # Service popularity
    service_popularity = {}
    for category in categories:
        category_services = [s for s in services if s['category_id'] == category['id']]
        category_bookings = 0
        for service in category_services:
            category_bookings += len([b for b in bookings if b['service_id'] == service['id']])
        service_popularity[category['category_name']] = category_bookings
    
    analytics_data = {
        'user_stats': user_stats,
        'booking_stats': booking_stats,
        'revenue_stats': revenue_stats,
        'service_popularity': service_popularity
    }
    
    # Save to Platform_Metrics
    try:
        db.add('Platform_Metrics', {
            'total_users': user_stats['total_users'],
            'total_providers': user_stats['total_providers'],
            'total_bookings': booking_stats['total_bookings'],
            'total_revenue': revenue_stats['total_revenue'],
            'service_popularity': json.dumps(service_popularity),
            'recorded_at': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error saving metrics: {e}")
    
    return render_template('admin/analytics.html', analytics=analytics_data)

@bp.route('/fraud')
@login_required
@admin_required
def fraud_monitoring():
    """Monitor for fraudulent activity"""
    db = get_db()
    
    # Get users with low ratings or multiple complaints
    reviews = db.get_all('Reviews')
    users = db.get_all('Users')
    
    # Calculate average ratings for providers
    provider_ratings = {}
    for review in reviews:
        provider_id = review['provider_id']
        if provider_id not in provider_ratings:
            provider_ratings[provider_id] = []
        provider_ratings[provider_id].append(review['rating'])
    
    # Find providers with low average ratings
    flagged_providers = []
    for provider_id, ratings in provider_ratings.items():
        avg_rating = sum(ratings) / len(ratings)
        if avg_rating < 2.5 and len(ratings) >= 3:  # Low rating with at least 3 reviews
            provider = db.get_by_id('Users', provider_id)
            if provider:
                provider['avg_rating'] = avg_rating
                provider['review_count'] = len(ratings)
                flagged_providers.append(provider)
    
    # Find users with multiple cancelled bookings
    bookings = db.get_all('Bookings')
    user_cancellations = {}
    for booking in bookings:
        if booking['booking_status'] == 'cancelled':
            user_id = booking['user_id']
            user_cancellations[user_id] = user_cancellations.get(user_id, 0) + 1
    
    flagged_users = []
    for user_id, cancellation_count in user_cancellations.items():
        if cancellation_count >= 3:  # 3 or more cancellations
            user = db.get_by_id('Users', user_id)
            if user:
                user['cancellation_count'] = cancellation_count
                flagged_users.append(user)
    
    return render_template('admin/fraud.html', 
                         flagged_providers=flagged_providers, 
                         flagged_users=flagged_users)


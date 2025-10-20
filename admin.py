from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, jsonify
from auth import login_required
from datetime import datetime
from forms import PlatformSettingForm, CategoryForm, ServiceEditForm, FlagForm, AdminNoteForm, ReviewModerationForm
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

def log_admin_activity(admin_id, action_type, target_type, target_id, details):
    """Log admin activity for audit trail"""
    try:
        db = get_db()
        db.add('Admin_Activity_Log', {
            'admin_id': admin_id,
            'action_type': action_type,
            'target_type': target_type,
            'target_id': target_id,
            'details': json.dumps(details),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error logging admin activity: {e}")

# ========== DASHBOARD ==========

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Enhanced admin dashboard with comprehensive metrics"""
    db = get_db()
    
    # Get all data
    users = db.get_all('Users')
    services = db.get_all('Services')
    bookings = db.get_all('Bookings')
    payments = db.get_all('Payments')
    support_tickets = db.get_all('Support_Tickets')
    categories = db.get_all('Service_Categories')
    
    # User metrics
    total_users = len([u for u in users if u['role'] == 'user'])
    total_providers = len([u for u in users if u['role'] == 'service_provider'])
    verified_users = len([u for u in users if u.get('email_verified', False)])
    flagged_accounts = len([u for u in users if u.get('is_flagged', False)])
    
    # Service metrics
    total_services = len(services)
    active_services = len([s for s in services if s.get('status') == 'active'])
    pending_services = len([s for s in services if s.get('status') == 'pending_approval'])
    flagged_services = len([s for s in services if s.get('status') == 'flagged'])
    
    # Booking metrics
    total_bookings = len(bookings)
    pending_bookings = len([b for b in bookings if b['booking_status'] == 'pending'])
    completed_bookings = len([b for b in bookings if b['booking_status'] == 'completed'])
    cancelled_bookings = len([b for b in bookings if b['booking_status'] == 'cancelled'])
    
    # Financial metrics
    total_revenue = sum(p['total_amount'] for p in payments if p['payment_status'] == 'completed')
    platform_fees = sum(p['platform_fee'] for p in payments if p['payment_status'] == 'completed')
    pending_payments = sum(p['total_amount'] for p in payments if p['payment_status'] == 'pending')
    
    # Support metrics
    open_tickets = len([t for t in support_tickets if t['status'] == 'open'])
    
    # Recent activity
    recent_users = sorted(users, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
    recent_bookings = sorted(bookings, key=lambda x: x.get('booking_date', ''), reverse=True)[:10]
    recent_payments = sorted([p for p in payments if p['payment_status'] == 'completed'], 
                            key=lambda x: x.get('payment_date', ''), reverse=True)[:10]
    
    # Service popularity
    service_popularity = {}
    for category in categories:
        if category.get('is_active', True):
            category_services = [s for s in services if s['category_id'] == category['id']]
            category_bookings = 0
            for service in category_services:
                category_bookings += len([b for b in bookings if b['service_id'] == service['id']])
            service_popularity[category['category_name']] = category_bookings
    
    metrics = {
        'total_users': total_users,
        'total_providers': total_providers,
        'verified_users': verified_users,
        'flagged_accounts': flagged_accounts,
        'total_services': total_services,
        'active_services': active_services,
        'pending_services': pending_services,
        'flagged_services': flagged_services,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': round(total_revenue, 2),
        'platform_fees': round(platform_fees, 2),
        'pending_payments': round(pending_payments, 2),
        'open_tickets': open_tickets,
        'recent_users': recent_users[:5],
        'recent_bookings': recent_bookings[:5],
        'recent_payments': recent_payments[:5],
        'service_popularity': service_popularity
    }
    
    return render_template('admin/dashboard.html', metrics=metrics)

# ========== PLATFORM SETTINGS ==========

@bp.route('/settings')
@login_required
@admin_required
def settings():
    """View and manage platform settings"""
    db = get_db()
    all_settings = db.get_all('Platform_Settings')
    return render_template('admin/settings.html', settings=all_settings)

@bp.route('/settings/<int:setting_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_setting(setting_id):
    """Edit platform setting"""
    db = get_db()
    setting = db.get_by_id('Platform_Settings', setting_id)
    
    if not setting:
        flash('Setting not found.', 'error')
        return redirect(url_for('admin.settings'))
    
    form = PlatformSettingForm()
    
    if form.validate_on_submit():
        try:
            old_value = setting['setting_value']
            db.update('Platform_Settings', setting_id, {
                'setting_value': form.setting_value.data,
                'updated_at': datetime.now().isoformat(),
                'updated_by': g.user['id']
            })
            
            log_admin_activity(
                g.user['id'],
                'setting_update',
                'platform_setting',
                setting_id,
                {
                    'setting_key': setting['setting_key'],
                    'old_value': old_value,
                    'new_value': form.setting_value.data
                }
            )
            
            flash(f'Setting "{setting["setting_key"]}" updated successfully!', 'success')
            return redirect(url_for('admin.settings'))
        except Exception as e:
            flash(f'Error updating setting: {str(e)}', 'error')
    else:
        form.setting_value.data = setting['setting_value']
    
    return render_template('admin/edit_setting.html', form=form, setting=setting)

# ========== USER MANAGEMENT ==========

@bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users with advanced filtering"""
    db = get_db()
    users = db.get_all('Users')
    
    # Apply filters
    role_filter = request.args.get('role')
    status_filter = request.args.get('status')
    verified_filter = request.args.get('verified')
    flagged_filter = request.args.get('flagged')
    search_query = request.args.get('search', '').lower()
    
    if role_filter:
        users = [u for u in users if u['role'] == role_filter]
    
    if status_filter:
        users = [u for u in users if u.get('status') == status_filter]
    
    if verified_filter == 'yes':
        users = [u for u in users if u.get('email_verified', False)]
    elif verified_filter == 'no':
        users = [u for u in users if not u.get('email_verified', False)]
    
    if flagged_filter == 'yes':
        users = [u for u in users if u.get('is_flagged', False)]
    
    if search_query:
        users = [u for u in users if search_query in u.get('name', '').lower() or 
                                     search_query in u.get('email', '').lower() or
                                     search_query in str(u.get('id', ''))]
    
    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View detailed user profile"""
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    # Get user's bookings and reviews
    bookings = db.find_by_attribute('Bookings', 'user_id', user_id)
    reviews = db.find_by_attribute('Reviews', 'user_id', user_id)
    
    # If provider, get services and earnings
    services = []
    earnings = 0
    if user['role'] == 'service_provider':
        services = db.find_by_attribute('Services', 'provider_id', user_id)
        provider_bookings = db.find_by_attribute('Bookings', 'provider_id', user_id)
        for booking in provider_bookings:
            if booking['booking_status'] == 'completed':
                service = db.get_by_id('Services', booking['service_id'])
                if service:
                    earnings += service['price']
    
    return render_template('admin/user_detail.html', user=user, bookings=bookings, 
                          reviews=reviews, services=services, earnings=round(earnings, 2))

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details"""
    from forms import AdminUserEditForm
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    form = AdminUserEditForm()
    
    if form.validate_on_submit():
        try:
            update_data = {
                'name': form.name.data,
                'email': form.email.data,
                'contact_number': form.contact_number.data,
                'nid_number': form.nid_number.data,
                'role': form.role.data,
                'status': form.status.data,
                'email_verified': form.email_verified.data,
                'nid_verified': form.nid_verified.data
            }
            db.update('Users', user_id, update_data)
            log_admin_activity(g.user['id'], 'user_edit', 'user', user_id, 
                             {'user_name': user['name'], 'changes': update_data})
            flash(f'User {form.name.data} has been updated successfully.', 'success')
            return redirect(url_for('admin.user_detail', user_id=user_id))
        except Exception as e:
            flash(f'Error updating user: {str(e)}', 'error')
    
    # Pre-populate form
    if request.method == 'GET':
        form.name.data = user.get('name')
        form.email.data = user.get('email')
        form.contact_number.data = user.get('contact_number')
        form.nid_number.data = user.get('nid_number')
        form.role.data = user.get('role')
        form.status.data = user.get('status', 'active')
        form.email_verified.data = user.get('email_verified', False)
        form.nid_verified.data = user.get('nid_verified', False)
    
    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset user password"""
    from forms import AdminPasswordResetForm
    import bcrypt
    
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    form = AdminPasswordResetForm()
    
    if form.validate_on_submit():
        if form.new_password.data != form.confirm_password.data:
            flash('Passwords do not match.', 'error')
        else:
            try:
                hashed_password = bcrypt.hashpw(form.new_password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.update('Users', user_id, {'password_hash': hashed_password})
                log_admin_activity(g.user['id'], 'user_password_reset', 'user', user_id, 
                                 {'user_name': user['name']})
                flash(f'Password for {user["name"]} has been reset successfully.', 'success')
                return redirect(url_for('admin.user_detail', user_id=user_id))
            except Exception as e:
                flash(f'Error resetting password: {str(e)}', 'error')
    
    return render_template('admin/reset_password.html', form=form, user=user)


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
        log_admin_activity(g.user['id'], 'user_suspend', 'user', user_id, {'user_name': user['name']})
        db.add('Notifications', {
            'user_id': user_id,
            'notification_type': 'in_app',
            'message': f'Your account has been suspended. Please contact support for more information.'
        })
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
        log_admin_activity(g.user['id'], 'user_ban', 'user', user_id, {'user_name': user['name']})
        db.add('Notifications', {
            'user_id': user_id,
            'notification_type': 'in_app',
            'message': f'Your account has been banned from this platform.'
        })
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
        log_admin_activity(g.user['id'], 'user_activate', 'user', user_id, {'user_name': user['name']})
        db.add('Notifications', {
            'user_id': user_id,
            'notification_type': 'in_app',
            'message': f'Your account has been activated. You can now use all platform features.'
        })
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
        log_admin_activity(g.user['id'], 'user_verify', 'user', user_id, {'user_name': user['name']})
        db.add('Notifications', {
            'user_id': user_id,
            'notification_type': 'in_app',
            'message': f'Congratulations! Your account has been verified.'
        })
        flash(f'User {user["name"]} has been verified.', 'success')
    except Exception as e:
        flash(f'Error verifying user: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/users/<int:user_id>/flag', methods=['GET', 'POST'])
@login_required
@admin_required
def flag_user(user_id):
    """Flag a suspicious user"""
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    form = FlagForm()
    
    if form.validate_on_submit():
        try:
            db.update('Users', user_id, {
                'is_flagged': True,
                'flagged_reason': form.reason.data,
                'flagged_date': datetime.now().isoformat(),
                'investigation_status': 'investigating'
            })
            log_admin_activity(g.user['id'], 'user_flag', 'user', user_id, 
                             {'user_name': user['name'], 'reason': form.reason.data})
            db.add('Notifications', {
                'user_id': user_id,
                'notification_type': 'in_app',
                'message': f'Your account has been flagged for review. Our team will investigate and contact you if needed.'
            })
            flash(f'User {user["name"]} has been flagged for investigation.', 'success')
            return redirect(url_for('admin.user_detail', user_id=user_id))
        except Exception as e:
            flash(f'Error flagging user: {str(e)}', 'error')
    
    return render_template('admin/flag_user.html', form=form, user=user)

@bp.route('/users/<int:user_id>/unflag', methods=['POST'])
@login_required
@admin_required
def unflag_user(user_id):
    """Remove flag from user"""
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        db.update('Users', user_id, {
            'is_flagged': False,
            'flagged_reason': None,
            'investigation_status': 'cleared'
        })
        log_admin_activity(g.user['id'], 'user_unflag', 'user', user_id, {'user_name': user['name']})
        flash(f'Flag removed from user {user["name"]}.', 'success')
    except Exception as e:
        flash(f'Error unflagging user: {str(e)}', 'error')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    db = get_db()
    user = db.get_by_id('Users', user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    if user['role'] == 'admin':
        flash('Cannot delete admin users.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        user_name = user['name']
        db.delete('Users', user_id)
        log_admin_activity(g.user['id'], 'user_delete', 'user', user_id, {'user_name': user_name})
        flash(f'User {user_name} has been deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

# ========== SERVICE MANAGEMENT ==========

@bp.route('/services')
@login_required
@admin_required
def manage_services():
    """Manage services with filtering"""
    db = get_db()
    services = db.get_all('Services')
    categories = db.get_all('Service_Categories')
    
    # Apply filters
    category_filter = request.args.get('category')
    status_filter = request.args.get('status')
    search_query = request.args.get('search', '').lower()
    
    if category_filter:
        services = [s for s in services if s.get('category_id') == int(category_filter)]
    
    if status_filter:
        services = [s for s in services if s.get('status') == status_filter]
    
    if search_query:
        services = [s for s in services if search_query in s.get('service_name', '').lower()]
    
    # Enrich with provider info
    for service in services:
        provider = db.get_by_id('Users', service.get('provider_id'))
        category = db.get_by_id('Service_Categories', service.get('category_id'))
        service['provider_name'] = provider.get('name') if provider else 'Unknown'
        service['category_name'] = category.get('category_name') if category else 'Unknown'
    
    return render_template('admin/services.html', services=services, categories=categories)

@bp.route('/services/<int:service_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_service(service_id):
    """Approve a service"""
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('admin.manage_services'))
    
    try:
        db.update('Services', service_id, {'status': 'active'})
        log_admin_activity(g.user['id'], 'service_approve', 'service', service_id, 
                         {'service_name': service['service_name']})
        flash(f'Service "{service["service_name"]}" has been approved.', 'success')
    except Exception as e:
        flash(f'Error approving service: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_services'))

@bp.route('/services/<int:service_id>/flag', methods=['GET', 'POST'])
@login_required
@admin_required
def flag_service(service_id):
    """Flag inappropriate service"""
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('admin.manage_services'))
    
    form = FlagForm()
    
    if form.validate_on_submit():
        try:
            db.update('Services', service_id, {
                'status': 'flagged',
                'flagged_reason': form.reason.data
            })
            log_admin_activity(g.user['id'], 'service_flag', 'service', service_id,
                             {'service_name': service['service_name'], 'reason': form.reason.data})
            db.add('Notifications', {
                'user_id': service['provider_id'],
                'notification_type': 'in_app',
                'message': f'Your service "{service["service_name"]}" has been flagged for review. Reason: {form.reason.data}'
            })
            flash(f'Service "{service["service_name"]}" has been flagged.', 'success')
            return redirect(url_for('admin.manage_services'))
        except Exception as e:
            flash(f'Error flagging service: {str(e)}', 'error')
    
    return render_template('admin/flag_service.html', form=form, service=service)

@bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_service(service_id):
    """Edit service details"""
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('admin.manage_services'))
    
    form = ServiceEditForm()
    
    if form.validate_on_submit():
        try:
            db.update('Services', service_id, {
                'service_name': form.service_name.data,
                'description': form.description.data,
                'price': float(form.price.data),
                'location': form.location.data,
                'status': form.status.data
            })
            log_admin_activity(g.user['id'], 'service_edit', 'service', service_id,
                             {'service_name': form.service_name.data})
            flash(f'Service "{form.service_name.data}" updated successfully!', 'success')
            return redirect(url_for('admin.manage_services'))
        except Exception as e:
            flash(f'Error updating service: {str(e)}', 'error')
    else:
        form.service_name.data = service['service_name']
        form.description.data = service.get('description')
        form.price.data = service['price']
        form.location.data = service.get('location')
        form.status.data = service.get('status', 'pending_approval')
    
    return render_template('admin/edit_service.html', form=form, service=service)

@bp.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_service(service_id):
    """Delete a service"""
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('admin.manage_services'))
    
    try:
        service_name = service['service_name']
        db.delete('Services', service_id)
        log_admin_activity(g.user['id'], 'service_delete', 'service', service_id,
                         {'service_name': service_name})
        flash(f'Service "{service_name}" has been deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting service: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_services'))

# ========== CATEGORY MANAGEMENT ==========

@bp.route('/categories')
@login_required
@admin_required
def manage_categories():
    """Manage service categories"""
    db = get_db()
    all_categories = db.get_all('Service_Categories')
    
    # Separate pending requests from approved categories
    pending_requests = [c for c in all_categories if c.get('status') == 'pending_approval']
    categories = [c for c in all_categories if c.get('status') != 'pending_approval']
    
    # Sort by display order
    categories.sort(key=lambda x: x.get('display_order', 999))
    pending_requests.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Count services in each category
    all_services = db.get_all('Services')
    for category in categories:
        category['service_count'] = len([s for s in all_services if s['category_id'] == category['id']])
    
    # Get requester info for pending requests
    for request in pending_requests:
        requester = db.get_by_id('Users', request.get('requested_by'))
        request['requester_name'] = requester['name'] if requester else 'Unknown'
    
    return render_template('admin/categories.html', categories=categories, pending_requests=pending_requests)

@bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Add new category"""
    db = get_db()
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            category = db.add('Service_Categories', {
                'category_name': form.category_name.data,
                'description': form.description.data,
                'is_active': form.is_active.data,
                'display_order': form.display_order.data or 999
            })
            log_admin_activity(g.user['id'], 'category_add', 'category', category['id'],
                             {'category_name': form.category_name.data})
            flash(f'Category "{form.category_name.data}" added successfully!', 'success')
            return redirect(url_for('admin.manage_categories'))
        except Exception as e:
            flash(f'Error adding category: {str(e)}', 'error')
    
    return render_template('admin/add_category.html', form=form)

@bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """Edit category"""
    db = get_db()
    category = db.get_by_id('Service_Categories', category_id)
    
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin.manage_categories'))
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            db.update('Service_Categories', category_id, {
                'category_name': form.category_name.data,
                'description': form.description.data,
                'is_active': form.is_active.data,
                'display_order': form.display_order.data or 999
            })
            log_admin_activity(g.user['id'], 'category_edit', 'category', category_id,
                             {'category_name': form.category_name.data})
            flash(f'Category "{form.category_name.data}" updated successfully!', 'success')
            return redirect(url_for('admin.manage_categories'))
        except Exception as e:
            flash(f'Error updating category: {str(e)}', 'error')
    else:
        form.category_name.data = category['category_name']
        form.description.data = category.get('description')
        form.is_active.data = category.get('is_active', True)
        form.display_order.data = category.get('display_order')
    
    return render_template('admin/edit_category.html', form=form, category=category)

@bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """Delete category"""
    db = get_db()
    category = db.get_by_id('Service_Categories', category_id)
    
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin.manage_categories'))
    
    # Check if category has services
    services = db.find_by_attribute('Services', 'category_id', category_id)
    if services:
        flash(f'Cannot delete category "{category["category_name"]}" because it has {len(services)} service(s). Please reassign or delete those services first.', 'error')
        return redirect(url_for('admin.manage_categories'))
    
    try:
        category_name = category['category_name']
        db.delete('Service_Categories', category_id)
        log_admin_activity(g.user['id'], 'category_delete', 'category', category_id,
                         {'category_name': category_name})
        flash(f'Category "{category_name}" has been deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_categories'))

# ========== BOOKING MANAGEMENT ==========

@bp.route('/bookings')
@login_required
@admin_required
def manage_bookings():
    """Manage all bookings"""
    db = get_db()
    bookings = db.get_all('Bookings')
    
    # Apply filters
    status_filter = request.args.get('status')
    search_query = request.args.get('search', '')
    
    if status_filter:
        bookings = [b for b in bookings if b['booking_status'] == status_filter]
    
    if search_query:
        bookings = [b for b in bookings if search_query in str(b.get('id', ''))]
    
    # Enrich with user and service info
    for booking in bookings:
        user = db.get_by_id('Users', booking['user_id'])
        provider = db.get_by_id('Users', booking['provider_id'])
        service = db.get_by_id('Services', booking['service_id'])
        booking['user_name'] = user.get('name') if user else 'Unknown'
        booking['provider_name'] = provider.get('name') if provider else 'Unknown'
        booking['service_name'] = service.get('service_name') if service else 'Unknown'
    
    # Sort by booking date (newest first)
    bookings.sort(key=lambda x: x.get('booking_date', ''), reverse=True)
    
    return render_template('admin/bookings.html', bookings=bookings)

@bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('admin.manage_bookings'))
    
    try:
        db.update('Bookings', booking_id, {'booking_status': 'cancelled'})
        
        # Update payment if exists
        payments = db.find_by_attribute('Payments', 'booking_id', booking_id)
        if payments:
            db.update('Payments', payments[0]['id'], {'payment_status': 'refunded'})
        
        # Notify user and provider
        db.add('Notifications', {
            'user_id': booking['user_id'],
            'notification_type': 'in_app',
            'message': f'Your booking #{booking_id} has been cancelled by admin.'
        })
        
        log_admin_activity(g.user['id'], 'booking_cancel', 'booking', booking_id, {})
        flash('Booking cancelled successfully.', 'success')
    except Exception as e:
        flash(f'Error cancelling booking: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_bookings'))

@bp.route('/bookings/<int:booking_id>/complete', methods=['POST'])
@login_required
@admin_required
def complete_booking(booking_id):
    """Mark booking as completed"""
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('admin.manage_bookings'))
    
    try:
        db.update('Bookings', booking_id, {'booking_status': 'completed'})
        log_admin_activity(g.user['id'], 'booking_complete', 'booking', booking_id, {})
        flash('Booking marked as completed.', 'success')
    except Exception as e:
        flash(f'Error completing booking: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_bookings'))

# ========== REVIEW MODERATION ==========

@bp.route('/reviews')
@login_required
@admin_required
def manage_reviews():
    """Manage reviews"""
    db = get_db()
    reviews = db.get_all('Reviews')
    
    # Apply filters
    rating_filter = request.args.get('rating')
    flagged_filter = request.args.get('flagged')
    
    if rating_filter:
        reviews = [r for r in reviews if r['rating'] == int(rating_filter)]
    
    if flagged_filter == 'yes':
        reviews = [r for r in reviews if r.get('is_flagged', False)]
    
    # Enrich with user and provider info
    for review in reviews:
        user = db.get_by_id('Users', review['user_id'])
        provider = db.get_by_id('Users', review['provider_id'])
        review['user_name'] = user.get('name') if user else 'Unknown'
        review['provider_name'] = provider.get('name') if provider else 'Unknown'
    
    reviews.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('admin/reviews.html', reviews=reviews)

@bp.route('/reviews/<int:review_id>/flag', methods=['GET', 'POST'])
@login_required
@admin_required
def flag_review(review_id):
    """Flag inappropriate review"""
    db = get_db()
    review = db.get_by_id('Reviews', review_id)
    
    if not review:
        flash('Review not found.', 'error')
        return redirect(url_for('admin.manage_reviews'))
    
    form = FlagForm()
    
    if form.validate_on_submit():
        try:
            db.update('Reviews', review_id, {
                'is_flagged': True,
                'flagged_reason': form.reason.data
            })
            log_admin_activity(g.user['id'], 'review_flag', 'review', review_id,
                             {'reason': form.reason.data})
            flash('Review has been flagged.', 'success')
            return redirect(url_for('admin.manage_reviews'))
        except Exception as e:
            flash(f'Error flagging review: {str(e)}', 'error')
    
    return render_template('admin/flag_review.html', form=form, review=review)

@bp.route('/reviews/<int:review_id>/unflag', methods=['POST'])
@login_required
@admin_required
def unflag_review(review_id):
    """Unflag review"""
    db = get_db()
    review = db.get_by_id('Reviews', review_id)
    
    if not review:
        flash('Review not found.', 'error')
        return redirect(url_for('admin.manage_reviews'))
    
    try:
        db.update('Reviews', review_id, {
            'is_flagged': False,
            'flagged_reason': None
        })
        log_admin_activity(g.user['id'], 'review_unflag', 'review', review_id, {})
        flash('Review flag removed.', 'success')
    except Exception as e:
        flash(f'Error unflagging review: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_reviews'))

@bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(review_id):
    """Delete fake/abusive review"""
    db = get_db()
    review = db.get_by_id('Reviews', review_id)
    
    if not review:
        flash('Review not found.', 'error')
        return redirect(url_for('admin.manage_reviews'))
    
    try:
        db.delete('Reviews', review_id)
        log_admin_activity(g.user['id'], 'review_delete', 'review', review_id, {})
        flash('Review has been deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting review: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_reviews'))

@bp.route('/reviews/<int:review_id>/respond', methods=['GET', 'POST'])
@login_required
@admin_required
def respond_to_review(review_id):
    """Add admin response to review"""
    db = get_db()
    review = db.get_by_id('Reviews', review_id)
    
    if not review:
        flash('Review not found.', 'error')
        return redirect(url_for('admin.manage_reviews'))
    
    form = ReviewModerationForm()
    
    if form.validate_on_submit():
        try:
            db.update('Reviews', review_id, {
                'admin_response': form.admin_response.data
            })
            log_admin_activity(g.user['id'], 'review_respond', 'review', review_id, {})
            flash('Admin response added successfully.', 'success')
            return redirect(url_for('admin.manage_reviews'))
        except Exception as e:
            flash(f'Error adding response: {str(e)}', 'error')
    else:
        form.admin_response.data = review.get('admin_response')
    
    return render_template('admin/respond_review.html', form=form, review=review)

# ========== SUPPORT TICKETS ==========

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
        
        log_admin_activity(g.user['id'], 'ticket_update', 'support_ticket', ticket_id,
                         {'new_status': new_status})
        flash('Ticket status updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating ticket: {str(e)}', 'error')
    
    return redirect(url_for('admin.support_tickets'))

# ========== FRAUD MONITORING ==========

@bp.route('/fraud')
@login_required
@admin_required
def fraud_monitoring():
    """Enhanced fraud monitoring"""
    db = get_db()
    
    reviews = db.get_all('Reviews')
    users = db.get_all('Users')
    bookings = db.get_all('Bookings')
    payments = db.get_all('Payments')
    
    # 1. Providers with low ratings
    provider_ratings = {}
    for review in reviews:
        provider_id = review['provider_id']
        if provider_id not in provider_ratings:
            provider_ratings[provider_id] = []
        provider_ratings[provider_id].append(review['rating'])
    
    flagged_providers = []
    for provider_id, ratings in provider_ratings.items():
        avg_rating = sum(ratings) / len(ratings)
        if avg_rating < 2.5 and len(ratings) >= 3:
            provider = db.get_by_id('Users', provider_id)
            if provider:
                provider['avg_rating'] = round(avg_rating, 2)
                provider['review_count'] = len(ratings)
                flagged_providers.append(provider)
    
    # 2. Users with multiple cancellations
    user_cancellations = {}
    for booking in bookings:
        if booking['booking_status'] == 'cancelled':
            user_id = booking['user_id']
            user_cancellations[user_id] = user_cancellations.get(user_id, 0) + 1
    
    flagged_users = []
    for user_id, cancellation_count in user_cancellations.items():
        if cancellation_count >= 3:
            user = db.get_by_id('Users', user_id)
            if user:
                user['cancellation_count'] = cancellation_count
                flagged_users.append(user)
    
    # 3. Duplicate accounts detection (same NID or phone)
    duplicate_accounts = []
    nid_map = {}
    phone_map = {}
    
    for user in users:
        nid = user.get('nid_number')
        phone = user.get('contact_number')
        
        if nid:
            if nid in nid_map:
                if nid not in [d['identifier'] for d in duplicate_accounts]:
                    duplicate_accounts.append({
                        'type': 'NID',
                        'identifier': nid,
                        'users': [nid_map[nid], user]
                    })
                else:
                    # Add to existing duplicate group
                    for dup in duplicate_accounts:
                        if dup['identifier'] == nid:
                            dup['users'].append(user)
            else:
                nid_map[nid] = user
        
        if phone:
            if phone in phone_map and phone not in [d['identifier'] for d in duplicate_accounts]:
                duplicate_accounts.append({
                    'type': 'Phone',
                    'identifier': phone,
                    'users': [phone_map[phone], user]
                })
            else:
                phone_map[phone] = user
    
    # 4. Suspicious payment patterns (multiple failed payments)
    user_failed_payments = {}
    for payment in payments:
        if payment.get('payment_status') == 'failed':
            booking = db.get_by_id('Bookings', payment['booking_id'])
            if booking:
                user_id = booking['user_id']
                user_failed_payments[user_id] = user_failed_payments.get(user_id, 0) + 1
    
    suspicious_payments = []
    for user_id, failed_count in user_failed_payments.items():
        if failed_count >= 3:
            user = db.get_by_id('Users', user_id)
            if user:
                user['failed_payment_count'] = failed_count
                suspicious_payments.append(user)
    
    # 5. Fake reviews detection (very similar reviews from same user)
    user_reviews = {}
    for review in reviews:
        user_id = review['user_id']
        if user_id not in user_reviews:
            user_reviews[user_id] = []
        user_reviews[user_id].append(review)
    
    fake_review_suspects = []
    for user_id, user_review_list in user_reviews.items():
        if len(user_review_list) >= 5:
            # Check if all reviews have same rating and very short comments
            ratings = [r['rating'] for r in user_review_list]
            if len(set(ratings)) == 1:  # All same rating
                avg_comment_length = sum(len(r.get('comment', '')) for r in user_review_list) / len(user_review_list)
                if avg_comment_length < 20:  # Very short comments
                    user = db.get_by_id('Users', user_id)
                    if user:
                        user['review_count'] = len(user_review_list)
                        user['pattern'] = f'All {ratings[0]}-star, short comments'
                        fake_review_suspects.append(user)
    
    return render_template('admin/fraud.html',
                         flagged_providers=flagged_providers,
                         flagged_users=flagged_users,
                         duplicate_accounts=duplicate_accounts,
                         suspicious_payments=suspicious_payments,
                         fake_review_suspects=fake_review_suspects)

# ========== ANALYTICS ==========

@bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Enhanced analytics"""
    db = get_db()
    
    # Get all data
    users = db.get_all('Users')
    services = db.get_all('Services')
    bookings = db.get_all('Bookings')
    payments = db.get_all('Payments')
    categories = db.get_all('Service_Categories')
    reviews = db.get_all('Reviews')
    
    # User analytics
    user_stats = {
        'total_users': len([u for u in users if u['role'] == 'user']),
        'total_providers': len([u for u in users if u['role'] == 'service_provider']),
        'verified_users': len([u for u in users if u.get('email_verified', False)]),
        'active_users': len([u for u in users if u.get('status') == 'active']),
        'suspended_users': len([u for u in users if u.get('status') == 'suspended']),
        'banned_users': len([u for u in users if u.get('status') == 'banned'])
    }
    
    # Booking analytics
    booking_stats = {
        'total_bookings': len(bookings),
        'pending_bookings': len([b for b in bookings if b['booking_status'] == 'pending']),
        'accepted_bookings': len([b for b in bookings if b['booking_status'] == 'accepted']),
        'completed_bookings': len([b for b in bookings if b['booking_status'] == 'completed']),
        'cancelled_bookings': len([b for b in bookings if b['booking_status'] == 'cancelled']),
        'rejected_bookings': len([b for b in bookings if b['booking_status'] == 'rejected'])
    }
    
    # Calculate rates
    total_bookings = booking_stats['total_bookings']
    if total_bookings > 0:
        booking_stats['cancellation_rate'] = round((booking_stats['cancelled_bookings'] / total_bookings) * 100, 1)
        booking_stats['completion_rate'] = round((booking_stats['completed_bookings'] / total_bookings) * 100, 1)
        booking_stats['acceptance_rate'] = round((booking_stats['accepted_bookings'] / total_bookings) * 100, 1)
    else:
        booking_stats['cancellation_rate'] = 0
        booking_stats['completion_rate'] = 0
        booking_stats['acceptance_rate'] = 0
    
    # Revenue analytics
    completed_payments = [p for p in payments if p['payment_status'] == 'completed']
    revenue_stats = {
        'total_revenue': sum(p['total_amount'] for p in completed_payments),
        'platform_fees': sum(p['platform_fee'] for p in completed_payments),
        'pending_payments': sum(p['total_amount'] for p in payments if p['payment_status'] == 'pending'),
        'refunded_payments': sum(p['total_amount'] for p in payments if p.get('payment_status') == 'refunded')
    }
    
    # Payment method distribution
    payment_method_dist = {}
    for payment in completed_payments:
        method = payment.get('payment_method', 'unknown')
        payment_method_dist[method] = payment_method_dist.get(method, 0) + 1
    
    # Service analytics
    service_stats = {
        'total_services': len(services),
        'active_services': len([s for s in services if s.get('status') == 'active']),
        'pending_services': len([s for s in services if s.get('status') == 'pending_approval']),
        'flagged_services': len([s for s in services if s.get('status') == 'flagged'])
    }
    
    # Service popularity by category
    service_popularity = {}
    for category in categories:
        if category.get('is_active', True):
            category_services = [s for s in services if s['category_id'] == category['id']]
            category_bookings = 0
            for service in category_services:
                category_bookings += len([b for b in bookings if b['service_id'] == service['id']])
            service_popularity[category['category_name']] = category_bookings
    
    # Top providers by earnings
    provider_earnings = {}
    for booking in bookings:
        if booking['booking_status'] == 'completed':
            provider_id = booking['provider_id']
            service = db.get_by_id('Services', booking['service_id'])
            if service:
                provider_earnings[provider_id] = provider_earnings.get(provider_id, 0) + service['price']
    
    top_providers = []
    for provider_id, earnings in sorted(provider_earnings.items(), key=lambda x: x[1], reverse=True)[:10]:
        provider = db.get_by_id('Users', provider_id)
        if provider:
            provider_reviews = [r for r in reviews if r['provider_id'] == provider_id]
            avg_rating = sum(r['rating'] for r in provider_reviews) / len(provider_reviews) if provider_reviews else 0
            top_providers.append({
                'name': provider['name'],
                'earnings': round(earnings, 2),
                'rating': round(avg_rating, 1),
                'review_count': len(provider_reviews)
            })
    
    # Average booking value
    if completed_payments:
        avg_booking_value = sum(p['payment_amount'] for p in completed_payments) / len(completed_payments)
    else:
        avg_booking_value = 0
    
    analytics_data = {
        'user_stats': user_stats,
        'booking_stats': booking_stats,
        'revenue_stats': revenue_stats,
        'service_stats': service_stats,
        'service_popularity': service_popularity,
        'payment_method_dist': payment_method_dist,
        'top_providers': top_providers,
        'avg_booking_value': round(avg_booking_value, 2)
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

# ========== ACTIVITY LOG ==========

@bp.route('/activity-log')
@login_required
@admin_required
def activity_log():
    """View admin activity log"""
    db = get_db()
    logs = db.get_all('Admin_Activity_Log')
    
    # Sort by timestamp (newest first)
    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Enrich with admin names
    for log in logs:
        admin = db.get_by_id('Users', log.get('admin_id'))
        log['admin_name'] = admin.get('name') if admin else 'Unknown'
    
    # Pagination (show 50 per page)
    page = request.args.get('page', 1, type=int)
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page
    paginated_logs = logs[start:end]
    
    return render_template('admin/activity_log.html', logs=paginated_logs, 
                          page=page, total_logs=len(logs), per_page=per_page)

@bp.route('/categories/<int:category_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_category(category_id):
    """Approve a pending category request"""
    db = get_db()
    category = db.get_by_id('Service_Categories', category_id)
    
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin.manage_categories'))
    
    try:
        db.update('Service_Categories', category_id, {
            'is_active': True,
            'status': 'approved'
        })
        
        # Notify the requester
        requester_id = category.get('requested_by')
        if requester_id:
            db.add('Notifications', {
                'user_id': requester_id,
                'notification_type': 'in_app',
                'message': f'Your custom category request "{category["category_name"]}" has been approved!'
            })
        
        log_admin_activity(g.user['id'], 'category_approve', 'category', category_id,
                         {'category_name': category['category_name']})
        flash(f'Category "{category["category_name"]}" has been approved!', 'success')
    except Exception as e:
        flash(f'Error approving category: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_categories'))

@bp.route('/categories/<int:category_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_category(category_id):
    """Reject a pending category request"""
    db = get_db()
    category = db.get_by_id('Service_Categories', category_id)
    
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin.manage_categories'))
    
    try:
        # Notify the requester
        requester_id = category.get('requested_by')
        if requester_id:
            db.add('Notifications', {
                'user_id': requester_id,
                'notification_type': 'in_app',
                'message': f'Your custom category request "{category["category_name"]}" has been rejected. Please contact support for more information.'
            })
        
        # Delete the pending request
        db.delete('Service_Categories', category_id)
        
        log_admin_activity(g.user['id'], 'category_reject', 'category', category_id,
                         {'category_name': category['category_name']})
        flash(f'Category request "{category["category_name"]}" has been rejected.', 'warning')
    except Exception as e:
        flash(f'Error rejecting category: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_categories'))

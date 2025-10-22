from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, jsonify
from forms import ServiceForm
from auth import login_required
import random
import string

bp = Blueprint('services', __name__, url_prefix='/services')

def get_db():
    return current_app.db

@bp.route('/')
def browse():
    """Browse all services with optional filtering"""
    db = get_db()
    all_services = db.get_all('Services')
    categories = db.get_all('Service_Categories')
    
    # Filter to show only active/approved services from active providers
    # Also show provider's own pending/active services
    services = []
    current_user_id = g.user['id'] if g.user else None
    
    for service in all_services:
        # Show service if it's approved/active OR if it belongs to the current user (show own pending services)
        is_own_service = current_user_id and service.get('provider_id') == current_user_id
        is_approved = service.get('status') in ['active', 'approved']
        
        if not (is_approved or is_own_service):
            continue
            
        provider = db.get_by_id('Users', service.get('provider_id'))
        if provider and provider.get('status') == 'active':
            services.append(service)
    
    # Get filter parameters
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category')
    location_filter = request.args.get('location')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'popular')
    
    # Apply search filter
    if search_query:
        services = [s for s in services if 
                   search_query.lower() in s.get('service_name', '').lower() or
                   search_query.lower() in s.get('description', '').lower() or
                   search_query.lower() in s.get('location', '').lower()]
    
    # Apply other filters
    if category_filter:
        services = [s for s in services if s.get('category_id') == int(category_filter)]
    
    if location_filter:
        services = [s for s in services if location_filter.lower() in s.get('location', '').lower()]
    
    if min_price is not None:
        services = [s for s in services if s.get('price', 0) >= min_price]
    
    if max_price is not None:
        services = [s for s in services if s.get('price', 0) <= max_price]
    
    # Enrich services with category and provider information
    for service in services:
        category = db.get_by_id('Service_Categories', service.get('category_id'))
        provider = db.get_by_id('Users', service.get('provider_id'))
        service['category_name'] = category.get('category_name') if category else 'Unknown'
        service['provider_name'] = provider.get('name') if provider else 'Unknown'
        service['provider_email'] = provider.get('email') if provider else 'Unknown'
        
        # Get average rating for sorting
        reviews = [r for r in db.get_all('Reviews') if r.get('service_id') == service['id']]
        if reviews:
            service['avg_rating'] = sum(r.get('rating', 0) for r in reviews) / len(reviews)
            service['review_count'] = len(reviews)
        else:
            service['avg_rating'] = 0
            service['review_count'] = 0
    
    # Apply sorting
    if sort_by == 'popular':
        services.sort(key=lambda s: (s.get('review_count', 0), s.get('avg_rating', 0)), reverse=True)
    elif sort_by == 'price_low':
        services.sort(key=lambda s: s.get('price', 0))
    elif sort_by == 'price_high':
        services.sort(key=lambda s: s.get('price', 0), reverse=True)
    elif sort_by == 'newest':
        services.sort(key=lambda s: s.get('created_at', ''), reverse=True)
    
    # Filter to show only active categories
    categories = [c for c in categories if c.get('is_active', True)]
    
    return render_template('services/browse.html', services=services, categories=categories)

@bp.route('/<int:service_id>')
def detail(service_id):
    """View service details"""
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('services.browse'))
    
    # Get category and provider information
    category = db.get_by_id('Service_Categories', service.get('category_id'))
    provider = db.get_by_id('Users', service.get('provider_id'))
    
    # Get reviews for this service (exclude flagged reviews)
    all_reviews = db.find_by_attribute('Reviews', 'provider_id', service.get('provider_id'))
    reviews = [r for r in all_reviews if not r.get('is_flagged', False)]
    
    # Enrich reviews with user info
    for review in reviews:
        user = db.get_by_id('Users', review.get('user_id'))
        review['user'] = user if user else {'name': 'Anonymous'}
    
    # Calculate average rating and review count
    if reviews:
        average_rating = sum(r['rating'] for r in reviews) / len(reviews)
        review_count = len(reviews)
    else:
        average_rating = 0
        review_count = 0
    
    # Calculate completed jobs
    all_bookings = db.get_all("Bookings")
    completed_jobs = len([b for b in all_bookings if b["provider_id"] == service.get("provider_id") and b["booking_status"] == "completed"])
    
    # Check if current user has an accepted/completed booking for this service
    user_has_booking = False
    if g.user and g.user.get('role') == 'user':
        user_bookings = [b for b in all_bookings 
                        if b.get('user_id') == g.user['id'] 
                        and b.get('service_id') == service_id
                        and b.get('booking_status') in ['accepted', 'completed']]
        user_has_booking = len(user_bookings) > 0
    
    service['category_name'] = category.get('category_name') if category else 'Unknown'
    service['provider_name'] = provider.get('name') if provider else 'Unknown'
    service['provider_email'] = provider.get('email') if provider else 'Not provided'
    service['contact_number'] = provider.get('contact_number') if provider else 'Not provided'
    service['provider'] = provider
    
    return render_template('services/detail.html', service=service, reviews=reviews, average_rating=average_rating, review_count=review_count, completed_jobs=completed_jobs, user_has_booking=user_has_booking)

@bp.route('/<int:service_id>/start-chat')
@login_required
def start_chat(service_id):
    """Find or prompt to create a booking to start chat"""
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('services.browse'))
    
    # Find existing booking between user and this service's provider
    all_bookings = db.get_all('Bookings')
    user_bookings = [b for b in all_bookings 
                    if b.get('user_id') == g.user['id'] 
                    and b.get('service_id') == service_id
                    and b.get('booking_status') in ['pending', 'confirmed', 'completed']]
    
    if user_bookings:
        # Use the most recent booking
        booking = sorted(user_bookings, key=lambda x: x.get('created_at', ''), reverse=True)[0]
        return redirect(url_for('chat.booking_chat', booking_id=booking['id']))
    else:
        # No booking exists, prompt user to book first
        flash('Please book this service first to start chatting with the provider.', 'info')
        return redirect(url_for('bookings.book_service', service_id=service_id))

@bp.route('/manage')
@login_required
def manage():
    """Manage services for providers"""
    if g.user['role'] != 'service_provider':
        flash('Access denied. Only service providers can manage services.', 'error')
        return redirect(url_for('index'))
    
    if g.user.get('status') != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    services = db.find_by_attribute('Services', 'provider_id', g.user['id'])
    categories = db.get_all('Service_Categories')
    
    # Enrich services with category information
    for service in services:
        category = db.get_by_id('Service_Categories', service.get('category_id'))
        service['category_name'] = category.get('category_name') if category else 'Unknown'
    
    return render_template('services/manage.html', services=services, categories=categories)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new service"""
    if g.user['role'] != 'service_provider':
        flash('Access denied. Only service providers can add services.', 'error')
        return redirect(url_for('index'))
    
    if g.user.get('status') != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    form = ServiceForm()
    
    # Populate category choices (only active categories)
    all_categories = db.get_all('Service_Categories')
    categories = [c for c in all_categories if c.get('is_active', True)]
    form.category_id.choices = [(c['id'], c['category_name']) for c in categories]
    
    if form.validate_on_submit():
        try:
            service = db.add('Services', {
                'category_id': form.category_id.data,
                'provider_id': g.user['id'],
                'service_name': form.service_name.data,
                'description': form.description.data,
                'price': float(form.price.data),
                'location': form.location.data,
                'status': 'pending'
            })
            
            # Create notification for admin
            db.add('Notifications', {
                'user_id': 1,  # Admin user ID
                'message': f'New service "{form.service_name.data}" submitted by {g.user.get("name")} for approval.',
                'notification_type': 'service_approval',
                'is_read': False
            })
            
            flash('Service added successfully and submitted for admin approval!', 'success')
            return redirect(url_for('services.manage'))
        except Exception as e:
            flash(f'Error adding service: {str(e)}', 'error')
    
    return render_template('services/add.html', form=form)

@bp.route('/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit(service_id):
    """Edit an existing service"""
    if g.user['role'] != 'service_provider':
        flash('Access denied. Only service providers can edit services.', 'error')
        return redirect(url_for('index'))
    
    if g.user.get('status') != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('services.manage'))
    
    if service['provider_id'] != g.user['id']:
        flash('Access denied. You can only edit your own services.', 'error')
        return redirect(url_for('services.manage'))
    
    form = ServiceForm(obj=type('obj', (object,), service)())
    
    # Populate category choices (only active categories)
    all_categories = db.get_all('Service_Categories')
    categories = [c for c in all_categories if c.get('is_active', True)]
    form.category_id.choices = [(c['id'], c['category_name']) for c in categories]
    
    if form.validate_on_submit():
        try:
            db.update('Services', service_id, {
                'category_id': form.category_id.data,
                'service_name': form.service_name.data,
                'description': form.description.data,
                'price': float(form.price.data),
                'location': form.location.data
            })
            flash('Service updated successfully!', 'success')
            return redirect(url_for('services.manage'))
        except Exception as e:
            flash(f'Error updating service: {str(e)}', 'error')
    
    return render_template('services/edit.html', form=form, service=service)

@bp.route('/delete/<int:service_id>', methods=['POST'])
@login_required
def delete(service_id):
    """Delete a service"""
    if g.user['role'] != 'service_provider':
        flash('Access denied. Only service providers can delete services.', 'error')
        return redirect(url_for('index'))
    
    if g.user.get('status') != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('services.manage'))
    
    if service['provider_id'] != g.user['id']:
        flash('Access denied. You can only delete your own services.', 'error')
        return redirect(url_for('services.manage'))
    
    try:
        db.delete('Services', service_id)
        flash('Service deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting service: {str(e)}', 'error')
    
    return redirect(url_for('services.manage'))

@bp.route('/categories')
def categories():
    """List all service categories"""
    db = get_db()
    categories = db.get_all('Service_Categories')
    return render_template('services/categories.html', categories=categories)

@bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """Add a new service category (admin only)"""
    if g.user['role'] != 'admin':
        flash('Access denied. Only admins can add categories.', 'error')
        return redirect(url_for('services.categories'))
    
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        description = request.form.get('description')
        
        if not category_name:
            flash('Category name is required.', 'error')
        else:
            try:
                db = get_db()
                db.add('Service_Categories', {
                    'category_name': category_name,
                    'description': description
                })
                flash('Category added successfully!', 'success')
                return redirect(url_for('services.categories'))
            except Exception as e:
                flash(f'Error adding category: {str(e)}', 'error')
    
    return render_template('services/add_category.html')


@bp.route('/request-category', methods=['GET', 'POST'])
@login_required
def request_category():
    """Request a new custom category"""
    if g.user['role'] != 'service_provider':
        flash('Only service providers can request custom categories.', 'error')
        return redirect(url_for('index'))
    
    from forms import CategoryForm
    from datetime import datetime
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            db = get_db()
            
            # Create category with pending status
            category_data = {
                'category_name': form.category_name.data,
                'description': form.description.data,
                'is_active': False,  # Not active until approved
                'display_order': form.display_order.data or 999,
                'requested_by': g.user['id'],
                'status': 'pending_approval',
                'created_at': datetime.now().isoformat()
            }
            db.add('Service_Categories', category_data)
            
            # Notify admin
            db.add('Activity_Log', {
                'admin_id': None,
                'action_type': 'category_request',
                'action_description': f'New category "{form.category_name.data}" requested by {g.user["name"]}',
                'target_type': 'category',
                'timestamp': datetime.now().isoformat()
            })
            
            flash('Your custom category request has been submitted for admin approval!', 'success')
            return redirect(url_for('services.manage'))
        except Exception as e:
            flash(f'Error submitting category request: {str(e)}', 'error')
    
    return render_template('services/request_category.html', form=form)

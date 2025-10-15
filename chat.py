from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, jsonify
from auth import login_required
from datetime import datetime
import json

bp = Blueprint('chat', __name__, url_prefix='/chat')

def get_db():
    return current_app.db

@bp.route('/booking/<int:booking_id>')
@login_required
def booking_chat(booking_id):
    """Chat interface for a specific booking"""
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('bookings.list_bookings'))
    
    # Check access permissions
    if g.user['id'] not in [booking['user_id'], booking['provider_id']]:
        flash('Access denied.', 'error')
        return redirect(url_for('bookings.list_bookings'))
    
    # Get chat messages
    messages = db.find_by_attribute('Chat_Messages', 'booking_id', booking_id)
    
    # Sort messages by sent_at
    messages.sort(key=lambda x: x.get('sent_at', ''))
    
    # Enrich messages with sender information
    for message in messages:
        sender = db.get_by_id('Users', message.get('sender_id'))
        message['sender_name'] = sender.get('name') if sender else 'Unknown'
        message['is_own'] = message['sender_id'] == g.user['id']
    
    # Get other participant info
    if g.user['id'] == booking['user_id']:
        other_user = db.get_by_id('Users', booking['provider_id'])
    else:
        other_user = db.get_by_id('Users', booking['user_id'])
    
    service = db.get_by_id('Services', booking.get('service_id'))
    
    # Mark messages as read
    try:
        for message in messages:
            if message['receiver_id'] == g.user['id'] and not message.get('is_read', False):
                db.update('Chat_Messages', message['id'], {'is_read': True})
    except Exception as e:
        print(f"Error marking messages as read: {e}")
        flash('Error marking messages as read.', 'error')
    
    return render_template("chat/booking_chat.html", 
                         booking=booking, 
                         messages=messages, 
                         other_user=other_user,
                         service=service)

@bp.route("/send_message/<int:booking_id>", methods=["POST"])
@login_required
def send_message(booking_id):
    message_content = request.form.get("message_content", "").strip()    
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'})
    
    # Check access permissions
    if g.user['id'] not in [booking['user_id'], booking['provider_id']]:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    # Determine receiver
    if g.user['id'] == booking['user_id']:
        receiver_id = booking['provider_id']
    else:
        receiver_id = booking['user_id']
    
    try:
        # Add message
        message = db.add('Chat_Messages', {
            'booking_id': booking_id,
            'sender_id': g.user['id'],
            'receiver_id': receiver_id,
            'message_content': message_content,
            'sent_at': datetime.now().isoformat(),
            'is_read': False
        })
        
        # Create notification for receiver
        db.add('Notifications', {
            'user_id': receiver_id,
            'notification_type': 'in_app',
            'message': f'New message from {g.user["name"]} about booking #{booking_id}',
            'sent_at': datetime.now().isoformat(),
            'is_read': False
        })
        
        return jsonify({
            'success': True,
            'message': {
                'id': message['id'],
                'sender_name': g.user['name'],
                'message_content': message_content,
                'sent_at': message['sent_at'],
                'is_own': True
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/get_messages/<int:booking_id>')
@login_required
def get_messages(booking_id):
    """Get chat messages for a booking (AJAX endpoint)"""
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'})
    
    # Check access permissions
    if g.user['id'] not in [booking['user_id'], booking['provider_id']]:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    # Get messages
    messages = db.find_by_attribute('Chat_Messages', 'booking_id', booking_id)
    
    # Sort messages by sent_at
    messages.sort(key=lambda x: x.get('sent_at', ''))
    
    # Enrich messages with sender information
    for message in messages:
        sender = db.get_by_id('Users', message.get('sender_id'))
        message['sender_name'] = sender.get('name') if sender else 'Unknown'
        message['is_own'] = message['sender_id'] == g.user['id']
    
    return jsonify({"success": True, "messages": messages})

@bp.route("/mark_read/<int:booking_id>", methods=["POST"])
@login_required
def mark_read(booking_id):
    """Mark messages for a booking as read"""
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'})
    
    # Check access permissions
    if g.user['id'] not in [booking['user_id'], booking['provider_id']]:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        # Get unread messages for this user
        messages = db.find_by_attribute('Chat_Messages', 'booking_id', booking_id)
        unread_messages = [m for m in messages if m['receiver_id'] == g.user['id'] and not m.get('is_read', False)]
        
        # Mark as read
        for message in unread_messages:
            db.update('Chat_Messages', message['id'], {'is_read': True})
        
        return jsonify({'success': True, 'marked_count': len(unread_messages)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/conversations')
@login_required
def conversations():
    """List all conversations for the current user"""
    db = get_db()
    
    # Get all bookings where user is involved
    all_bookings = db.get_all('Bookings')
    user_bookings = [b for b in all_bookings if b['user_id'] == g.user['id'] or b['provider_id'] == g.user['id']]
    
    conversations = []
    for booking in user_bookings:
        # Get last message
        messages = db.find_by_attribute('Chat_Messages', 'booking_id', booking['id'])
        if messages:
            messages.sort(key=lambda x: x.get('sent_at', ''), reverse=True)
            last_message = messages[0]
            
            # Get unread count
            unread_count = len([m for m in messages if m['receiver_id'] == g.user['id'] and not m.get('is_read', False)])
        else:
            last_message = None
            unread_count = 0
        
        # Get other participant
        if g.user['id'] == booking['user_id']:
            other_user = db.get_by_id('Users', booking['provider_id'])
        else:
            other_user = db.get_by_id('Users', booking['user_id'])
        
        # Get service info
        service = db.get_by_id('Services', booking.get('service_id'))
        
        conversations.append({
            'booking': booking,
            'other_user': other_user,
            'service': service,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Sort by last message time
    conversations.sort(key=lambda x: x['last_message']['sent_at'] if x['last_message'] else '', reverse=True)
    
    return render_template('chat/conversations.html', conversations=conversations)

@bp.route('/delete_message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    """Delete a chat message (sender only)"""
    db = get_db()
    message = db.get_by_id('Chat_Messages', message_id)
    
    if not message:
        return jsonify({'success': False, 'error': 'Message not found'})
    
    # Only sender can delete their own messages
    if message['sender_id'] != g.user['id']:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        # Mark as deleted instead of actually deleting
        db.update('Chat_Messages', message_id, {
            'message_content': '[Message deleted]',
            'is_deleted': True,
            'deleted_at': datetime.now().isoformat()
        })
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route("/typing/<int:booking_id>", methods=["POST"])
@login_required
def typing_indicator(booking_id):
    """Handle typing indicator"""
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'})
    
    # Check access permissions
    if g.user['id'] not in [booking['user_id'], booking['provider_id']]:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    is_typing = request.form.get('is_typing', 'false').lower() == 'true'
    
    return jsonify({'success': True, 'is_typing': is_typing})
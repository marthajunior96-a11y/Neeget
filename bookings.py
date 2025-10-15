from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, jsonify
from forms import BookingForm, ReviewForm, ConfirmForm
from auth import login_required
from datetime import datetime
import random
import string

bp = Blueprint("bookings", __name__, url_prefix="/bookings")

def get_db():
    return current_app.db

def generate_otp():
    """Generate a 6-digit OTP"""
    return "".join(random.choices(string.digits, k=6))

def calculate_platform_fee(amount):
    """Calculate platform fee (10% of service price)"""
    db = get_db()
    settings = db.get_all('Platform_Settings')
    fee_setting = next((s for s in settings if s['setting_key'] == 'platform_fee_percentage'), None)
    fee_percentage = float(fee_setting['setting_value']) / 100 if fee_setting else 0.10
    return round(amount * fee_percentage, 2)

@bp.route("/")
@login_required
def list_bookings():
    db = get_db()
    
    bookings = []
    if g.user:
        if g.user["role"] == "service_provider":
            bookings = db.find_by_attribute("Bookings", "provider_id", g.user["id"])
        else:
            bookings = db.find_by_attribute("Bookings", "user_id", g.user["id"])
    
    for booking in bookings:
        service = db.get_by_id("Services", booking.get("service_id"))
        user = db.get_by_id("Users", booking.get("user_id"))
        provider = db.get_by_id("Users", booking.get("provider_id"))
        
        booking["service"] = service
        booking["user"] = user
        booking["provider"] = provider
    
    return render_template("bookings/list.html", bookings=bookings)

@bp.route("/book/<int:service_id>", methods=["GET", "POST"])
@login_required
def book_service(service_id):
    if g.user["role"] != "user":
        flash("Only users can book services.", "error")
        return redirect(url_for("services.browse"))
    
    if g.user.get("status") != "active":
        flash("Your account is not active. Please contact support.", "error")
        return redirect(url_for("services.browse"))
    
    db = get_db()
    service = db.get_by_id("Services", service_id)
    
    if not service:
        flash("Service not found.", "error")
        return redirect(url_for("services.browse"))
    
    provider = db.get_by_id("Users", service.get("provider_id"))
    
    # Check if provider is active
    if not provider or provider.get("status") != "active":
        flash("This service provider is not available at the moment.", "error")
        return redirect(url_for("services.browse"))
    
    # Check if service is active
    if service.get("status") != "active":
        flash("This service is not available at the moment.", "error")
        return redirect(url_for("services.browse"))
    
    reviews = db.find_by_attribute("Reviews", "provider_id", provider["id"])
    if reviews:
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        review_count = len(reviews)
    else:
        avg_rating = 0
        review_count = 0
    form = BookingForm()
    
    # Populate payment methods dynamically from Platform_Settings
    settings = db.get_all('Platform_Settings')
    payment_setting = next((s for s in settings if s['setting_key'] == 'payment_methods'), None)
    if payment_setting:
        methods = payment_setting['setting_value'].split(',')
        form.payment_method.choices = [(m.strip().lower().replace(' ', '_'), m.strip()) for m in methods]
    
    # Create a dummy booking for GET request to avoid undefined error
    booking = {
        "booking_date": datetime.now().isoformat(),
        "service_date": "",
        "id": None
    }
    
    print(f"Route: /book/{service_id}, Method: {request.method}, Form Data: {form.data}, Errors: {form.errors}, User: {g.user}")
    
    if form.validate_on_submit():
        # Explicitly check required fields
        if not form.payment_method.data:
            flash("Please select a payment method.", "error")
            return render_template("bookings/book.html", form=form, service=service, provider=provider, booking=booking)
        
        try:
            service_price = float(service["price"])
            platform_fee = calculate_platform_fee(service_price)
            total_amount = service_price + platform_fee
            
            booking = db.add("Bookings", {
                "user_id": g.user["id"],
                "service_id": service_id,
                "provider_id": service["provider_id"],
                "booking_status": "pending",
                "booking_date": datetime.now().isoformat(),
                "service_date": form.service_date.data.isoformat(),
                "otp_code": generate_otp(),
                "location": form.location.data,
                "contact_number": form.contact_number.data
            })
            
            payment = db.add("Payments", {
                "booking_id": booking["id"],
                "payment_method": form.payment_method.data,
                "payment_amount": service_price,
                "platform_fee": platform_fee,
                "total_amount": total_amount,
                "payment_status": "pending"
            })
            
            db.add("Notifications", {
                "user_id": service["provider_id"],
                "notification_type": "in_app",
                "message": f"New booking request from {g.user['name']} for {service['service_name']}"
            })
            
            flash("Booking request submitted successfully!", "success")
            return redirect(url_for("bookings.payment", booking_id=booking["id"]))
            
        except Exception as e:
            flash(f"Error creating booking: {str(e)}", "error")
            return render_template("bookings/book.html", form=form, service=service, provider=provider, booking=booking)
    
    return render_template("bookings/book.html", form=form, service=service, provider=provider, booking=booking,avg_rating=avg_rating, review_count=review_count)

@bp.route("/payment/<int:booking_id>")
@login_required
def payment(booking_id):
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["user_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    service = db.get_by_id("Services", booking.get("service_id"))
    provider = db.get_by_id("Users", booking.get("provider_id"))
    payment = db.find_by_attribute("Payments", "booking_id", booking_id)[0] if db.find_by_attribute("Payments", "booking_id", booking_id) else None
    form = ConfirmForm()
    
    if provider:
        booking["provider"] = provider
    
    return render_template("bookings/payment.html", booking=booking, service=service, payment=payment, form=form)

@bp.route("/confirm/<int:booking_id>", methods=["POST"])
@login_required
def confirm(booking_id):
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["user_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    form = ConfirmForm()
    if not form.validate_on_submit():
        flash("Invalid confirmation request.", "error")
        return redirect(url_for("bookings.payment", booking_id=booking_id))
    
    service = db.get_by_id("Services", booking.get("service_id"))
    provider = db.get_by_id("Users", booking.get("provider_id"))
    payment = db.find_by_attribute("Payments", "booking_id", booking_id)[0] if db.find_by_attribute("Payments", "booking_id", booking_id) else None
    
    if not payment:
        flash("Payment information not found.", "error")
        return redirect(url_for("bookings.payment", booking_id=booking_id))
    
    try:
        db.update("Payments", payment["id"], {"payment_status": "completed"})
       
        
        db.add("Notifications", {
            "user_id": provider["id"] if provider else booking["provider_id"],
            "notification_type": "in_app",
            "message": f"New paid booking request from {g.user['name']}"
        })
        db.add("Notifications", {
            "user_id": booking["user_id"],
            "notification_type": "in_app",
            "message": f"Your payment for {service['service_name'] if service else 'this service'} has been confirmed!"
        })
        
        flash("Service Requested For Booking successfully!", "success")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    except Exception as e:
        flash(f"Error confirming payment: {str(e)}", "error")
        return redirect(url_for("bookings.payment", booking_id=booking_id))

@bp.route("/<int:booking_id>")
@login_required
def detail(booking_id):
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking:
        flash("Booking not found.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if g.user["role"] == "user" and booking["user_id"] != g.user["id"]:
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    elif g.user["role"] == "service_provider" and booking["provider_id"] != g.user["id"]:
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    service = db.get_by_id("Services", booking.get("service_id"))
    user = db.get_by_id("Users", booking.get("user_id"))
    provider = db.get_by_id("Users", booking.get("provider_id"))
    payment = db.find_by_attribute("Payments", "booking_id", booking_id)
    payment = payment[0] if payment else None
    
    messages = db.find_by_attribute("Chat_Messages", "booking_id", booking_id)
    for message in messages:
        sender = db.get_by_id("Users", message.get("sender_id"))
        message["sender_name"] = sender.get("name") if sender else "Unknown"
    
    review = db.find_by_attribute("Reviews", "booking_id", booking_id)
    review = review[0] if review else None
    
    booking["service"] = service
    booking["user"] = user
    booking["provider"] = provider
    booking["payment"] = payment
    booking["messages"] = messages
    
    return render_template("bookings/detail.html", booking=booking, review=review)

@bp.route("/<int:booking_id>/accept", methods=["POST"])
@login_required
def accept_booking(booking_id):
    if g.user["role"] != "service_provider":
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["provider_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] != "pending":
        flash("Booking cannot be accepted in its current status.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    try:
        db.update("Bookings", booking_id, {"booking_status": "accepted"})
        
        db.add("Notifications", {
            "user_id": booking["user_id"],
            "notification_type": "in_app",
            "message": f"Your booking has been accepted by {g.user['name']}"
        })
        
        flash("Booking accepted successfully!", "success")
    except Exception as e:
        flash(f"Error accepting booking: {str(e)}", "error")
    
    return redirect(url_for("bookings.detail", booking_id=booking_id))

@bp.route("/<int:booking_id>/reject", methods=["POST"])
@login_required
def reject_booking(booking_id):
    if g.user["role"] != "service_provider":
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["provider_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] != "pending":
        flash("Booking cannot be rejected in its current status.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    try:
        db.update("Bookings", booking_id, {"booking_status": "rejected"})
        
        db.add("Notifications", {
            "user_id": booking["user_id"],
            "notification_type": "in_app",
            "message": f"Your booking has been rejected by {g.user['name']}"
        })
        
        flash("Booking rejected.", "success")
    except Exception as e:
        flash(f"Error rejecting booking: {str(e)}", "error")
    
    return redirect(url_for("bookings.detail", booking_id=booking_id))

@bp.route("/<int:booking_id>/complete", methods=["POST"])
@login_required
def complete_booking(booking_id):
    if g.user["role"] != "service_provider":
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["provider_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] != "accepted":
        flash("Booking must be accepted before it can be completed.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    otp_input = request.form.get("otp_code")
    if not otp_input or otp_input != booking["otp_code"]:
        flash("Invalid OTP. Please try again.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    try:
        db.update("Bookings", booking_id, {"booking_status": "completed"})
        
        payments = db.find_by_attribute("Payments", "booking_id", booking_id)
        if payments:
            db.update("Payments", payments[0]["id"], {"payment_status": "completed"})
        
        db.add("Notifications", {
            "user_id": booking["user_id"],
            "notification_type": "in_app",
            "message": f"Your booking has been completed by {g.user['name']}. Please leave a review!"
        })
        
        flash("Booking marked as completed!", "success")
    except Exception as e:
        flash(f"Error completing booking: {str(e)}", "error")
    
    return redirect(url_for("bookings.detail", booking_id=booking_id))

@bp.route("/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    if g.user["role"] != "user":
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if g.user.get("status") != "active":
        flash("Your account is not active. Please contact support.", "error")
        return redirect(url_for("services.browse"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["user_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] != "pending":
        flash("Booking cannot be cancelled in its current status.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    try:
        db.update("Bookings", booking_id, {"booking_status": "cancelled"})
        
        db.add("Notifications", {
            "user_id": booking["provider_id"],
            "notification_type": "in_app",
            "message": f"Booking has been cancelled by {g.user['name']}"
        })
        
        flash("Booking cancelled successfully.", "success")
    except Exception as e:
        flash(f"Error cancelling booking: {str(e)}", "error")
    
    return redirect(url_for("bookings.detail", booking_id=booking_id))

@bp.route("/<int:booking_id>/review", methods=["GET", "POST"])
@login_required
def review_booking(booking_id):
    if g.user["role"] != "user":
        flash("Only users can leave reviews.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if g.user.get("status") != "active":
        flash("Your account is not active. Please contact support.", "error")
        return redirect(url_for("services.browse"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["user_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] != "completed":
        flash("You can only review completed bookings.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    existing_reviews = db.find_by_attribute("Reviews", "booking_id", booking_id)
    if existing_reviews:
        flash("You have already reviewed this booking.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        try:
            db.add("Reviews", {
                "booking_id": booking_id,
                "user_id": g.user["id"],
                "provider_id": booking["provider_id"],
                "rating": form.rating.data,
                "comment": form.comment.data,
                "created_at": datetime.now().isoformat()
            })
            
            flash("Review submitted successfully!", "success")
            return redirect(url_for("bookings.detail", booking_id=booking_id))
        except Exception as e:
            flash(f"Error submitting review: {str(e)}", "error")
    
    service = db.get_by_id("Services", booking.get("service_id"))
    provider = db.get_by_id("Users", booking.get("provider_id"))
    
    return render_template("bookings/review.html", form=form, booking=booking, service=service, provider=provider)
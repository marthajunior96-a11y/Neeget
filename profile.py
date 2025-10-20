from flask import Blueprint, render_template, g, redirect, url_for, request, flash, current_app
from data_manager import DataManager
from auth import login_required
import bcrypt

bp = Blueprint("profile", __name__, url_prefix="/profile")

@bp.before_app_request
def load_logged_in_user():
    user_id = g.user["id"] if g.user else None
    if user_id is None:
        g.user = None
    else:
        g.user = current_app.db.get_by_id("Users", user_id)

@bp.route("")
@login_required
def view():
    user = g.user
    if not user:
        flash("You must be logged in to view your profile.", "error")
        return redirect(url_for("auth.login"))

    # Calculate user stats
    all_bookings = current_app.db.get_all("Bookings")
    user_bookings = [b for b in all_bookings if b["user_id"] == user["id"]]
    total_bookings = len(user_bookings)
    pending_bookings = len([b for b in user_bookings if b["booking_status"] == "pending"])
    completed_bookings = len([b for b in user_bookings if b["booking_status"] == "completed"])
    favorite_services = len(current_app.db.find_by_attribute("Favorites", "user_id", user["id"]))

    user_stats = {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "completed_bookings": completed_bookings,
        "favorite_services": favorite_services
    }

    # Calculate provider stats if applicable
    provider_stats = None
    if user["role"] == "service_provider":
        all_services = current_app.db.get_all("Services")
        my_services = [s for s in all_services if s["provider_id"] == user["id"]]
        provider_bookings = [b for b in all_bookings if b["provider_id"] == user["id"]]
        all_reviews = current_app.db.get_all("Reviews")
        my_reviews = [r for r in all_reviews if r["provider_id"] == user["id"]]

        total_services = len(my_services)
        total_bookings = len(provider_bookings)
        average_rating = sum([r["rating"] for r in my_reviews]) / len(my_reviews) if my_reviews else 0
        total_earnings = sum([current_app.db.get_by_id("Services", b["service_id"])["price"] for b in provider_bookings if b["booking_status"] == "completed" and current_app.db.get_by_id("Services", b["service_id"])]) if provider_bookings else 0

        provider_stats = {
            "total_services": total_services,
            "total_bookings": total_bookings,
            "average_rating": round(average_rating, 1),
            "total_earnings": round(total_earnings, 2),
            "response_rate": 95,  # Placeholder
            "completion_rate": round(len([b for b in provider_bookings if b["booking_status"] == "completed"]) / total_bookings * 100, 1) if total_bookings else 0,
            "satisfaction_rate": 96  # Placeholder
        }

    return render_template("profile/view.html", user=user, user_stats=user_stats, provider_stats=provider_stats)

@bp.route("/<int:user_id>")
@login_required
def view_other(user_id):
    user = current_app.db.get_by_id("Users", user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("index"))
    
    # Restrict access (e.g., only admins or the user themselves can view
    if g.user["id"] != user_id and g.user["role"] != "admin":
        flash("You do not have permission to view this profile.", "error")
        return redirect(url_for("profile.view"))

    # Calculate user stats
    all_bookings = current_app.db.get_all("Bookings")
    user_bookings = [b for b in all_bookings if b["user_id"] == user_id]
    total_bookings = len(user_bookings)
    pending_bookings = len([b for b in user_bookings if b["booking_status"] == "pending"])
    completed_bookings = len([b for b in user_bookings if b["booking_status"] == "completed"])
    favorite_services = len(current_app.db.find_by_attribute("Favorites", "user_id", user_id))

    user_stats = {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "completed_bookings": completed_bookings,
        "favorite_services": favorite_services
    }

    # Calculate provider stats if applicable
    provider_stats = None
    if user["role"] == "service_provider":
        all_services = current_app.db.get_all("Services")
        my_services = [s for s in all_services if s["provider_id"] == user_id]
        provider_bookings = [b for b in all_bookings if b["provider_id"] == user_id]
        all_reviews = current_app.db.get_all("Reviews")
        my_reviews = [r for r in all_reviews if r["provider_id"] == user_id]

        total_services = len(my_services)
        total_bookings = len(provider_bookings)
        average_rating = sum([r["rating"] for r in my_reviews]) / len(my_reviews) if my_reviews else 0
        total_earnings = sum([current_app.db.get_by_id("Services", b["service_id"])["price"] for b in provider_bookings if b["booking_status"] == "completed" and current_app.db.get_by_id("Services", b["service_id"])]) if provider_bookings else 0

        provider_stats = {
            "total_services": total_services,
            "total_bookings": total_bookings,
            "average_rating": round(average_rating, 1),
            "total_earnings": round(total_earnings, 2),
            "response_rate": 95,  # Placeholder
            "completion_rate": round(len([b for b in provider_bookings if b["booking_status"] == "completed"]) / total_bookings * 100, 1) if total_bookings else 0,
            "satisfaction_rate": 96  # Placeholder
        }

    return render_template("profile/view.html", user=user, user_stats=user_stats, provider_stats=provider_stats)

@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if not g.user:
        flash("You must be logged in to edit your profile.", "error")
        return redirect(url_for("auth.login"))

    from forms import ProfileForm
    # Preprocess g.user data to match form fields
    user_data = {
        "name": g.user.get("name", ""),
        "email": g.user.get("email", ""),
        "contact_number": g.user.get("contact_number", ""),
        "address": g.user.get("address", ""),
        "profession": g.user.get("profession", ""),
        "experience": g.user.get("experience", ""),
        "expertise": g.user.get("expertise", ""),
        "professional_description": g.user.get("professional_description", ""),
        "preferred_locations": g.user.get("preferred_locations", ""),
        "portfolio_url": g.user.get("portfolio_url", ""),
        "email_notifications": g.user.get("email_notifications", True),
        "sms_notifications": g.user.get("sms_notifications", False),
        "marketing_emails": g.user.get("marketing_emails", False),
        "profile_visibility": g.user.get("profile_visibility", True),
        "current_password": "",
        "new_password": "",
        "confirm_password": ""
    }
    print(f"User data for form: {user_data}")  # Debug log
    form = ProfileForm(data=user_data)  # Use data= instead of obj= for dictionary compatibility
    
    if form.validate_on_submit():
        try:
            update_data = {
                "name": form.name.data,
                "email": form.email.data,
                "contact_number": form.contact_number.data,
                "address": form.address.data,
                "profession": form.profession.data,
                "experience": form.experience.data,
                "expertise": form.expertise.data,
                "professional_description": form.professional_description.data,
                "preferred_locations": form.preferred_locations.data,
                "portfolio_url": form.portfolio_url.data,
                "email_notifications": form.email_notifications.data,
                "sms_notifications": form.sms_notifications.data,
                "marketing_emails": form.marketing_emails.data,
                "profile_visibility": form.profile_visibility.data
            }
            if form.new_password.data:
                if not form.current_password.data:
                    flash("Current password is required to change password.", "error")
                    return render_template("profile/edit.html", form=form, user=g.user)
                if not bcrypt.checkpw(form.current_password.data.encode("utf-8"), g.user.get("password_hash", "").encode("utf-8")):
                    flash("Incorrect current password.", "error")
                    return render_template("profile/edit.html", form=form, user=g.user)
                if form.new_password.data != form.confirm_password.data:
                    flash("New passwords do not match.", "error")
                    return render_template("profile/edit.html", form=form, user=g.user)
                update_data["password_hash"] = bcrypt.hashpw(form.new_password.data.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            current_app.db.update("Users", g.user["id"], update_data)
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile.view"))
        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "error")
    
    return render_template("profile/edit.html", form=form, user=g.user)

@bp.route("/notifications")
@login_required
def notifications():
    if not g.user:
        return redirect(url_for("auth.login"))

    notifications = current_app.db.find_by_attribute("Notifications", "user_id", g.user["id"])
    notifications.sort(key=lambda x: x.get("sent_at", ""), reverse=True)

    return render_template("profile/notifications.html", notifications=notifications)
@bp.route("/support", methods=["GET", "POST"])
@login_required
def support():
    """User support ticket submission"""
    if not g.user:
        flash("You must be logged in to submit a support ticket.", "error")
        return redirect(url_for("auth.login"))
    
    from forms import SupportTicketForm
    from datetime import datetime
    
    form = SupportTicketForm()
    
    if form.validate_on_submit():
        try:
            ticket_data = {
                'user_id': g.user['id'],
                'issue_description': form.issue_description.data,
                'status': 'open',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            ticket = current_app.db.add('Support_Tickets', ticket_data)
            
            # Notify all admin users
            all_users = current_app.db.get_all('Users')
            admin_users = [u for u in all_users if u.get('role') == 'admin']
            for admin in admin_users:
                current_app.db.add('Notifications', {
                    'user_id': admin['id'],
                    'notification_type': 'in_app',
                    'message': f'New support ticket #{ticket["id"]} submitted by {g.user["name"]}'
                })
            
            flash('Your support ticket has been submitted successfully. Our team will get back to you soon.', 'success')
            return redirect(url_for('profile.support_tickets'))
        except Exception as e:
            flash(f'Error submitting ticket: {str(e)}', 'error')
    
    return render_template("profile/support.html", form=form)

@bp.route("/support/tickets")
@login_required
def support_tickets():
    """View user's support tickets"""
    if not g.user:
        return redirect(url_for("auth.login"))
    
    tickets = current_app.db.find_by_attribute("Support_Tickets", "user_id", g.user["id"])
    tickets.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return render_template("profile/support_tickets.html", tickets=tickets)

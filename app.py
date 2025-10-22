from flask import Flask, render_template, redirect, url_for, g, session
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment
from data_manager import DataManager
import auth
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    
    # Set secret key if not set in config
    if not app.secret_key:
        app.secret_key = os.urandom(24)
    
    # Enable CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize Flask-Moment
    Moment(app)
    
    # Initialize DataManager
    app.db = DataManager(app.config["JSON_DATABASE_DIR"])
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    
    import services
    app.register_blueprint(services.bp)
    
    import bookings
    app.register_blueprint(bookings.bp)
    
    import chat
    app.register_blueprint(chat.bp)
    
    import admin
    app.register_blueprint(admin.bp)
    
    import profile
    app.register_blueprint(profile.bp)
    
    @app.route("/")
    def index():
        if g.user and "role" in g.user:
            if g.user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif g.user["role"] == "service_provider":
                return redirect(url_for("provider_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        
        # Calculate real platform statistics
        all_users = app.db.get_all("Users")
        all_reviews = app.db.get_all("Reviews")
        all_bookings = app.db.get_all("Bookings")
        
        # Count active users (not banned/suspended)
        active_users = len([u for u in all_users if u.get('status') == 'active'])
        total_reviews = len(all_reviews)
        
        # Calculate average rating from all reviews
        if total_reviews > 0:
            avg_rating = sum([r.get('rating', 0) for r in all_reviews]) / total_reviews
        else:
            avg_rating = 0
        
        platform_stats = {
            'total_users': active_users,
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 1),
            'total_bookings': len([b for b in all_bookings if b.get('booking_status') == 'completed'])
        }
        
        return render_template("index.html", platform_stats=platform_stats)
    
    @app.route("/user_dashboard")
    def user_dashboard():
        if not g.user or ("role" not in g.user) or (g.user["role"] != "user"):
            return redirect(url_for("auth.login"))

        user_id = g.user["id"]
        all_bookings = app.db.get_all("Bookings")
        user_bookings = [b for b in all_bookings if b["user_id"] == user_id]

        # Calculate stats
        total_bookings = len(user_bookings)
        pending_bookings = len([b for b in user_bookings if b["booking_status"] == "pending"])
        completed_bookings = len([b for b in user_bookings if b["booking_status"] == "completed"])
        favorite_services = len(app.db.find_by_attribute("Favorites", "user_id", user_id))

        stats = {
            "total_bookings": total_bookings,
            "pending_bookings": pending_bookings,
            "completed_bookings": completed_bookings,
            "favorite_services": favorite_services
        }

        # Get recommended services with provider and rating information
        # Only show approved/active services from active providers with rating > 4.5
        all_services = app.db.get_all("Services")
        recommended_services = []
        
        for service in all_services:
            # Only show approved/active services
            if service.get('status') not in ['active', 'approved']:
                continue
                
            provider = app.db.get_by_id("Users", service.get("provider_id"))
            
            # Only show services from active providers
            if not provider or provider.get('status') != 'active':
                continue
            
            # Fetch bookings for this service to get related reviews
            related_bookings = app.db.find_by_attribute("Bookings", "service_id", service.get("id"))
            reviews = []
            for booking in related_bookings:
                review = app.db.get_by_id("Reviews", booking.get("id"))
                if review:
                    reviews.append(review)
            
            average_rating = sum([r.get("rating", 0) for r in reviews]) / len(reviews) if reviews else 0
            
            # Only show services with rating > 4.5
            if average_rating <= 4.5:
                continue
            
            category = app.db.get_by_id("Service_Categories", service.get("category_id")) if service.get("category_id") else None
            recommended_services.append({
                "id": service["id"],
                "service_name": service["service_name"],
                "category_name": category.get("category_name") if category else "Unknown Category",
                "price": service.get("price", 0.00),
                "provider_name": provider.get("name", "Unknown Provider") if provider else "Unknown Provider",
                "rating": round(average_rating, 1)
            })
        
        # Limit to top 4 recommended services
        recommended_services = recommended_services[:4]

        # Prepare bookings data for display with debug printing
        bookings_display = []
        for booking in user_bookings:
            service = app.db.get_by_id("Services", booking["service_id"])
            provider = app.db.get_by_id("Users", booking["provider_id"])
            if service and provider:
                print(f"Debug - Provider data for booking {booking['id']}: {provider}")
                print(f"Debug - Provider name: {provider.get('name')}")
                bookings_display.append({
                    "id": booking["id"],
                    "service_name": service["service_name"],
                    "provider_name": provider.get("name", "Unknown Provider"),  # Flattened to root level
                    "booking_date": booking["booking_date"],
                    "booking_time": booking["booking_date"].split("T")[1][:5] if "booking_date" in booking and "T" in booking["booking_date"] else "N/A",
                    "status": booking["booking_status"]
                })
        
        return render_template("user_dashboard.html", stats=stats, bookings=bookings_display, recommended_services=recommended_services)

    @app.route("/provider_dashboard")
    def provider_dashboard():
        if not g.user or g.user["role"] != "service_provider":
            return redirect(url_for("auth.login"))

        provider_id = g.user["id"]
        all_services = app.db.get_all("Services")
        my_services = [s for s in all_services if s["provider_id"] == provider_id]

        all_bookings = app.db.get_all("Bookings")
        provider_bookings = [b for b in all_bookings if b["provider_id"] == provider_id]

        all_reviews = app.db.get_all("Reviews")
        my_reviews = [r for r in all_reviews if r["provider_id"] == provider_id]

        # Calculate provider stats
        total_services = len(my_services)
        total_bookings = len(provider_bookings)
        average_rating = sum([r["rating"] for r in my_reviews]) / len(my_reviews) if my_reviews else 0

        # Calculate total_earnings using service price
        total_earnings = 0
        for b in provider_bookings:
            if b["booking_status"] == "completed":
                service = app.db.get_by_id("Services", b["service_id"])
                if service:
                    total_earnings += service["price"]

        # Calculate real response rate (% of bookings accepted or rejected vs pending)
        responded_bookings = len([b for b in provider_bookings if b["booking_status"] in ["accepted", "rejected", "completed", "cancelled"]])
        response_rate = (responded_bookings / total_bookings * 100) if total_bookings else 0
        
        # Calculate real completion rate
        completion_rate = len([b for b in provider_bookings if b["booking_status"] == "completed"]) / total_bookings * 100 if total_bookings else 0
        
        # Calculate real customer satisfaction (% of 4+ star reviews)
        high_rated_reviews = len([r for r in my_reviews if r.get("rating", 0) >= 4])
        satisfaction_rate = (high_rated_reviews / len(my_reviews) * 100) if my_reviews else 0

        provider_stats = {
            "total_services": total_services,
            "total_bookings": total_bookings,
            "average_rating": round(average_rating, 1),
            "total_earnings": round(total_earnings, 2),
            "response_rate": response_rate,
            "completion_rate": round(completion_rate, 1),
            "satisfaction_rate": satisfaction_rate
        }

        # Prepare booking requests data for display
        booking_requests = []
        for booking in provider_bookings:
            user = app.db.get_by_id("Users", booking["user_id"])
            service = app.db.get_by_id("Services", booking["service_id"])
            if user and service:
                booking_requests.append({
                    "id": booking["id"],
                    "service_name": service["service_name"],
                    "user_name": user["name"],
                    "booking_date": booking["booking_date"][:10] if booking.get("booking_date") else "N/A",
                    "booking_time": booking["booking_date"].split("T")[1][:5] if booking.get("booking_date") and "T" in booking["booking_date"] else "N/A",
                    "status": booking["booking_status"]
                })
        
        # Prepare my services data for display
        my_services_display = []
        for service in my_services:
            category = app.db.get_by_id("Service_Categories", service.get("category_id"))
            my_services_display.append({
                "id": service["id"],
                "service_name": service["service_name"],
                "category_name": category.get("category_name") if category else "Unknown Category",
                "status": service["status"],
                "views": service.get("views", 0),
                "price": service["price"]
            })

        # Prepare recent reviews data for display
        recent_reviews = []
        for review in my_reviews:
            user = app.db.get_by_id("Users", review["user_id"])
            if user:
                recent_reviews.append({
                    "user_name": user["name"],
                    "rating": review["rating"],
                    "comment": review["comment"],
                    "created_at": review["created_at"]
                })

        return render_template("provider_dashboard.html", provider_stats=provider_stats, booking_requests=booking_requests, my_services=my_services_display, recent_reviews=recent_reviews)
    
    @app.route("/admin_dashboard")
    def admin_dashboard():
        return render_template("admin_dashboard.html")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
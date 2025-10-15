
from datetime import datetime

def get_current_timestamp():
    return datetime.now().isoformat()

class User:
    def __init__(self, name, email, contact_number, nid_number, password_hash, role,
                 email_verified=False, nid_verified=False, status=\'active\',
                 profile_picture_url=None, age=None, profession=None, address=None,
                 professional_description=None, expertise=None, preferred_locations=None,
                 portfolio_url=None, created_at=None, updated_at=None):
        self.name = name
        self.email = email
        self.contact_number = contact_number
        self.nid_number = nid_number
        self.password_hash = password_hash
        self.role = role
        self.email_verified = email_verified
        self.nid_verified = nid_verified
        self.status = status
        self.profile_picture_url = profile_picture_url
        self.age = age
        self.profession = profession
        self.address = address
        self.professional_description = professional_description
        self.expertise = expertise
        self.preferred_locations = preferred_locations
        self.portfolio_url = portfolio_url
        self.created_at = created_at if created_at else get_current_timestamp()
        self.updated_at = updated_at if updated_at else get_current_timestamp()

    def to_dict(self):
        return self.__dict__

class ServiceCategory:
    def __init__(self, category_name, description=None):
        self.category_name = category_name
        self.description = description

    def to_dict(self):
        return self.__dict__

class Service:
    def __init__(self, category_id, provider_id, service_name, price, description=None, location=None):
        self.category_id = category_id
        self.provider_id = provider_id
        self.service_name = service_name
        self.description = description
        self.price = price
        self.location = location

    def to_dict(self):
        return self.__dict__

class Booking:
    def __init__(self, user_id, service_id, provider_id, service_date, booking_status=\'pending\',
                 booking_date=None, otp_code=None):
        self.user_id = user_id
        self.service_id = service_id
        self.provider_id = provider_id
        self.booking_status = booking_status
        self.booking_date = booking_date if booking_date else get_current_timestamp()
        self.service_date = service_date
        self.otp_code = otp_code

    def to_dict(self):
        return self.__dict__

class Payment:
    def __init__(self, booking_id, payment_method, payment_amount, platform_fee, total_amount,
                 transaction_id=None, payment_status=\'pending\', payment_date=None):
        self.booking_id = booking_id
        self.payment_method = payment_method
        self.payment_amount = payment_amount
        self.platform_fee = platform_fee
        self.total_amount = total_amount
        self.transaction_id = transaction_id
        self.payment_status = payment_status
        self.payment_date = payment_date if payment_date else get_current_timestamp()

    def to_dict(self):
        return self.__dict__

class ChatMessage:
    def __init__(self, booking_id, sender_id, receiver_id, message_content, sent_at=None):
        self.booking_id = booking_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_content = message_content
        self.sent_at = sent_at if sent_at else get_current_timestamp()

    def to_dict(self):
        return self.__dict__

class Review:
    def __init__(self, booking_id, user_id, provider_id, rating, comment=None, created_at=None):
        self.booking_id = booking_id
        self.user_id = user_id
        self.provider_id = provider_id
        self.rating = rating
        self.comment = comment
        self.created_at = created_at if created_at else get_current_timestamp()

    def to_dict(self):
        return self.__dict__

class Notification:
    def __init__(self, user_id, notification_type, message, sent_at=None, is_read=False):
        self.user_id = user_id
        self.notification_type = notification_type
        self.message = message
        self.sent_at = sent_at if sent_at else get_current_timestamp()
        self.is_read = is_read

    def to_dict(self):
        return self.__dict__

class SupportTicket:
    def __init__(self, user_id, issue_description, status=\'open\', created_at=None, updated_at=None):
        self.user_id = user_id
        self.issue_description = issue_description
        self.status = status
        self.created_at = created_at if created_at else get_current_timestamp()
        self.updated_at = updated_at if updated_at else get_current_timestamp()

    def to_dict(self):
        return self.__dict__

class PlatformMetric:
    def __init__(self, total_users, total_providers, total_bookings, total_revenue,
                 service_popularity=None, geographic_data=None, user_behavior=None, recorded_at=None):
        self.total_users = total_users
        self.total_providers = total_providers
        self.total_bookings = total_bookings
        self.total_revenue = total_revenue
        self.service_popularity = service_popularity
        self.geographic_data = geographic_data
        self.user_behavior = user_behavior
        self.recorded_at = recorded_at if recorded_at else get_current_timestamp()

    def to_dict(self):
        return self.__dict__



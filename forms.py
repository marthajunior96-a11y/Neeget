from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DecimalField, DateTimeField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, Optional
import re

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(max=20)])
    nid_number = StringField('NID Number', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=255)])
    role = SelectField('Role', choices=[('user', 'User'), ('service_provider', 'Service Provider')], validators=[DataRequired()])

    def validate_contact_number(self, field):
        if not re.match(r'^[\d\-\+\(\)\s]+$', field.data):
            raise ValidationError('Invalid contact number format.')

    def validate_password(self, field):
        if len(field.data) < 6:
            raise ValidationError('Password must be at least 6 characters long.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class ServiceForm(FlaskForm):
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    service_name = StringField('Service Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description')
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    location = StringField('Location', validators=[Length(max=255)])

class BookingForm(FlaskForm):
    service_date = DateTimeField("Service Date & Time", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[('bkash', 'bKash'), ('nagad', 'Nagad'), ('card', 'Card')], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=255)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(max=20)])

    def validate_contact_number(self, field):
        if not re.match(r'^[\d\-\+\(\)\s]+$', field.data):
            raise ValidationError('Invalid contact number format.')

class ConfirmForm(FlaskForm):
    confirm = HiddenField(default="yes")

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    contact_number = StringField('Contact Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    profession = StringField('Profession', validators=[Optional(), Length(max=100)])
    experience = StringField('Experience', validators=[Optional(), Length(max=50)])
    expertise = StringField('Expertise', validators=[Optional(), Length(max=255)])
    professional_description = TextAreaField('Professional Description', validators=[Optional()])
    preferred_locations = StringField('Preferred Locations', validators=[Optional(), Length(max=255)])
    portfolio_url = StringField('Portfolio URL', validators=[Optional(), Length(max=255)])
    email_notifications = BooleanField('Email Notifications', default=True)
    sms_notifications = BooleanField('SMS Notifications', default=False)
    marketing_emails = BooleanField('Marketing Emails', default=False)
    profile_visibility = BooleanField('Profile Visibility', default=True)
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm Password')

    def validate_contact_number(self, field):
        if field.data and not re.match(r'^[\d\-\+\(\)\s]+$', field.data):
            raise ValidationError('Invalid contact number format.')

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment')

class SupportTicketForm(FlaskForm):
    issue_description = TextAreaField('Issue Description', validators=[DataRequired()])
# Admin Forms
class PlatformSettingForm(FlaskForm):
    setting_value = StringField('Value', validators=[DataRequired()])

class CategoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    display_order = IntegerField('Display Order', validators=[Optional(), NumberRange(min=0)])

class ServiceEditForm(FlaskForm):
    service_name = StringField('Service Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description')
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    location = StringField('Location', validators=[Length(max=255)])
    status = SelectField('Status', choices=[('active', 'Active'), ('inactive', 'Inactive'), ('flagged', 'Flagged'), ('pending_approval', 'Pending Approval')], validators=[DataRequired()])

class FlagForm(FlaskForm):
    reason = TextAreaField('Reason for Flagging', validators=[DataRequired()])

class AdminNoteForm(FlaskForm):
    notes = TextAreaField('Admin Notes', validators=[DataRequired()])

class ReviewModerationForm(FlaskForm):
    admin_response = TextAreaField('Admin Response', validators=[Optional()])

class AdminUserEditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    contact_number = StringField('Contact Number', validators=[Optional(), Length(max=20)])
    nid_number = StringField('NID Number', validators=[Optional(), Length(max=50)])
    role = SelectField('Role', choices=[('user', 'User'), ('service_provider', 'Service Provider'), ('admin', 'Admin')], validators=[DataRequired()])
    status = SelectField('Status', choices=[('active', 'Active'), ('suspended', 'Suspended'), ('banned', 'Banned')], validators=[DataRequired()])
    email_verified = BooleanField('Email Verified')
    nid_verified = BooleanField('NID Verified')

class AdminPasswordResetForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=255)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6, max=255)])

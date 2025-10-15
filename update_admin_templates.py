#!/usr/bin/env python3
"""
Script to update all admin templates to use the new base_admin.html structure
"""

import os
import re

# Templates to update with their details
templates = {
    'user_detail.html': ('User Details', 'fa-user'),
    'edit_user.html': ('Edit User', 'fa-user-edit'),
    'reset_user_password.html': ('Reset Password', 'fa-key'),
    'flag_user.html': ('Flag User', 'fa-flag'),
    'services.html': ('Service Management', 'fa-concierge-bell'),
    'edit_service.html': ('Edit Service', 'fa-edit'),
    'flag_service.html': ('Flag Service', 'fa-flag'),
    'categories.html': ('Category Management', 'fa-layer-group'),
    'add_category.html': ('Add Category', 'fa-plus'),
    'edit_category.html': ('Edit Category', 'fa-edit'),
    'bookings.html': ('Booking Management', 'fa-calendar-check'),
    'reviews.html': ('Review Management', 'fa-star'),
    'flag_review.html': ('Flag Review', 'fa-flag'),
    'respond_review.html': ('Respond to Review', 'fa-reply'),
    'fraud.html': ('Fraud Detection', 'fa-shield-alt'),
    'analytics.html': ('Analytics Dashboard', 'fa-chart-pie'),
    'support.html': ('Support Tickets', 'fa-headset'),
    'activity_log.html': ('Activity Log', 'fa-history'),
    'settings.html': ('Platform Settings', 'fa-cog'),
    'edit_setting.html': ('Edit Setting', 'fa-edit'),
}

template_dir = 'templates/admin/'

def update_template(filename, title, icon):
    filepath = os.path.join(template_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filename}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated (has {% block breadcrumb %})
    if '{% block breadcrumb %}' in content:
        print(f"✓ Already updated: {filename}")
        return True
    
    # Replace {% block admin_content %} with proper structure
    if '{% block admin_content %}' in content:
        # Add title block
        if '{% block title %}' not in content:
            content = re.sub(
                r'{% extends "admin/base_admin.html" %}',
                f'{{% extends "admin/base_admin.html" %}}\n\n{{% block title %}}{title}{{% endblock %}}',
                content
            )
        
        # Add breadcrumb block before admin_content
        breadcrumb_block = f"""
{{% block breadcrumb %}}
<i class="fas {icon}"></i>
<span>{title}</span>
{{% endblock %}}
"""
        content = re.sub(
            r'{% block admin_content %}',
            f'{breadcrumb_block}\n{{% block content %}}',
            content
        )
        
        # Replace {% endblock %} at the end with {% endblock %}
        content = re.sub(r'{% endblock %}$', '{% endblock %}', content.strip()) + '\n'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated: {filename}")
        return True
    else:
        print(f"⚠️  No admin_content block found: {filename}")
        return False

def main():
    print("🚀 Updating admin templates to new base structure...\n")
    
    updated_count = 0
    for filename, (title, icon) in templates.items():
        if update_template(filename, title, icon):
            updated_count += 1
    
    print(f"\n✨ Updated {updated_count}/{len(templates)} templates successfully!")

if __name__ == '__main__':
    main()

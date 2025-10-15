#!/usr/bin/env python3
"""Script to update files for admin panel integration"""

def update_bookings():
    with open('bookings.py', 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Update platform fee calculation
        if 'def calculate_platform_fee(amount):' in line:
            new_lines.append(line)
            i += 1
            new_lines.append(lines[i])  # docstring
            i += 1
            # Replace the return line
            new_lines.append("    db = get_db()\n")
            new_lines.append("    settings = db.get_all('Platform_Settings')\n")
            new_lines.append("    fee_setting = next((s for s in settings if s['setting_key'] == 'platform_fee_percentage'), None)\n")
            new_lines.append("    fee_percentage = float(fee_setting['setting_value']) / 100 if fee_setting else 0.10\n")
            new_lines.append("    return round(amount * fee_percentage, 2)\n")
            i += 1  # skip old return
            continue
        
        # Add user status check in book_service
        if line.strip() == 'if g.user["role"] != "user":':
            new_lines.append(line)
            i += 1
            new_lines.append(lines[i])  # flash line
            i += 1
            new_lines.append(lines[i])  # return line
            i += 1
            new_lines.append(lines[i])  # empty line
            i += 1
            # Add status check
            new_lines.append('    if g.user.get("status") != "active":\n')
            new_lines.append('        flash("Your account is not active. Please contact support.", "error")\n')
            new_lines.append('        return redirect(url_for("services.browse"))\n')
            new_lines.append('    \n')
            continue
        
        # Add provider status check
        if 'provider = db.get_by_id("Users", service.get("provider_id"))' in line:
            new_lines.append(line)
            i += 1
            new_lines.append('    \n')
            new_lines.append('    # Check if provider is active\n')
            new_lines.append('    if not provider or provider.get("status") != "active":\n')
            new_lines.append('        flash("This service provider is not available at the moment.", "error")\n')
            new_lines.append('        return redirect(url_for("services.browse"))\n')
            new_lines.append('    \n')
            new_lines.append('    # Check if service is active\n')
            new_lines.append('    if service.get("status") != "active":\n')
            new_lines.append('        flash("This service is not available at the moment.", "error")\n')
            new_lines.append('        return redirect(url_for("services.browse"))\n')
            new_lines.append('    \n')
            continue
        
        new_lines.append(line)
        i += 1
    
    with open('bookings.py', 'w') as f:
        f.writelines(new_lines)
    print("✓ Updated bookings.py")

if __name__ == '__main__':
    update_bookings()

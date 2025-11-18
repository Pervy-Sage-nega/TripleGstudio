# Site Personnel Roles - Implementation Guide

## Overview
Added customizable site personnel roles system for Site Managers. Roles are managed by admins via Django admin panel.

## Changes Made

### 1. Models (accounts/models.py)
- **New Model**: `SitePersonnelRole` - Customizable roles with dynamic employee ID prefixes
- **Updated Model**: `SiteManagerProfile` - Added `site_role` ForeignKey (nullable for backward compatibility)
- **Updated Methods**: 
  - `generate_employee_id()` - Now uses role prefix (AR, EN, FM, SV) instead of hardcoded SM
  - `get_role_display()` - Returns role display name or default "Site Manager"
  - `__str__()` - Shows role name in string representation

### 2. Admin (accounts/admin.py)
- **New Admin**: `SitePersonnelRoleAdmin` - Manage roles via admin panel
- **Updated Admin**: `SiteManagerProfileAdmin` - Added `site_role` field and filter

### 3. Default Roles Script (create_default_roles.py)
Creates 4 default roles:
- Architect (AR)
- Engineer (EN)
- Foreman (FM)
- Supervisor (SV)

## Setup Instructions

### Step 1: Create Migration
```bash
python manage.py makemigrations accounts
```

### Step 2: Run Migration
```bash
python manage.py migrate accounts
```

### Step 3: Create Default Roles
```bash
python manage.py shell < create_default_roles.py
```

## How It Works

### For Existing Site Managers
- All existing site managers will have `site_role=None`
- They continue working normally with default "Site Manager" title
- Employee IDs remain unchanged (SM-YYYY-NNNN format)

### For New Site Managers
- Admin assigns role during approval process
- Employee ID uses role prefix (e.g., EN-2024-0001 for Engineer)
- Role appears in profile display

### Admin Workflow
1. User registers as site manager (no role selection)
2. Admin reviews registration in Django admin
3. Admin assigns appropriate role from dropdown
4. Admin approves account
5. Employee ID generated with role prefix

## Admin Panel Access

### Manage Roles
- Navigate to: **Admin Panel → Accounts → Site Personnel Roles**
- Add/Edit/Deactivate roles
- Set custom prefixes and display order

### Assign Roles to Site Managers
- Navigate to: **Admin Panel → Accounts → Site Manager Profiles**
- Edit site manager profile
- Select role from "Site role" dropdown
- Save changes

## Benefits

✅ **Fully Customizable** - Add/edit roles without code changes
✅ **Backward Compatible** - Existing site managers unaffected
✅ **Dynamic Employee IDs** - Prefix based on role
✅ **Easy Management** - All via admin panel
✅ **Scalable** - Add role-based permissions later
✅ **No Breaking Changes** - All features continue working

## Future Enhancements

- Add role-based permissions for site diary features
- Add role hierarchy/reporting structure
- Add color coding for visual identification
- Add role-specific dashboard widgets

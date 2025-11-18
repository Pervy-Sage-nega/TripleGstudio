@echo off
echo ========================================
echo Site Personnel Roles Setup
echo ========================================
echo.

echo Step 1: Creating migrations...
python manage.py makemigrations accounts
echo.

echo Step 2: Running migrations...
python manage.py migrate accounts
echo.

echo Step 3: Creating default roles...
python manage.py shell < create_default_roles.py
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Access Django admin panel
echo 2. Navigate to Site Personnel Roles
echo 3. Assign roles to site managers
echo.
pause

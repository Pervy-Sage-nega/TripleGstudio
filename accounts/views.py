from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import timedelta
from .forms import ClientRegisterForm, OTPForm, AdminRegisterForm, AdminLoginForm, AdminOTPForm
from .models import OneTimePassword, AdminProfile, SiteManagerProfile, Profile
from .utils import get_user_role, get_user_dashboard_url, get_appropriate_redirect
from .activity_tracker import UserActivityTracker
@csrf_protect
@never_cache
@transaction.atomic
def client_register_view(request):
    if request.method == "POST":
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    
                    # Generate OTP
                    code = OneTimePassword.generate_code()
                    OneTimePassword.objects.update_or_create(
                        user=user, 
                        defaults={"code": code}
                    )
                    
                    # Send OTP via email
                    print(f"[DEBUG] Sending OTP to: {user.email} from: {settings.DEFAULT_FROM_EMAIL} code: {code}")
                    result = send_mail(
                        "Verify your Triple G account",
                        f"Your OTP code is {code}. It will expire in 10 minutes.",
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    print(f"[DEBUG] send_mail result: {result}")
                    
                    messages.info(request, "Account created! Please verify with the OTP sent to your email.")
                    request.session['pending_user_id'] = user.id
                    return redirect("accounts:client_verify_otp")
                    
            except Exception as e:
                messages.error(request, "Error creating account or sending email. Please try again.")
                # Transaction will automatically rollback on exception
    else:
        form = ClientRegisterForm()
    return render(request, 'client/register.html', {"form": form})

# Client OTP Verification
@csrf_protect
@never_cache
@transaction.atomic
def client_verify_otp(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        messages.error(request, "No pending verification found.")
        return redirect("accounts:client_register")
    
    try:
        user = User.objects.select_for_update().get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid verification session.")
        return redirect("accounts:client_register")
    
    otp_obj = OneTimePassword.objects.filter(user=user).first()
    
    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['otp']
            
            if otp_obj and otp_obj.code == code and not otp_obj.is_expired():
                with transaction.atomic():
                    user.is_active = True
                    user.save()
                    otp_obj.delete()
                    del request.session['pending_user_id']
                    
                # Don't set Django message here - JavaScript will handle the success modal
                return redirect("accounts:client_login")
            else:
                messages.error(request, "Invalid or expired OTP.")
    else:
        form = OTPForm()
    
    return render(request, "client/verify_otp.html", {"form": form, "email": user.email})

# Client Resend OTP
def client_resend_otp(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return redirect("accounts:client_register")
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect("accounts:client_register")
    
    code = OneTimePassword.generate_code()
    OneTimePassword.objects.update_or_create(user=user, defaults={"code": code})
    
    try:
        send_mail(
            "Resend OTP - Triple G account",
            f"Your new OTP code is {code}. It will expire in 10 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        messages.success(request, "A new OTP has been sent to your email.")
    except Exception as e:
        messages.error(request, "Error sending email. Please try again.")
    
    return redirect("accounts:client_verify_otp")

# Client Login
@transaction.atomic
@csrf_protect
def client_login_view(request):
    # Redirect already authenticated clients
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        return redirect(get_user_dashboard_url(request.user))
    
    reg_messages = []
    if request.method == "POST":
        # Check if this is a registration attempt
        if 'register' in request.POST:
            print("[DEBUG] Registration attempt detected")
            from django.contrib.auth.models import User
            from django.core.mail import send_mail
            from .models import OneTimePassword, Profile
            from django.db import IntegrityError

            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('reg_password')
            username = email

            print(f"[DEBUG] Registration data - Name: {first_name} {last_name}, Email: {email}")

            if not all([first_name, last_name, email, password]):
                print("[DEBUG] Missing required fields")
                reg_messages.append({'tags': 'error', 'message': 'Please fill out all fields to register.'})
            # Remove this duplicate check since we handle it below
            # elif User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            #     print(f"[DEBUG] User already exists: {email}")
            #     reg_messages.append({'tags': 'error', 'message': 'This email is already registered. Please try logging in.'})
            else:
                try:
                    print("[DEBUG] Creating new user...")
                    with transaction.atomic():
                        # Check if user already exists (including inactive users)
                        existing_user = User.objects.filter(username=username).first()
                        if existing_user:
                            print(f"[DEBUG] User already exists: {existing_user.username} (Active: {existing_user.is_active})")
                            if not existing_user.is_active:
                                # Reactivate existing inactive user and resend OTP
                                user = existing_user
                                user.first_name = first_name
                                user.last_name = last_name
                                user.set_password(password)
                                user.save()
                                print(f"[DEBUG] Reactivated existing user: {user.username}")
                            else:
                                reg_messages.append({'tags': 'error', 'message': 'This email is already registered and active. Please try logging in.'})
                                return render(request, 'client/login.html', {'reg_messages': reg_messages})
                        else:
                            # Create new user
                            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, is_active=False)
                            print(f"[DEBUG] User created: {user.username} (ID: {user.id})")
                        
                        # Create profile manually (signal is disabled)
                        print(f"[DEBUG] Checking for existing profiles...")
                        existing_profiles = Profile.objects.filter(user=user)
                        print(f"[DEBUG] Found {existing_profiles.count()} existing profiles for user {user.id}")
                        
                        if existing_profiles.exists():
                            profile = existing_profiles.first()
                            print(f"[DEBUG] Using existing profile: {profile.id}")
                        else:
                            print(f"[DEBUG] Creating new profile for user: {user.username}")
                            profile = Profile.objects.create(user=user, role='customer')
                            print(f"[DEBUG] Profile created successfully: {profile.id}")
                        
                        code = OneTimePassword.generate_code()
                        OneTimePassword.objects.update_or_create(user=user, defaults={"code": code})
                        print(f"[DEBUG] OTP generated: {code}")
                        
                        send_mail(
                            "Verify your Triple G account",
                            f"Your OTP code is {code}. It will expire in 10 minutes.",
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )
                        print(f"[DEBUG] OTP email sent to: {user.email}")
                        
                        request.session['pending_user_id'] = user.id
                        print(f"[DEBUG] Session set with user ID: {user.id}")
                        messages.info(request, "Account created! Please verify with the OTP sent to your email.")
                        print("[DEBUG] Redirecting to OTP verification...")
                        return redirect("accounts:client_verify_otp")
                except IntegrityError as e:
                    print(f"[DEBUG] IntegrityError: {e}")
                    reg_messages.append({'tags': 'error', 'message': 'Something went wrong on our end. Please try again.'})
                except Exception as e:
                    print(f"[DEBUG] Exception during registration: {e}")
                    reg_messages.append({'tags': 'error', 'message': 'An unexpected error occurred. Please try again shortly.'})
        
        # Handle login attempt
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    # Clear any existing messages (like logout messages)
                    storage = messages.get_messages(request)
                    storage.used = True
                    
                    # Handle remember me
                    remember = request.POST.get('remember')
                    if remember:
                        request.session.set_expiry(1209600)  # 2 weeks
                    else:
                        request.session.set_expiry(0)  # Session expires when browser closes
                    
                    login(request, user)
                    # The success message will be shown on the home page after redirect
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    
                    # Redirect based on user role
                    dashboard_url = get_user_dashboard_url(user)
                    next_url = request.GET.get('next', dashboard_url)
                    return redirect(next_url)
                else:
                    messages.warning(request, "Your account isn't active. Please check your email to verify your account.")
            else:
                # Use a generic message for security reasons
                messages.error(request, "The email or password you entered is incorrect.")
    return render(request, 'client/login.html', {'reg_messages': reg_messages})

# Client Logout
def client_logout_view(request):
    if request.user.is_authenticated:
        UserActivityTracker.mark_user_offline(request.user)
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('accounts:client_login')

# Admin Authentication Views
@csrf_protect
@never_cache
@transaction.atomic
def admin_register_view(request):
    """Admin registration with approval workflow"""
    if request.method == "POST":
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    
                    # Create admin profile
                    admin_profile = AdminProfile.objects.create(
                        user=user,
                        admin_role='staff',  # Default role
                        approval_status='pending'
                    )
                    
                    # Generate OTP for email verification
                    code = OneTimePassword.generate_code()
                    OneTimePassword.objects.update_or_create(
                        user=user,
                        defaults={"code": code}
                    )
                    
                    # Send verification email
                    send_mail(
                        "Verify your Triple G Admin Account",
                        f"Your admin account verification code is {code}. It will expire in 10 minutes. "
                        f"After verification, your account will be reviewed for approval.",
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    
                    messages.success(
                        request, 
                        "Admin account created! Please check your email for verification code. "
                        "Your account will be reviewed for approval after verification."
                    )
                    request.session['pending_admin_id'] = user.id
                    return redirect("accounts:admin_verify_otp")
                    
            except Exception as e:
                messages.error(request, "Error creating admin account. Please try again.")
                print(f"[ERROR] Admin registration failed: {e}")
    else:
        form = AdminRegisterForm()
    
    return render(request, 'admin/register.html', {"form": form})


@csrf_protect
@never_cache
def admin_login_view(request):
    """Admin login with enhanced security checks"""
    # Redirect already authenticated admin users
    if request.user.is_authenticated and hasattr(request.user, 'adminprofile'):
        admin_profile = request.user.adminprofile
        if admin_profile.can_login():
            return redirect(get_user_dashboard_url(request.user))
    
    print(f"[DEBUG] admin_login_view called! Method: {request.method}")
    print(f"[DEBUG] Request path: {request.path}")
    print(f"[DEBUG] Request META: {request.META.get('HTTP_HOST', 'No host')}")
    
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember', False)
            
            # Get client IP for logging
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                       request.META.get('REMOTE_ADDR', ''))
            if client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            try:
                user = User.objects.get(email=email, is_staff=True)
                
                # Check if user has admin profile
                if not hasattr(user, 'adminprofile'):
                    messages.error(request, "Invalid admin credentials.")
                    return render(request, 'admin/custom_admin_login.html', {'form': form})
                
                admin_profile = user.adminprofile
                
                # Check if account is locked
                if admin_profile.is_account_locked():
                    messages.error(request, "Account is temporarily locked. Please try again later.")
                    return render(request, 'admin/custom_admin_login.html', {'form': form})
                
                # Authenticate user
                auth_user = authenticate(request, username=email, password=password)
                
                if auth_user is not None:
                    # Check if admin can login (approved, active, not suspended)
                    if admin_profile.can_login():
                        # Reset failed login attempts
                        admin_profile.failed_login_attempts = 0
                        admin_profile.last_login_ip = client_ip
                        admin_profile.save()
                        
                        # Set session expiry based on remember me
                        if remember:
                            request.session.set_expiry(1209600)  # 2 weeks
                        else:
                            request.session.set_expiry(0)  # Session expires when browser closes
                        
                        # Clear any existing messages (like logout messages)
                        storage = messages.get_messages(request)
                        storage.used = True
                        
                        login(request, auth_user)
                        messages.success(request, f"Welcome back, {auth_user.get_full_name()}!")
                        
                        # Redirect based on admin role (admin vs site manager)
                        dashboard_url = get_user_dashboard_url(auth_user)
                        next_url = request.GET.get('next', dashboard_url)
                        return redirect(next_url)
                    else:
                        if admin_profile.approval_status == 'pending':
                            # Redirect to pending approval page for better UX
                            messages.warning(request, 
                                "Your admin account hasn't been approved yet. Please wait for administrator approval. "
                                "You will receive an email notification once your account is approved.")
                            return render(request, 'admin/pending_approval.html', {
                                'user': user,
                                'admin_profile': admin_profile
                            })
                        elif admin_profile.approval_status == 'denied':
                            messages.error(request, 
                                "Your admin account application has been denied. "
                                "Please contact the system administrator for more information.")
                        elif admin_profile.approval_status == 'suspended':
                            messages.error(request, 
                                "Your admin account has been suspended. "
                                "Please contact the system administrator to resolve this issue.")
                        else:
                            messages.error(request, 
                                "Your admin account is not active. "
                                "Please contact the system administrator for assistance.")
                else:
                    # Invalid password - increment failed attempts
                    admin_profile.failed_login_attempts += 1
                    
                    # Lock account after 5 failed attempts for 30 minutes
                    if admin_profile.failed_login_attempts >= 5:
                        admin_profile.account_locked_until = timezone.now() + timedelta(minutes=30)
                        messages.error(request, "Too many failed attempts. Account locked for 30 minutes.")
                    else:
                        remaining = 5 - admin_profile.failed_login_attempts
                        messages.error(request, f"Invalid credentials. {remaining} attempts remaining.")
                    
                    admin_profile.save()
                    
            except User.DoesNotExist:
                messages.error(request, "Invalid admin credentials.")
                
    else:
        form = AdminLoginForm()
    
    print(f"[DEBUG] Rendering custom_admin_login.html template")
    print(f"[DEBUG] Template dirs: {settings.TEMPLATES[0]['DIRS']}")
    
    # Try to render with explicit template path to avoid conflicts
    from django.template.loader import get_template
    try:
        template = get_template('admin/custom_admin_login.html')
        print(f"[DEBUG] Found template: {template.origin.name}")
    except Exception as e:
        print(f"[DEBUG] Template error: {e}")
    
    return render(request, 'admin/custom_admin_login.html', {'form': form})


@csrf_protect
@never_cache
@transaction.atomic
def admin_verify_otp(request):
    """Admin OTP verification"""
    user_id = request.session.get('pending_admin_id')
    if not user_id:
        messages.error(request, "No pending admin verification found.")
        return redirect("accounts:admin_register")
    
    try:
        user = User.objects.select_for_update().get(id=user_id, is_staff=True)
    except User.DoesNotExist:
        messages.error(request, "Invalid admin verification session.")
        return redirect("accounts:admin_register")
    
    otp_obj = OneTimePassword.objects.filter(user=user).first()
    
    if request.method == "POST":
        form = AdminOTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['otp']
            
            if otp_obj and otp_obj.code == code and not otp_obj.is_expired():
                with transaction.atomic():
                    # Mark user as verified (but still pending approval)
                    user.is_active = True
                    user.save()
                    
                    # Update admin profile
                    admin_profile = user.adminprofile
                    admin_profile.approval_status = 'pending'  # Still needs approval
                    admin_profile.save()
                    
                    otp_obj.delete()
                    del request.session['pending_admin_id']
                    
                messages.success(
                    request, 
                    "Email verified successfully! Your admin account is now pending approval. "
                    "You will be notified by email once approved."
                )
                return redirect("accounts:admin_login")
            else:
                messages.error(request, "Invalid or expired verification code.")
    else:
        form = AdminOTPForm()
    
    return render(request, "admin/adminverify_otp.html", {"form": form, "email": user.email})


def admin_resend_otp(request):
    """Resend OTP for admin verification"""
    user_id = request.session.get('pending_admin_id')
    if not user_id:
        return redirect("accounts:admin_register")
    
    try:
        user = User.objects.get(id=user_id, is_staff=True)
    except User.DoesNotExist:
        return redirect("accounts:admin_register")
    
    code = OneTimePassword.generate_code()
    OneTimePassword.objects.update_or_create(user=user, defaults={"code": code})
    
    try:
        send_mail(
            "Resend Admin OTP - Triple G BuildHub",
            f"Your new admin verification code is {code}. It will expire in 10 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        messages.success(request, "A new verification code has been sent to your email.")
    except Exception as e:
        messages.error(request, "Error sending email. Please try again.")
    
    return redirect("accounts:admin_verify_otp")


def admin_logout_view(request):
    """Admin logout"""
    if request.user.is_authenticated and hasattr(request.user, 'adminprofile'):
        UserActivityTracker.mark_user_offline(request.user)
        logout(request)
        messages.info(request, "You have been successfully logged out from admin panel.")
    return redirect('accounts:admin_login')

# Site Manager authentication views (handles blog creation)
@csrf_protect
@never_cache
def sitemanager_login_view(request):
    """Site Manager login view with authentication logic"""
    # Redirect already authenticated site managers
    if request.user.is_authenticated and hasattr(request.user, 'sitemanagerprofile'):
        sitemanager_profile = request.user.sitemanagerprofile
        if sitemanager_profile.can_login():
            return redirect(get_user_dashboard_url(request.user))
    
    print(f"[DEBUG] sitemanager_login_view called - Method: {request.method}")
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print(f"[DEBUG] Login attempt - Email: {email}, Password length: {len(password) if password else 0}")
        
        if not email or not password:
            print("[DEBUG] Missing email or password")
            messages.error(request, 'Please enter both email and password.')
            return render(request, 'sitemanager/login.html')
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            print(f"[DEBUG] Found user: {user.username}, Active: {user.is_active}")
            
            # Authenticate user
            auth_user = authenticate(request, username=user.username, password=password)
            print(f"[DEBUG] Authentication result: {auth_user}")
            
            if auth_user is not None:
                print(f"[DEBUG] Authentication successful for: {auth_user.username}")
                
                # Check if user has site manager profile
                if hasattr(auth_user, 'sitemanagerprofile'):
                    sitemanager_profile = auth_user.sitemanagerprofile
                    print(f"[DEBUG] Site manager profile found - Status: {sitemanager_profile.approval_status}")
                    
                    # Check if site manager is approved
                    if sitemanager_profile.approval_status == 'approved':
                        # Clear any existing messages (like logout messages)
                        storage = messages.get_messages(request)
                        storage.used = True
                        
                        # Handle remember me
                        remember = request.POST.get('remember')
                        if remember:
                            request.session.set_expiry(1209600)  # 2 weeks
                        else:
                            request.session.set_expiry(0)  # Session expires when browser closes
                        
                        # Login successful
                        login(request, auth_user)
                        messages.success(request, f'Welcome back, {auth_user.get_full_name()}!')
                        print(f"[DEBUG] Login successful, redirecting to dashboard")
                        
                        # Redirect to site manager dashboard
                        from .utils import get_user_role
                        user_role = get_user_role(auth_user)
                        print(f"[DEBUG] User role detected: {user_role}")
                        dashboard_url = get_user_dashboard_url(auth_user)
                        print(f"[DEBUG] Dashboard URL: {dashboard_url}")
                        next_url = request.GET.get('next', dashboard_url)
                        print(f"[DEBUG] Final redirect URL: {next_url}")
                        return redirect(next_url)
                    elif sitemanager_profile.approval_status == 'pending':
                        print(f"[DEBUG] Account pending approval")
                        messages.warning(request, 'Your account is still pending approval. Please wait for admin approval.')
                        return redirect('accounts:sitemanager_pending_approval')
                    elif sitemanager_profile.approval_status == 'denied':
                        print(f"[DEBUG] Account denied")
                        messages.error(request, 'Your account has been denied access.')
                    else:
                        print(f"[DEBUG] Account suspended")
                        messages.error(request, 'Your account is suspended.')
                else:
                    print(f"[DEBUG] No site manager profile found")
                    messages.error(request, 'Invalid credentials for site manager access.')
            else:
                print(f"[DEBUG] Authentication failed for user: {user.username}")
                messages.error(request, 'The email or password you entered is incorrect.')
                
        except User.DoesNotExist:
            print(f"[DEBUG] User not found with email: {email}")
            messages.error(request, 'The email or password you entered is incorrect.')
        except Exception as e:
            print(f"[ERROR] Site manager login error: {e}")
            messages.error(request, 'An error occurred during login. Please try again.')
    
    return render(request, 'sitemanager/login.html')

def sitemanager_register_view(request):
    """Site Manager registration view"""
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        
        # Basic validation
        if not all([first_name, last_name, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'sitemanager/register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'sitemanager/register.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'sitemanager/register.html')
        
        try:
            # Create user account
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_active=False  # Will be activated after OTP verification
            )
            
            # Create SiteManagerProfile for Site Manager
            sitemanager_profile = SiteManagerProfile.objects.create(
                user=user,
                approval_status='pending',
                department='Site Management'
            )
            
            # Generate and send OTP
            otp_code = OneTimePassword.generate_code()
            otp_instance, created = OneTimePassword.objects.get_or_create(
                user=user,
                defaults={'code': otp_code}
            )
            if not created:
                # Update existing OTP with new code
                otp_instance.code = otp_code
                otp_instance.created_at = timezone.now()
                otp_instance.save()
            
            # Send OTP email
            subject = 'Verify Your Site Manager Account - Triple G BuildHub'
            message = f'''
            Hello {first_name},
            
            Thank you for registering as a Site Manager with Triple G BuildHub.
            
            Your verification code is: {otp_instance.code}
            
            This code will expire in 10 minutes.
            
            Best regards,
            Triple G BuildHub Team
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            # Store user ID in session for OTP verification
            request.session['registration_user_id'] = user.id
            request.session['registration_email'] = email
            
            messages.success(request, 'Registration successful! Please check your email for the verification code.')
            return redirect('accounts:sitemanager_verify_otp')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'sitemanager/register.html')
    
    return render(request, 'sitemanager/register.html')

def sitemanager_verify_otp(request):
    """Site Manager OTP verification view"""
    user_id = request.session.get('registration_user_id')
    email = request.session.get('registration_email')
    
    # Debug: Print session data (remove in production)
    # print(f"DEBUG: user_id = {user_id}, email = {email}")
    # print(f"DEBUG: session keys = {list(request.session.keys())}")
    
    if not user_id:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('accounts:sitemanager_register')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        
        if not otp_code:
            messages.error(request, 'Please enter the OTP code.')
            return render(request, 'sitemanager/verify_otp.html', {'email': email})
        
        try:
            user = User.objects.get(id=user_id)
            otp_instance = OneTimePassword.objects.get(
                user=user,
                code=otp_code
            )
            
            if otp_instance.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return render(request, 'sitemanager/verify_otp.html', {'email': email})
            
            # Delete OTP after successful verification
            otp_instance.delete()
            
            # Activate user account
            user.is_active = True
            user.save()
            
            # Clear session data
            request.session.pop('registration_user_id', None)
            request.session.pop('registration_email', None)
            
            messages.success(request, 'Email verified successfully! Your account is pending admin approval.')
            return redirect('accounts:sitemanager_pending_approval')
            
        except OneTimePassword.DoesNotExist:
            messages.error(request, 'Invalid OTP code. Please try again.')
            return render(request, 'sitemanager/verify_otp.html', {'email': email})
        except User.DoesNotExist:
            messages.error(request, 'User not found. Please register again.')
            return redirect('accounts:sitemanager_register')
    
    return render(request, 'sitemanager/verify_otp.html', {'email': email})

def sitemanager_pending_approval(request):
    """Site Manager pending approval view"""
    return render(request, 'sitemanager/pending_approval.html')

def sitemanager_logout_view(request):
    """Site Manager logout"""
    if request.user.is_authenticated and hasattr(request.user, 'sitemanagerprofile'):
        UserActivityTracker.mark_user_offline(request.user)
        logout(request)
        messages.info(request, "You have been successfully logged out.")
    return redirect('accounts:sitemanager_login')

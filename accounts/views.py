from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import User, EmailVerification


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        role = request.POST.get('role', 'STUDENT')
        
        # Validation
        errors = []
        
        if not email:
            errors.append('Email is required')
        elif User.objects.filter(email=email).exists():
            errors.append('Email already exists')
        
        if not username:
            errors.append('Username is required')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already exists')
        
        if not password:
            errors.append('Password is required')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if password != password_confirm:
            errors.append('Passwords do not match')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html', {
                'email': email,
                'username': username,
                'role': role
            })
        
        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                role=role,
                is_verified=False  # User is not verified yet
            )
            
            # Send verification email
            if user.send_verification_email():
                messages.success(request, f'Registration successful! Please check your email ({email}) for the verification code.')
                # Store user email in session for verification page
                request.session['verification_email'] = email
                return redirect('accounts:verify_email')
            else:
                messages.error(request, 'Registration successful but failed to send verification email. Please contact support.')
                return redirect('accounts:login')
                
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'accounts/register.html', {
                'email': email,
                'username': username,
                'role': role
            })
    
    return render(request, 'accounts/register.html')


def verify_email_view(request):
    """Email verification page"""
    email = request.session.get('verification_email')
    
    if not email:
        messages.error(request, 'Please register first')
        return redirect('accounts:register')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('accounts:register')
    
    if user.is_verified:
        messages.info(request, 'Your email is already verified. You can login now.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        if not code:
            messages.error(request, 'Please enter the verification code')
            return render(request, 'accounts/verify_email.html', {'email': email})
        
        # Get the latest verification code for this user
        verification = EmailVerification.objects.filter(
            user=user,
            is_used=False
        ).order_by('-created_at').first()
        
        if not verification:
            messages.error(request, 'No verification code found. Please request a new one.')
            return render(request, 'accounts/verify_email.html', {'email': email})
        
        if verification.is_expired():
            messages.error(request, 'Verification code has expired. Please request a new one.')
            return render(request, 'accounts/verify_email.html', {'email': email})
        
        if verification.code == code:
            # Mark verification as used
            verification.is_used = True
            verification.save()
            
            # Mark user as verified
            user.is_verified = True
            user.save()
            
            # Auto-login the user
            login(request, user)
            
            # Clear session
            if 'verification_email' in request.session:
                del request.session['verification_email']
            
            messages.success(request, f'Email verified successfully! Welcome, {user.username}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
            return render(request, 'accounts/verify_email.html', {'email': email})
    
    return render(request, 'accounts/verify_email.html', {'email': email})


def resend_verification_view(request):
    """Resend verification code"""
    if request.method != 'POST':
        return redirect('accounts:verify_email')
    
    email = request.session.get('verification_email')
    
    if not email:
        messages.error(request, 'Please register first')
        return redirect('accounts:register')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('accounts:register')
    
    if user.is_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('accounts:login')
    
    if user.send_verification_email():
        messages.success(request, 'Verification code has been resent to your email.')
    else:
        messages.error(request, 'Failed to send verification email. Please try again later.')
    
    return redirect('accounts:verify_email')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user:
            # Check if user is verified
            if not user.is_verified:
                messages.warning(request, 'Please verify your email before logging in. Check your email for the verification code.')
                request.session['verification_email'] = email
                return redirect('accounts:verify_email')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('accounts:login')


def forgot_password_view(request):
    """Step 1: Request password reset - user enters email"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your email address')
            return render(request, 'accounts/forgot_password.html')
        
        try:
            user = User.objects.get(email=email)
            
            # Send password reset email
            if user.send_password_reset_email():
                messages.success(request, f'A 4-digit verification code has been sent to {email}')
                # Store email in session for next step
                request.session['reset_email'] = email
                return redirect('accounts:verify_reset_code')
            else:
                messages.error(request, 'Failed to send reset code. Please try again later.')
                return render(request, 'accounts/forgot_password.html', {'email': email})
                
        except User.DoesNotExist:
            # For security, don't reveal if email exists or not
            messages.success(request, f'If an account exists with {email}, a verification code has been sent.')
            return render(request, 'accounts/forgot_password.html')
    
    return render(request, 'accounts/forgot_password.html')


def verify_reset_code_view(request):
    """Step 2: Verify the 4-digit code"""
    email = request.session.get('reset_email')
    
    if not email:
        messages.error(request, 'Please start the password reset process first')
        return redirect('accounts:forgot_password')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'Invalid session. Please start again.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Handle resend code
        if action == 'resend':
            if user.send_password_reset_email():
                messages.success(request, 'A new verification code has been sent to your email')
            else:
                messages.error(request, 'Failed to resend code. Please try again.')
            return render(request, 'accounts/verify_reset_code.html', {'email': email})
        
        # Handle code verification
        code = request.POST.get('code', '').strip()
        
        if not code:
            messages.error(request, 'Please enter the verification code')
            return render(request, 'accounts/verify_reset_code.html', {'email': email})
        
        # Import here to avoid circular import
        from .models import PasswordReset
        
        # Get the latest password reset code for this user
        reset = PasswordReset.objects.filter(
            user=user,
            is_used=False
        ).order_by('-created_at').first()
        
        if not reset:
            messages.error(request, 'No verification code found. Please request a new one.')
            return render(request, 'accounts/verify_reset_code.html', {'email': email})
        
        if reset.is_expired():
            messages.error(request, 'Verification code has expired. Please request a new one.')
            return render(request, 'accounts/verify_reset_code.html', {'email': email})
        
        if reset.code == code:
            # Mark code as used
            reset.is_used = True
            reset.save()
            
            # Store verified status in session
            request.session['reset_verified'] = True
            
            messages.success(request, 'Code verified! Please set your new password.')
            return redirect('accounts:reset_password')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
            return render(request, 'accounts/verify_reset_code.html', {'email': email})
    
    return render(request, 'accounts/verify_reset_code.html', {'email': email})


def reset_password_view(request):
    """Step 3: Set new password"""
    email = request.session.get('reset_email')
    verified = request.session.get('reset_verified')
    
    if not email or not verified:
        messages.error(request, 'Please complete the verification process first')
        return redirect('accounts:forgot_password')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'Invalid session. Please start again.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # Validation
        errors = []
        
        if not password:
            errors.append('Password is required')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if password != password_confirm:
            errors.append('Passwords do not match')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/reset_password.html', {'email': email})
        
        try:
            # Set new password
            user.set_password(password)
            user.save()
            
            # Clear session data
            if 'reset_email' in request.session:
                del request.session['reset_email']
            if 'reset_verified' in request.session:
                del request.session['reset_verified']
            
            messages.success(request, 'Password has been reset successfully! You can now login with your new password.')
            return redirect('accounts:login')
            
        except Exception as e:
            messages.error(request, f'Failed to reset password: {str(e)}')
            return render(request, 'accounts/reset_password.html', {'email': email})
    
    return render(request, 'accounts/reset_password.html', {'email': email})

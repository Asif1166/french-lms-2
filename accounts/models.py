from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('INSTRUCTOR', 'Instructor'),
        ('ADMIN', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def is_student(self):
        return self.role == 'STUDENT'
    
    def is_instructor(self):
        return self.role == 'INSTRUCTOR'
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    def send_verification_email(self):
        """Send verification code to user's email"""
        # Delete old verification codes
        EmailVerification.objects.filter(user=self).delete()
        
        # Generate 6-digit verification code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Create verification record
        verification = EmailVerification.objects.create(
            user=self,
            code=code
        )
        
        # Send email
        subject = 'Verify Your Email - French LMS'
        message = f'''
Hello {self.username},

Thank you for registering with French LMS!

Your verification code is: {code}

This code will expire in 10 minutes.

If you didn't create an account, please ignore this email.

Best regards,
French LMS Team
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_password_reset_email(self):
        """Send password reset code to user's email"""
        # Delete old password reset codes for this user
        from .models import PasswordReset
        PasswordReset.objects.filter(user=self).delete()
        
        # Generate 4-digit reset code
        code = ''.join(random.choices(string.digits, k=4))
        
        # Create password reset record
        reset = PasswordReset.objects.create(
            user=self,
            code=code
        )
        
        # Send email
        subject = 'Password Reset Code - French LMS'
        message = f'''
Hello {self.username},

You requested to reset your password for French LMS.

Your password reset code is: {code}

This code will expire in 10 minutes.

If you didn't request a password reset, please ignore this email and your password will remain unchanged.

Best regards,
French LMS Team
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending password reset email: {e}")
            return False


class EmailVerification(models.Model):
    """
    Email verification codes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_verifications'
        ordering = ['-created_at']
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
    
    def __str__(self):
        return f"{self.user.email} - {self.code}"
    
    def is_expired(self):
        """Check if verification code is expired (10 minutes)"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    def is_valid(self):
        """Check if verification code is valid"""
        return not self.is_used and not self.is_expired()


class PasswordReset(models.Model):
    """
    Password reset verification codes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_resets'
        ordering = ['-created_at']
        verbose_name = 'Password Reset'
        verbose_name_plural = 'Password Resets'
    
    def __str__(self):
        return f"{self.user.email} - {self.code}"
    
    def is_expired(self):
        """Check if reset code is expired (10 minutes)"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    def is_valid(self):
        """Check if reset code is valid"""
        return not self.is_used and not self.is_expired()

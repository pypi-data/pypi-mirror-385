#!/usr/bin/env python3
"""
Test file with secure Django code (no security issues).
Based on OWASP secure coding practices.
Expected: Should NOT detect any security vulnerabilities.
"""

import os
import logging
from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import View, ListView, DetailView
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.utils.html import escape
from django.utils.safestring import mark_safe
import hashlib
import secrets
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Configure logging without PII
logger = logging.getLogger(__name__)

class SecureUser(models.Model):
    """Secure user model with proper validation."""
    
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            MinLengthValidator(3),
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username must contain only letters, numbers, and underscores'
            )
        ]
    )
    
    email = models.EmailField(unique=True)
    
    # Secure password field (Django handles hashing)
    password = models.CharField(max_length=128)
    
    # Additional security fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    # Secure session management
    session_key = models.CharField(max_length=40, blank=True, null=True)
    
    class Meta:
        db_table = 'secure_users'
        verbose_name = 'Secure User'
        verbose_name_plural = 'Secure Users'
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        # Ensure password is hashed
        if not self.password.startswith('bcrypt$'):
            self.password = self._hash_password(self.password)
        super().save(*args, **kwargs)
    
    def _hash_password(self, raw_password):
        """Securely hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
        return f"bcrypt${hashed.decode('utf-8')}"
    
    def check_password(self, raw_password):
        """Securely check password."""
        if self.password.startswith('bcrypt$'):
            hashed = self.password[7:]  # Remove 'bcrypt$' prefix
            return bcrypt.checkpw(raw_password.encode('utf-8'), hashed.encode('utf-8'))
        return False

class SecureDocument(models.Model):
    """Secure document model with proper access control."""
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    owner = models.ForeignKey(SecureUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(SecureUser, related_name='accessible_documents', blank=True)
    
    class Meta:
        db_table = 'secure_documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def can_access(self, user):
        """Check if user can access this document."""
        if self.is_public:
            return True
        if user == self.owner:
            return True
        if user in self.allowed_users.all():
            return True
        return False

class SecureFileUpload(models.Model):
    """Secure file upload model."""
    
    file = models.FileField(upload_to='secure_uploads/')
    original_filename = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64)  # SHA-256 hash
    uploaded_by = models.ForeignKey(SecureUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'secure_file_uploads'
    
    def save(self, *args, **kwargs):
        # Calculate file hash for integrity
        if self.file and not self.file_hash:
            self.file_hash = self._calculate_file_hash()
        super().save(*args, **kwargs)
    
    def _calculate_file_hash(self):
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        for chunk in self.file.chunks():
            sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

# Secure views
class SecureDocumentView(LoginRequiredMixin, DetailView):
    """Secure document view with access control."""
    model = SecureDocument
    template_name = 'secure_document_detail.html'
    context_object_name = 'document'
    
    def get_object(self, queryset=None):
        """Get object with access control."""
        obj = super().get_object(queryset)
        if not obj.can_access(self.request.user):
            raise PermissionDenied("You don't have permission to access this document.")
        return obj
    
    def get_context_data(self, **kwargs):
        """Add secure context data."""
        context = super().get_context_data(**kwargs)
        # Sanitize content to prevent XSS
        context['safe_content'] = mark_safe(escape(self.object.content))
        return context

@login_required
def secure_document_list(request):
    """Secure document list view."""
    # Only show documents user can access
    if request.user.is_superuser:
        documents = SecureDocument.objects.all()
    else:
        documents = SecureDocument.objects.filter(
            models.Q(owner=request.user) |
            models.Q(allowed_users=request.user) |
            models.Q(is_public=True)
        ).distinct()
    
    # Log access without PII
    logger.info(f"User {request.user.id} accessed document list")
    
    return render(request, 'secure_document_list.html', {
        'documents': documents
    })

@require_http_methods(["POST"])
@login_required
def secure_document_create(request):
    """Secure document creation."""
    try:
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        # Input validation
        if not title or len(title) > 200:
            return JsonResponse({'error': 'Invalid title'}, status=400)
        
        if not content or len(content) > 10000:
            return JsonResponse({'error': 'Invalid content'}, status=400)
        
        # Sanitize input
        title = escape(title)
        content = escape(content)
        
        # Create document
        document = SecureDocument.objects.create(
            title=title,
            content=content,
            owner=request.user
        )
        
        # Log creation without PII
        logger.info(f"Document created by user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'document_id': document.id
        })
        
    except Exception as e:
        logger.error(f"Error creating document: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["POST"])
@login_required
def secure_file_upload(request):
    """Secure file upload."""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # File validation
        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
            return JsonResponse({'error': 'File too large'}, status=400)
        
        # File type validation
        allowed_types = ['text/plain', 'application/pdf', 'image/jpeg', 'image/png']
        if uploaded_file.content_type not in allowed_types:
            return JsonResponse({'error': 'File type not allowed'}, status=400)
        
        # Generate secure filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        secure_filename = f"{secrets.token_urlsafe(16)}{file_extension}"
        
        # Save file
        file_upload = SecureFileUpload.objects.create(
            file=uploaded_file,
            original_filename=uploaded_file.name,
            uploaded_by=request.user
        )
        
        # Log upload without PII
        logger.info(f"File uploaded by user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'file_id': file_upload.id,
            'filename': secure_filename
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

# Secure utilities
class SecureEncryption:
    """Secure encryption utilities."""
    
    def __init__(self):
        # Get encryption key from environment
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            # Generate new key if not exists
            key = Fernet.generate_key()
            logger.warning("No encryption key found, generated new key")
        
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt data securely."""
        if not isinstance(data, str):
            raise ValueError("Data must be a string")
        
        encrypted = self.cipher.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data securely."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise ValueError("Invalid encrypted data")

class SecurePasswordGenerator:
    """Secure password generation utilities."""
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate cryptographically secure password."""
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        # Use secrets for cryptographically secure random generation
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure password meets complexity requirements
        if not any(c.islower() for c in password):
            password = password[:-1] + secrets.choice("abcdefghijklmnopqrstuvwxyz")
        if not any(c.isupper() for c in password):
            password = password[:-1] + secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if not any(c.isdigit() for c in password):
            password = password[:-1] + secrets.choice("0123456789")
        if not any(c in "!@#$%^&*" for c in password):
            password = password[:-1] + secrets.choice("!@#$%^&*")
        
        return password
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """Validate password strength."""
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Password must be at least 8 characters long")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one lowercase letter")
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one uppercase letter")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one digit")
        
        if any(c in "!@#$%^&*" for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one special character")
        
        if len(password) >= 12:
            score += 1
        
        strength = "weak" if score < 3 else "medium" if score < 5 else "strong"
        
        return {
            'score': score,
            'strength': strength,
            'feedback': feedback,
            'is_acceptable': score >= 3
        }

# Secure middleware
class SecurityMiddleware:
    """Custom security middleware."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add security headers
        response = self.get_response(request)
        
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

# Secure configuration
SECURE_SETTINGS = {
    'SECURE_BROWSER_XSS_FILTER': True,
    'SECURE_CONTENT_TYPE_NOSNIFF': True,
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
    'SECURE_HSTS_SECONDS': 31536000,
    'SECURE_REDIRECT_EXEMPT': [],
    'SECURE_SSL_HOST': None,
    'SECURE_SSL_REDIRECT': True,
    'SESSION_COOKIE_SECURE': True,
    'CSRF_COOKIE_SECURE': True,
    'CSRF_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_AGE': 3600,  # 1 hour
    'SESSION_EXPIRE_AT_BROWSER_CLOSE': True,
}

if __name__ == "__main__":
    print("Secure Django code examples")
    print("This file contains secure coding practices")
    print("for testing Levox detection capabilities.")

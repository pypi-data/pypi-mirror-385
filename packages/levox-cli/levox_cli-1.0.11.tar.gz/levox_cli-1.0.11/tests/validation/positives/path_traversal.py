#!/usr/bin/env python3
"""
Test file with path traversal vulnerabilities.
Based on OWASP Path Traversal examples.
Expected: Should detect path traversal patterns.
"""

import os
from pathlib import Path
from flask import request, send_file
import zipfile
import tarfile

def vulnerable_file_read():
    """Vulnerable file reading with path traversal."""
    filename = request.args.get('file')
    
    # Direct path traversal
    file_path = f"/var/www/uploads/{filename}"  # Vulnerable
    with open(file_path, 'r') as f:  # Vulnerable
        content = f.read()
    
    # Another pattern
    file_path = f"uploads/{filename}"  # Vulnerable
    with open(file_path, 'rb') as f:  # Vulnerable
        return f.read()

def vulnerable_file_write():
    """Vulnerable file writing with path traversal."""
    filename = request.form.get('filename')
    content = request.form.get('content')
    
    # Dangerous file writing
    file_path = f"/var/www/uploads/{filename}"  # Vulnerable
    with open(file_path, 'w') as f:  # Vulnerable
        f.write(content)
    
    # Another pattern
    file_path = f"data/{filename}"  # Vulnerable
    with open(file_path, 'a') as f:  # Vulnerable
        f.write(content)

def vulnerable_file_delete():
    """Vulnerable file deletion with path traversal."""
    filename = request.args.get('file')
    
    # Dangerous file deletion
    file_path = f"/var/www/uploads/{filename}"  # Vulnerable
    os.remove(file_path)  # Vulnerable
    
    # Another pattern
    file_path = f"temp/{filename}"  # Vulnerable
    if os.path.exists(file_path):  # Vulnerable
        os.unlink(file_path)  # Vulnerable

def vulnerable_directory_listing():
    """Vulnerable directory listing with path traversal."""
    directory = request.args.get('dir')
    
    # Dangerous directory listing
    dir_path = f"/var/www/{directory}"  # Vulnerable
    files = os.listdir(dir_path)  # Vulnerable
    
    # Another pattern
    dir_path = f"public/{directory}"  # Vulnerable
    for root, dirs, files in os.walk(dir_path):  # Vulnerable
        pass

def vulnerable_zip_extraction():
    """Vulnerable ZIP extraction with path traversal."""
    zip_file = request.files.get('zipfile')
    
    # Dangerous ZIP extraction
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall("/var/www/uploads/")  # Vulnerable
    
    # Another pattern
    extract_path = f"uploads/{request.form.get('path')}"  # Vulnerable
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)  # Vulnerable

def vulnerable_tar_extraction():
    """Vulnerable TAR extraction with path traversal."""
    tar_file = request.files.get('tarfile')
    
    # Dangerous TAR extraction
    with tarfile.open(tar_file, 'r:*') as tar_ref:
        tar_ref.extractall("/var/www/uploads/")  # Vulnerable
    
    # Another pattern
    extract_path = f"data/{request.form.get('path')}"  # Vulnerable
    with tarfile.open(tar_file, 'r:*') as tar_ref:
        tar_ref.extractall(extract_path)  # Vulnerable

def vulnerable_file_copy():
    """Vulnerable file copying with path traversal."""
    source = request.args.get('source')
    destination = request.args.get('dest')
    
    # Dangerous file copying
    src_path = f"/var/www/{source}"  # Vulnerable
    dst_path = f"/var/www/{destination}"  # Vulnerable
    
    import shutil
    shutil.copy2(src_path, dst_path)  # Vulnerable

def vulnerable_file_move():
    """Vulnerable file moving with path traversal."""
    source = request.args.get('source')
    destination = request.args.get('dest')
    
    # Dangerous file moving
    src_path = f"uploads/{source}"  # Vulnerable
    dst_path = f"archive/{destination}"  # Vulnerable
    
    import shutil
    shutil.move(src_path, dst_path)  # Vulnerable

def vulnerable_file_permissions():
    """Vulnerable file permission changes with path traversal."""
    filename = request.args.get('file')
    
    # Dangerous permission changes
    file_path = f"/var/www/uploads/{filename}"  # Vulnerable
    os.chmod(file_path, 0o777)  # Vulnerable
    
    # Another pattern
    file_path = f"public/{filename}"  # Vulnerable
    os.chown(file_path, 1000, 1000)  # Vulnerable

def vulnerable_symlink_creation():
    """Vulnerable symlink creation with path traversal."""
    target = request.args.get('target')
    link_name = request.args.get('link')
    
    # Dangerous symlink creation
    target_path = f"/var/www/{target}"  # Vulnerable
    link_path = f"uploads/{link_name}"  # Vulnerable
    
    os.symlink(target_path, link_path)  # Vulnerable

def vulnerable_path_join():
    """Vulnerable path joining with path traversal."""
    user_input = request.args.get('path')
    
    # Dangerous path joining
    base_path = "/var/www/uploads"
    full_path = os.path.join(base_path, user_input)  # Vulnerable
    
    # Another pattern
    full_path = Path(base_path) / user_input  # Vulnerable
    
    with open(full_path, 'r') as f:  # Vulnerable
        return f.read()

if __name__ == "__main__":
    print("Path traversal test file")
    print("This file contains various path traversal vulnerabilities")
    print("for testing Levox detection capabilities.")

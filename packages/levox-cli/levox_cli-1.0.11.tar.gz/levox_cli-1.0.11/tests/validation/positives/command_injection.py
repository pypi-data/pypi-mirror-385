#!/usr/bin/env python3
"""
Test file with command injection vulnerabilities.
Based on OWASP Command Injection examples.
Expected: Should detect command injection patterns.
"""

import os
import subprocess
import platform
from flask import request

def vulnerable_command_execution():
    """Vulnerable command execution from user input."""
    user_input = request.args.get('command')
    
    # Direct command injection
    os.system(f"ping {user_input}")  # Vulnerable
    
    # Another vulnerable pattern
    subprocess.call(f"nslookup {user_input}", shell=True)  # Vulnerable
    
    # Using os.popen
    result = os.popen(f"dig {user_input}").read()  # Vulnerable
    
    return result

def vulnerable_file_operations():
    """Vulnerable file operations."""
    filename = request.form.get('filename')
    
    # Dangerous file operations
    os.system(f"cat {filename}")  # Vulnerable
    os.system(f"rm {filename}")   # Vulnerable
    
    # Using subprocess with shell=True
    subprocess.run(f"ls -la {filename}", shell=True)  # Vulnerable

def vulnerable_network_operations():
    """Vulnerable network operations."""
    host = request.args.get('host')
    port = request.args.get('port')
    
    # Network scanning
    os.system(f"nmap -p {port} {host}")  # Vulnerable
    
    # Port scanning
    subprocess.call(f"telnet {host} {port}", shell=True)  # Vulnerable

def vulnerable_system_info():
    """Vulnerable system information gathering."""
    user_input = request.args.get('info')
    
    # System commands
    os.system(f"uname -a {user_input}")  # Vulnerable
    subprocess.run(f"ps aux {user_input}", shell=True)  # Vulnerable

def complex_injection():
    """Complex command injection patterns."""
    user_input = request.form.get('input')
    
    # Multiple command injection
    command = f"echo {user_input} && whoami"  # Vulnerable
    os.system(command)
    
    # Pipeline injection
    pipeline = f"cat {user_input} | grep password"  # Vulnerable
    subprocess.call(pipeline, shell=True)

def vulnerable_backup_script():
    """Vulnerable backup script example."""
    backup_path = request.args.get('path')
    
    # Dangerous backup command
    os.system(f"tar -czf backup.tar.gz {backup_path}")  # Vulnerable
    
    # Another pattern
    subprocess.run(f"rsync -av {backup_path} /backup/", shell=True)  # Vulnerable

def vulnerable_log_analysis():
    """Vulnerable log analysis."""
    log_file = request.args.get('logfile')
    
    # Log analysis commands
    os.system(f"tail -f {log_file}")  # Vulnerable
    subprocess.call(f"grep ERROR {log_file}", shell=True)  # Vulnerable

def vulnerable_package_management():
    """Vulnerable package management."""
    package = request.args.get('package')
    
    # Package installation
    os.system(f"pip install {package}")  # Vulnerable
    subprocess.run(f"npm install {package}", shell=True)  # Vulnerable

def vulnerable_database_backup():
    """Vulnerable database backup."""
    db_name = request.args.get('database')
    
    # Database backup
    os.system(f"mysqldump {db_name} > backup.sql")  # Vulnerable
    subprocess.call(f"pg_dump {db_name} > backup.sql", shell=True)  # Vulnerable

def vulnerable_file_upload():
    """Vulnerable file upload processing."""
    file_path = request.args.get('file')
    
    # File processing
    os.system(f"chmod 755 {file_path}")  # Vulnerable
    subprocess.run(f"file {file_path}", shell=True)  # Vulnerable

if __name__ == "__main__":
    # Example usage
    print("Command injection test file")
    print("This file contains various command injection vulnerabilities")
    print("for testing Levox detection capabilities.")

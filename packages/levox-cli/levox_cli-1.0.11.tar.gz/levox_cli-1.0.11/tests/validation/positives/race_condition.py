#!/usr/bin/env python3
"""
Test file with race condition vulnerabilities.
Based on OWASP Race Condition examples.
Expected: Should detect race condition patterns.
"""

import threading
import time
import os
import tempfile
from flask import request
import json
import sqlite3
import shutil

# Global variables for race conditions
balance = 1000
file_lock = threading.Lock()
db_lock = threading.Lock()

def vulnerable_balance_check():
    """Vulnerable balance check with race condition."""
    global balance
    amount = int(request.args.get('amount', 0))
    
    # Race condition: check and modify without proper locking
    if balance >= amount:  # Check
        time.sleep(0.1)  # Simulate processing time
        balance -= amount  # Modify
        return f"Withdrawn {amount}, new balance: {balance}"
    else:
        return "Insufficient funds"

def vulnerable_file_creation():
    """Vulnerable file creation with race condition."""
    filename = request.args.get('filename')
    content = request.form.get('content')
    
    # Race condition: check if file exists, then create
    if not os.path.exists(filename):  # Check
        time.sleep(0.1)  # Simulate processing time
        with open(filename, 'w') as f:  # Create
            f.write(content)
        return f"File {filename} created"
    else:
        return f"File {filename} already exists"

def vulnerable_file_deletion():
    """Vulnerable file deletion with race condition."""
    filename = request.args.get('filename')
    
    # Race condition: check if file exists, then delete
    if os.path.exists(filename):  # Check
        time.sleep(0.1)  # Simulate processing time
        os.remove(filename)  # Delete
        return f"File {filename} deleted"
    else:
        return f"File {filename} not found"

def vulnerable_directory_creation():
    """Vulnerable directory creation with race condition."""
    dirname = request.args.get('dirname')
    
    # Race condition: check if directory exists, then create
    if not os.path.exists(dirname):  # Check
        time.sleep(0.1)  # Simulate processing time
        os.makedirs(dirname)  # Create
        return f"Directory {dirname} created"
    else:
        return f"Directory {dirname} already exists"

def vulnerable_temp_file_creation():
    """Vulnerable temporary file creation with race condition."""
    prefix = request.args.get('prefix', 'temp')
    content = request.form.get('content')
    
    # Race condition: create temp file without proper locking
    temp_file = tempfile.mktemp(prefix=prefix)  # Vulnerable
    time.sleep(0.1)  # Simulate processing time
    
    with open(temp_file, 'w') as f:
        f.write(content)
    
    return f"Temporary file {temp_file} created"

def vulnerable_database_operation():
    """Vulnerable database operation with race condition."""
    user_id = request.args.get('user_id')
    amount = int(request.args.get('amount', 0))
    
    # Race condition: read, modify, write without proper locking
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # Read current balance
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Update balance
        new_balance = current_balance + amount
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
        conn.commit()
    
    conn.close()
    return "Balance updated"

def vulnerable_counter_increment():
    """Vulnerable counter increment with race condition."""
    global balance
    
    # Race condition: read, modify, write without proper locking
    current = balance  # Read
    time.sleep(0.1)  # Simulate processing time
    balance = current + 1  # Modify
    
    return f"Counter incremented to {balance}"

def vulnerable_list_operation():
    """Vulnerable list operation with race condition."""
    items = []
    
    def add_item():
        nonlocal items
        items.append(threading.current_thread().name)
        time.sleep(0.1)
    
    # Create multiple threads to demonstrate race condition
    threads = []
    for i in range(5):
        thread = threading.Thread(target=add_item)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return f"Items added: {items}"

def vulnerable_dictionary_operation():
    """Vulnerable dictionary operation with race condition."""
    data = {}
    
    def update_data():
        nonlocal data
        thread_id = threading.current_thread().ident
        data[thread_id] = time.time()
        time.sleep(0.1)
    
    # Create multiple threads to demonstrate race condition
    threads = []
    for i in range(3):
        thread = threading.Thread(target=update_data)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return f"Data updated: {data}"

def vulnerable_file_copy():
    """Vulnerable file copy with race condition."""
    source = request.args.get('source')
    destination = request.args.get('destination')
    
    # Race condition: check if source exists, then copy
    if os.path.exists(source):  # Check
        time.sleep(0.1)  # Simulate processing time
        shutil.copy2(source, destination)  # Copy
        return f"File copied from {source} to {destination}"
    else:
        return f"Source file {source} not found"

def vulnerable_file_move():
    """Vulnerable file move with race condition."""
    source = request.args.get('source')
    destination = request.args.get('destination')
    
    # Race condition: check if source exists, then move
    if os.path.exists(source):  # Check
        time.sleep(0.1)  # Simulate processing time
        shutil.move(source, destination)  # Move
        return f"File moved from {source} to {destination}"
    else:
        return f"Source file {source} not found"

def vulnerable_symlink_creation():
    """Vulnerable symlink creation with race condition."""
    target = request.args.get('target')
    link_name = request.args.get('link')
    
    # Race condition: check if link exists, then create
    if not os.path.exists(link_name):  # Check
        time.sleep(0.1)  # Simulate processing time
        os.symlink(target, link_name)  # Create
        return f"Symlink {link_name} created pointing to {target}"
    else:
        return f"Symlink {link_name} already exists"

def vulnerable_process_creation():
    """Vulnerable process creation with race condition."""
    command = request.args.get('command')
    
    # Race condition: check if process is running, then start
    import psutil
    
    # Check if process is running (weak check)
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == command:
            return f"Process {command} is already running"
    
    time.sleep(0.1)  # Simulate processing time
    
    # Start process
    import subprocess
    subprocess.Popen([command])
    
    return f"Process {command} started"

def vulnerable_resource_allocation():
    """Vulnerable resource allocation with race condition."""
    resource_id = request.args.get('resource_id')
    
    # Race condition: check if resource is available, then allocate
    if not os.path.exists(f"resources/{resource_id}.lock"):  # Check
        time.sleep(0.1)  # Simulate processing time
        
        # Create lock file
        with open(f"resources/{resource_id}.lock", 'w') as f:
            f.write(str(threading.current_thread().ident))
        
        return f"Resource {resource_id} allocated"
    else:
        return f"Resource {resource_id} is not available"

if __name__ == "__main__":
    print("Race condition test file")
    print("This file contains various race condition vulnerabilities")
    print("for testing Levox detection capabilities.")

#!/usr/bin/env python3
"""
Test file with unsafe deserialization vulnerabilities.
Based on OWASP Deserialization examples.
Expected: Should detect unsafe deserialization patterns.
"""

import pickle
import json
import yaml
import xml.etree.ElementTree as ET
from flask import request
import base64
import marshal
import ast

def vulnerable_pickle_deserialization():
    """Vulnerable pickle deserialization."""
    data = request.data
    
    # Vulnerable pickle usage
    obj = pickle.loads(data)  # Vulnerable
    
    # Another pattern
    obj = pickle.loads(base64.b64decode(data))  # Vulnerable
    
    return obj

def vulnerable_pickle_file_deserialization():
    """Vulnerable pickle file deserialization."""
    pickle_file = request.files.get('pickle_file')
    
    # Vulnerable file deserialization
    obj = pickle.load(pickle_file)  # Vulnerable
    
    # Another pattern
    with open(pickle_file, 'rb') as f:
        obj = pickle.load(f)  # Vulnerable
    
    return obj

def vulnerable_json_deserialization():
    """Vulnerable JSON deserialization."""
    json_data = request.data
    
    # Vulnerable JSON parsing
    obj = json.loads(json_data)  # Vulnerable
    
    # Another pattern
    obj = json.loads(json_data.decode('utf-8'))  # Vulnerable
    
    return obj

def vulnerable_yaml_deserialization():
    """Vulnerable YAML deserialization."""
    yaml_data = request.data
    
    # Vulnerable YAML parsing
    obj = yaml.safe_load(yaml_data)  # Vulnerable
    
    # Dangerous YAML loading
    obj = yaml.load(yaml_data)  # Vulnerable
    
    return obj

def vulnerable_xml_deserialization():
    """Vulnerable XML deserialization."""
    xml_data = request.data
    
    # Vulnerable XML parsing
    root = ET.fromstring(xml_data)  # Vulnerable
    
    # Another pattern
    tree = ET.parse(xml_data)  # Vulnerable
    root = tree.getroot()
    
    return root

def vulnerable_marshal_deserialization():
    """Vulnerable marshal deserialization."""
    data = request.data
    
    # Vulnerable marshal usage
    obj = marshal.loads(data)  # Vulnerable
    
    # Another pattern
    obj = marshal.loads(base64.b64decode(data))  # Vulnerable
    
    return obj

def vulnerable_ast_deserialization():
    """Vulnerable AST deserialization."""
    code_string = request.args.get('code')
    
    # Vulnerable AST parsing
    tree = ast.parse(code_string)  # Vulnerable
    
    # Another pattern
    tree = ast.parse(code_string, mode='eval')  # Vulnerable
    
    return tree

def vulnerable_base64_deserialization():
    """Vulnerable base64 deserialization."""
    encoded_data = request.args.get('data')
    
    # Vulnerable base64 decoding
    decoded_data = base64.b64decode(encoded_data)  # Vulnerable
    
    # Try to deserialize
    try:
        obj = pickle.loads(decoded_data)  # Vulnerable
        return obj
    except:
        pass
    
    return decoded_data

def vulnerable_custom_deserialization():
    """Vulnerable custom deserialization."""
    data = request.data
    
    # Custom deserialization logic
    if data.startswith(b'pickle:'):
        pickle_data = data[8:]  # Remove prefix
        obj = pickle.loads(pickle_data)  # Vulnerable
    elif data.startswith(b'json:'):
        json_data = data[5:]  # Remove prefix
        obj = json.loads(json_data.decode('utf-8'))  # Vulnerable
    elif data.startswith(b'yaml:'):
        yaml_data = data[5:]  # Remove prefix
        obj = yaml.load(yaml_data)  # Vulnerable
    
    return obj

def vulnerable_conditional_deserialization():
    """Vulnerable conditional deserialization."""
    data = request.data
    format_type = request.args.get('format')
    
    # Conditional deserialization
    if format_type == 'pickle':
        obj = pickle.loads(data)  # Vulnerable
    elif format_type == 'json':
        obj = json.loads(data.decode('utf-8'))  # Vulnerable
    elif format_type == 'yaml':
        obj = yaml.load(data)  # Vulnerable
    elif format_type == 'xml':
        obj = ET.fromstring(data)  # Vulnerable
    
    return obj

def vulnerable_nested_deserialization():
    """Vulnerable nested deserialization."""
    data = request.data
    
    # First level deserialization
    first_obj = json.loads(data.decode('utf-8'))  # Vulnerable
    
    # Second level deserialization
    if 'nested_data' in first_obj:
        nested_data = first_obj['nested_data']
        if nested_data.startswith('pickle:'):
            pickle_data = nested_data[8:]
            second_obj = pickle.loads(base64.b64decode(pickle_data))  # Vulnerable
            return second_obj
    
    return first_obj

def vulnerable_deserialization_with_validation():
    """Vulnerable deserialization with weak validation."""
    data = request.data
    
    # Weak validation
    if len(data) < 10000:  # Size check only
        obj = pickle.loads(data)  # Vulnerable
        return obj
    
    return None

def vulnerable_deserialization_with_whitelist():
    """Vulnerable deserialization with weak whitelist."""
    data = request.data
    allowed_classes = ['User', 'Config', 'Settings']
    
    # Weak whitelist (can be bypassed)
    try:
        obj = pickle.loads(data)  # Vulnerable
        class_name = obj.__class__.__name__
        if class_name in allowed_classes:
            return obj
    except:
        pass
    
    return None

def vulnerable_deserialization_with_encoding():
    """Vulnerable deserialization with encoding."""
    data = request.args.get('data')
    encoding = request.args.get('encoding', 'utf-8')
    
    # Decode and deserialize
    decoded_data = data.encode(encoding)
    
    # Try multiple deserialization methods
    try:
        obj = pickle.loads(decoded_data)  # Vulnerable
        return obj
    except:
        pass
    
    try:
        obj = json.loads(decoded_data.decode(encoding))  # Vulnerable
        return obj
    except:
        pass
    
    try:
        obj = yaml.load(decoded_data)  # Vulnerable
        return obj
    except:
        pass
    
    return None

if __name__ == "__main__":
    print("Unsafe deserialization test file")
    print("This file contains various unsafe deserialization vulnerabilities")
    print("for testing Levox detection capabilities.")

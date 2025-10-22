#!/usr/bin/env python3
"""
Test file with SQL injection vulnerabilities.
Expected: Should detect SQL injection patterns and unsafe database operations.
"""

import sqlite3
import mysql.connector
import psycopg2
from flask import request

def unsafe_query_1(user_id):
    """Unsafe query with direct string concatenation."""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def unsafe_query_2(username):
    """Unsafe query with format string."""
    query = "SELECT * FROM users WHERE username = '{}'".format(username)
    return query

def unsafe_query_3(email):
    """Unsafe query with % formatting."""
    query = "SELECT * FROM users WHERE email = '%s'" % email
    return query

def unsafe_execute_1(cursor, user_id):
    """Unsafe execute with direct string concatenation."""
    query = f"DELETE FROM users WHERE id = {user_id}"
    cursor.execute(query)

def unsafe_execute_2(cursor, username):
    """Unsafe execute with format string."""
    query = "UPDATE users SET status = 'active' WHERE username = '{}'".format(username)
    cursor.execute(query)

def unsafe_execute_3(cursor, email):
    """Unsafe execute with % formatting."""
    query = "INSERT INTO users (email) VALUES ('%s')" % email
    cursor.execute(query)

def flask_unsafe_query():
    """Flask route with unsafe query."""
    user_id = request.args.get('id')
    query = f"SELECT * FROM users WHERE id = {user_id}"
    # This should be detected as unsafe

def raw_sql_construction():
    """Constructing raw SQL strings."""
    table_name = "users"
    column_name = "email"
    value = "test@example.com"
    
    # Unsafe table and column construction
    query = f"SELECT {column_name} FROM {table_name} WHERE {column_name} = '{value}'"
    
    # Unsafe ORDER BY
    order_by = "id"
    query2 = f"SELECT * FROM users ORDER BY {order_by}"
    
    # Unsafe LIMIT
    limit = "10"
    query3 = f"SELECT * FROM users LIMIT {limit}"

def dynamic_table_queries():
    """Dynamic table name queries."""
    table_name = request.args.get('table')
    query = f"SELECT * FROM {table_name}"
    
    # This is extremely dangerous
    query2 = f"DROP TABLE {table_name}"

def complex_injection():
    """More complex injection patterns."""
    user_input = request.form.get('search')
    
    # Multiple concatenations
    base_query = "SELECT * FROM products"
    if user_input:
        base_query += f" WHERE name LIKE '%{user_input}%'"
    
    # Additional conditions
    category = request.form.get('category')
    if category:
        base_query += f" AND category = '{category}'"
    
    # Final query construction
    final_query = base_query + " ORDER BY name"

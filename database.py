"""
Module quản lý SQLite Database cho Hill Cipher
"""

import sqlite3
import os
from datetime import datetime

# Tên file database
DB_FILE = 'hill_cipher.db'


def get_db_connection():
    """
    Tạo kết nối đến SQLite database.
    
    Trả về:
        Connection object
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Cho phép truy cập theo tên cột
    return conn


def init_database():
    """
    Khởi tạo database và tạo bảng nếu chưa tồn tại.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tạo bảng customers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            encrypted_data TEXT NOT NULL,
            key_matrix TEXT NOT NULL,
            key_inverse TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database đã được khởi tạo: {DB_FILE}")


def insert_customer(name, email, phone, encrypted_data, key_matrix, key_inverse):
    """
    Thêm một khách hàng mới vào database.
    
    Tham số:
        name: Tên khách hàng
        email: Email khách hàng
        phone: Số điện thoại
        encrypted_data: Dữ liệu đã mã hóa
        key_matrix: Ma trận khóa K (dạng chuỗi)
        key_inverse: Ma trận khóa nghịch đảo K⁻¹ (dạng chuỗi)
    
    Trả về:
        ID của khách hàng vừa được thêm, hoặc None nếu có lỗi
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers (name, email, phone, encrypted_data, key_matrix, key_inverse)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, encrypted_data, key_matrix, key_inverse))
        
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return customer_id
    except Exception as e:
        print(f"Lỗi khi thêm khách hàng: {e}")
        return None


def get_all_customers():
    """
    Lấy tất cả khách hàng từ database.
    
    Trả về:
        List các dictionary chứa thông tin khách hàng
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, phone, encrypted_data, key_matrix, key_inverse, created_at
            FROM customers
            ORDER BY id DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Chuyển đổi Row objects thành dictionaries
        customers = []
        for row in rows:
            customers.append({
                'id': row['id'],
                'name': row['name'],
                'email': row['email'],
                'phone': row['phone'],
                'encrypted_data': row['encrypted_data'],
                'key_matrix': row['key_matrix'],
                'key_inverse': row['key_inverse'],
                'created_at': row['created_at']
            })
        
        return customers
    except Exception as e:
        print(f"Lỗi khi lấy danh sách khách hàng: {e}")
        return []


def get_customer_by_id(customer_id):
    """
    Lấy thông tin một khách hàng theo ID.
    
    Tham số:
        customer_id: ID khách hàng
    
    Trả về:
        Dictionary chứa thông tin khách hàng, hoặc None nếu không tìm thấy
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, phone, encrypted_data, key_matrix, key_inverse, created_at
            FROM customers
            WHERE id = ?
        ''', (customer_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'name': row['name'],
                'email': row['email'],
                'phone': row['phone'],
                'encrypted_data': row['encrypted_data'],
                'key_matrix': row['key_matrix'],
                'key_inverse': row['key_inverse'],
                'created_at': row['created_at']
            }
        return None
    except Exception as e:
        print(f"Lỗi khi lấy thông tin khách hàng: {e}")
        return None


def delete_customer(customer_id):
    """
    Xóa một khách hàng khỏi database.
    
    Tham số:
        customer_id: ID khách hàng cần xóa
    
    Trả về:
        True nếu xóa thành công, False nếu có lỗi
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        
        return deleted
    except Exception as e:
        print(f"Lỗi khi xóa khách hàng: {e}")
        return False


def update_customer(customer_id, name, email, phone, encrypted_data, key_matrix, key_inverse):
    """
    Cập nhật thông tin khách hàng.
    
    Tham số:
        customer_id: ID khách hàng cần cập nhật
        name: Tên khách hàng
        email: Email khách hàng
        phone: Số điện thoại
        encrypted_data: Dữ liệu đã mã hóa
        key_matrix: Ma trận khóa K (dạng chuỗi)
        key_inverse: Ma trận khóa nghịch đảo K⁻¹ (dạng chuỗi)
    
    Trả về:
        True nếu cập nhật thành công, False nếu có lỗi
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE customers 
            SET name = ?, email = ?, phone = ?, encrypted_data = ?, 
                key_matrix = ?, key_inverse = ?
            WHERE id = ?
        ''', (name, email, phone, encrypted_data, key_matrix, key_inverse, customer_id))
        
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        
        return updated
    except Exception as e:
        print(f"Lỗi khi cập nhật khách hàng: {e}")
        return False


def get_customers_paginated(page=1, per_page=10):
    """
    Lấy danh sách khách hàng với phân trang.
    
    Tham số:
        page: Số trang (bắt đầu từ 1)
        per_page: Số record mỗi trang
    
    Trả về:
        Tuple (customers, total, pages) - danh sách khách hàng, tổng số, tổng số trang
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Đếm tổng số
        cursor.execute('SELECT COUNT(*) as total FROM customers')
        total = cursor.fetchone()['total']
        
        # Tính offset
        offset = (page - 1) * per_page
        
        # Lấy dữ liệu với phân trang
        cursor.execute('''
            SELECT id, name, email, phone, encrypted_data, key_matrix, key_inverse, created_at
            FROM customers
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Chuyển đổi Row objects thành dictionaries
        customers = []
        for row in rows:
            customers.append({
                'id': row['id'],
                'name': row['name'],
                'email': row['email'],
                'phone': row['phone'],
                'encrypted_data': row['encrypted_data'],
                'key_matrix': row['key_matrix'],
                'key_inverse': row['key_inverse'],
                'created_at': row['created_at']
            })
        
        # Tính tổng số trang
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        
        return customers, total, pages
    except Exception as e:
        print(f"Lỗi khi lấy danh sách khách hàng phân trang: {e}")
        return [], 0, 1


def get_database_stats():
    """
    Lấy thống kê về database.
    
    Trả về:
        Dictionary chứa các thống kê (tổng số khách hàng, v.v.)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM customers')
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return {
            'total_customers': total,
            'database_file': DB_FILE,
            'database_size': os.path.getsize(DB_FILE) if os.path.exists(DB_FILE) else 0
        }
    except Exception as e:
        print(f"Lỗi khi lấy thống kê: {e}")
        return {'total_customers': 0, 'database_file': DB_FILE, 'database_size': 0}


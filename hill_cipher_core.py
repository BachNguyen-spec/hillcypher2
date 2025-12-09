"""
Module Hill Cipher Core - Triển khai thuật toán Hill Cipher nâng cao
Hỗ trợ alphabet mở rộng bao gồm chữ cái tiếng Việt có dấu, số, dấu cách, dấu câu
"""

import warnings
warnings.filterwarnings('ignore')  # Bỏ qua warnings từ NumPy trên Python 3.13

import numpy as np
from math import gcd

# Định nghĩa alphabet mở rộng
ALPHABET = (
    # Chữ cái tiếng Anh (hoa và thường)
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    # Chữ cái tiếng Việt có dấu (hoa)
    'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊ'
    'ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ'
    # Chữ cái tiếng Việt có dấu (thường)
    'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩị'
    'òóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ'
    # Số
    '0123456789'
    # Dấu cách và dấu câu
    ' .,:;?!'
)

# Kích thước modulo m
M = len(ALPHABET)


def text_to_numbers(text, alphabet=ALPHABET):
    """
    Chuyển text thành list các số nguyên (index trong alphabet).
    
    Tham số:
        text: Chuỗi văn bản cần chuyển đổi
        alphabet: Bảng chữ cái sử dụng (mặc định là ALPHABET)
    
    Trả về:
        List các số nguyên tương ứng với từng ký tự trong text
    """
    numbers = []
    for char in text:
        if char in alphabet:
            numbers.append(alphabet.index(char))
        else:
            # Nếu ký tự không có trong alphabet, bỏ qua hoặc thêm ký tự mặc định
            # Ở đây ta sẽ bỏ qua ký tự không hợp lệ
            pass
    return numbers


def numbers_to_text(numbers, alphabet=ALPHABET):
    """
    Chuyển list số nguyên thành text.
    
    Tham số:
        numbers: List các số nguyên (index trong alphabet)
        alphabet: Bảng chữ cái sử dụng (mặc định là ALPHABET)
    
    Trả về:
        Chuỗi văn bản tương ứng
    """
    text = ""
    for num in numbers:
        if 0 <= num < len(alphabet):
            text += alphabet[num]
    return text


def extended_gcd(a, b):
    """
    Thực hiện thuật toán Euclidean mở rộng để tìm d, x, y sao cho ax + by = d.
    
    Tham số:
        a, b: Hai số nguyên
    
    Trả về:
        Tuple (d, x, y) trong đó d = gcd(a, b) và ax + by = d
    """
    if a == 0:
        return b, 0, 1
    
    d, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    
    return d, x, y


def mod_inverse(a, m):
    """
    Tìm nghịch đảo modulo của a theo m.
    
    Tham số:
        a: Số nguyên cần tìm nghịch đảo
        m: Modulo
    
    Trả về:
        Nghịch đảo modulo của a theo m, hoặc None nếu không tồn tại
    """
    d, x, y = extended_gcd(a, m)
    if d != 1:
        return None  # Nghịch đảo không tồn tại
    return (x % m + m) % m


def get_inverse_key(K, m=M):
    """
    Tính ma trận nghịch đảo K^(-1) modulo m.
    Kiểm tra điều kiện khả nghịch: gcd(det(K), m) = 1
    
    Tham số:
        K: Ma trận khóa (numpy array)
        m: Modulo (mặc định là M)
    
    Trả về:
        Ma trận nghịch đảo K^(-1) modulo m, hoặc None nếu không khả nghịch
    """
    try:
        # Chuyển đổi sang numpy array nếu chưa phải
        K = np.array(K, dtype=np.int64)
        
        # Kiểm tra ma trận vuông
        if K.shape[0] != K.shape[1]:
            return None
        
        # Tính định thức
        det = int(np.round(np.linalg.det(K))) % m
        
        # Kiểm tra điều kiện khả nghịch: gcd(det(K), m) = 1
        if gcd(det, m) != 1:
            return None
        
        # Tính nghịch đảo của định thức modulo m
        det_inv = mod_inverse(det, m)
        if det_inv is None:
            return None
        
        # Tính ma trận phụ hợp (adjugate matrix) bằng cách tính các phần phụ đại số
        n = K.shape[0]
        adj = np.zeros((n, n), dtype=np.int64)
        
        for i in range(n):
            for j in range(n):
                # Tính ma trận con (minor matrix) bằng cách bỏ hàng i và cột j
                minor = np.delete(np.delete(K, i, axis=0), j, axis=1)
                # Tính định thức của minor
                minor_det = int(np.round(np.linalg.det(minor))) % m
                # Phần phụ đại số = (-1)^(i+j) * det(minor)
                cofactor = ((-1) ** (i + j)) * minor_det
                # Ma trận phụ hợp là chuyển vị của ma trận phần phụ đại số
                adj[j, i] = cofactor % m
        
        # Tính ma trận nghịch đảo modulo m
        # Công thức: K^(-1) = (det(K))^(-1) * adj(K) mod m
        K_inv = (det_inv * adj) % m
        
        # Đảm bảo các giá trị trong khoảng [0, m-1]
        K_inv = K_inv % m
        
        return K_inv.astype(np.int64)
    
    except Exception as e:
        return None


def encrypt(plaintext, K, alphabet=ALPHABET, m=M):
    """
    Thực hiện mã hóa Hill Cipher.
    
    Tham số:
        plaintext: Văn bản gốc cần mã hóa
        K: Ma trận khóa (numpy array hoặc list)
        alphabet: Bảng chữ cái sử dụng (mặc định là ALPHABET)
        m: Modulo (mặc định là M)
    
    Trả về:
        Chuỗi bản mã, hoặc None nếu có lỗi
    """
    try:
        # Chuyển đổi ma trận khóa
        K = np.array(K, dtype=np.int64)
        n = K.shape[0]  # Kích thước ma trận (3x3)
        
        # Chuyển text thành số
        numbers = text_to_numbers(plaintext, alphabet)
        
        # Padding nếu cần (thêm ký tự ' ' (dấu cách) nếu độ dài không chia hết cho n)
        space_idx = alphabet.index(' ') if ' ' in alphabet else 0
        while len(numbers) % n != 0:
            numbers.append(space_idx)
        
        # Mã hóa từng khối
        cipher_numbers = []
        for i in range(0, len(numbers), n):
            block = np.array(numbers[i:i+n])
            encrypted_block = np.dot(K, block) % m
            cipher_numbers.extend(encrypted_block.tolist())
        
        # Chuyển số thành text
        ciphertext = numbers_to_text(cipher_numbers, alphabet)
        return ciphertext
    
    except Exception as e:
        return None


def decrypt(ciphertext, K_inv, alphabet=ALPHABET, m=M):
    """
    Thực hiện giải mã Hill Cipher.
    
    Tham số:
        ciphertext: Văn bản mã cần giải mã
        K_inv: Ma trận khóa nghịch đảo (numpy array hoặc list)
        alphabet: Bảng chữ cái sử dụng (mặc định là ALPHABET)
        m: Modulo (mặc định là M)
    
    Trả về:
        Chuỗi bản rõ, hoặc None nếu có lỗi
    """
    try:
        # Chuyển đổi ma trận khóa nghịch đảo
        K_inv = np.array(K_inv, dtype=np.int64)
        n = K_inv.shape[0]  # Kích thước ma trận (3x3)
        
        # Chuyển text thành số
        numbers = text_to_numbers(ciphertext, alphabet)
        
        # Kiểm tra độ dài
        if len(numbers) % n != 0:
            return None
        
        # Giải mã từng khối
        plain_numbers = []
        for i in range(0, len(numbers), n):
            block = np.array(numbers[i:i+n])
            decrypted_block = np.dot(K_inv, block) % m
            plain_numbers.extend(decrypted_block.tolist())
        
        # Chuyển số thành text
        plaintext = numbers_to_text(plain_numbers, alphabet)
        return plaintext
    
    except Exception as e:
        return None


def matrix_string_to_array(matrix_str, n=3):
    """
    Chuyển đổi chuỗi ma trận (ví dụ: "1 2 3; 4 5 6; 7 8 9") thành numpy array.
    
    Tham số:
        matrix_str: Chuỗi ma trận (có thể dùng ; hoặc \n để phân cách hàng, space hoặc , để phân cách cột)
        n: Kích thước ma trận (mặc định 3)
    
    Trả về:
        numpy array ma trận, hoặc None nếu có lỗi
    """
    try:
        # Thay thế các ký tự phân cách
        matrix_str = matrix_str.replace(',', ' ').replace(';', '\n')
        
        # Tách thành các hàng
        rows = matrix_str.strip().split('\n')
        matrix = []
        
        for row in rows:
            row = row.strip()
            if not row:
                continue
            # Tách thành các số
            cols = [int(x.strip()) for x in row.split() if x.strip()]
            if len(cols) == n:
                matrix.append(cols)
        
        if len(matrix) != n:
            return None
        
        return np.array(matrix, dtype=np.int64)
    
    except Exception as e:
        return None


def array_to_matrix_string(matrix):
    """
    Chuyển đổi numpy array thành chuỗi ma trận để hiển thị.
    
    Tham số:
        matrix: numpy array
    
    Trả về:
        Chuỗi ma trận dạng "1 2 3; 4 5 6; 7 8 9"
    """
    try:
        matrix = np.array(matrix)
        rows = []
        for row in matrix:
            rows.append(' '.join(str(int(x)) for x in row))
        return '; '.join(rows)
    except Exception as e:
        return ""
        
# Hill Cipher Web Application

Ứng dụng web Flask triển khai thuật toán Hill Cipher nâng cao để mã hóa dữ liệu tiếng Việt có dấu, số, và dấu cách.

## Tính năng

- **Alphabet mở rộng**: Hỗ trợ chữ cái tiếng Việt có dấu, số, dấu cách, và dấu câu cơ bản
- **Ma trận khóa 3x3**: Sử dụng ma trận khóa kích thước 3x3
- **Mã hóa thông tin khách hàng**: Form nhập liệu để mã hóa và lưu trữ thông tin khách hàng
- **Công cụ mã hóa/giải mã**: Công cụ để mã hóa và giải mã văn bản lớn
- **Import/Export CSV**: Upload file CSV để mã hóa/giải mã hàng loạt và tải về file kết quả
- **Giao diện hiện đại**: Sử dụng Bootstrap 5 với thiết kế đẹp mắt

## Cài đặt

1. **Cài đặt dependencies:**

```bash
pip install -r requirements.txt
```

2. **Chạy ứng dụng:**

```bash
python app.py
```

3. **Truy cập ứng dụng:**

Mở trình duyệt và truy cập: `http://localhost:5000`

## Cấu trúc dự án

```
hillcypher/
├── app.py                  # Entry point (khởi tạo app từ factory)
├── hillcipher_app/
│   ├── __init__.py         # create_app() và đăng ký blueprint
│   └── routes.py           # Toàn bộ routes/flask views
├── hill_cipher_core.py     # Module core với các hàm Hill Cipher
├── database.py             # Module quản lý SQLite database
├── hill_cipher.db          # File SQLite database (tự động tạo)
├── requirements.txt        # Dependencies
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── decrypt_tool.html
│   ├── bulk_tool.html
│   └── database.html
└── static/                 # Static files (CSS, JS)
```

## 💾 Cơ sở Dữ liệu (CSDL)

**CSDL sử dụng SQLite để lưu trữ dữ liệu:**

- **Vị trí lưu trữ:** File `hill_cipher.db` trong thư mục gốc của project
- **Module quản lý:** `database.py` - chứa các hàm để thao tác với SQLite
- **Schema:** Bảng `customers` với các cột:
  - `id`: ID tự động tăng (PRIMARY KEY)
  - `name`: Tên khách hàng
  - `email`: Email khách hàng
  - `phone`: Số điện thoại
  - `encrypted_data`: Dữ liệu đã mã hóa
  - `key_matrix`: Ma trận khóa K (dạng chuỗi)
  - `key_inverse`: Ma trận khóa nghịch đảo K⁻¹ (dạng chuỗi)
  - `created_at`: Thời gian tạo (TIMESTAMP)

- **Đặc điểm:**
  - ✅ Dữ liệu được lưu vĩnh viễn vào file database
  - ✅ Dữ liệu không mất khi tắt server
  - ✅ Phù hợp cho môi trường production
  - ✅ Không cần cài đặt server database riêng
  - ✅ File database có thể backup và restore dễ dàng

- **Xem dữ liệu:**
  - Truy cập route `/database` để xem tất cả dữ liệu đã lưu
  - File database `hill_cipher.db` có thể mở bằng SQLite browser hoặc các công cụ quản lý database

## Sử dụng

### 1. Mã hóa thông tin khách hàng

- Truy cập trang chủ `/`
- Nhập thông tin khách hàng (Tên, Email, SĐT)
- Nhập ma trận khóa K (3x3) - ví dụ: `1 2 3; 4 5 6; 7 8 9`
- Nhấn "Mã hóa và Lưu"
- Hệ thống sẽ hiển thị bản mã và ma trận khóa nghịch đảo K⁻¹

### 2. Công cụ mã hóa/giải mã

- Truy cập `/decrypt_tool`
- **Tab Mã hóa**: Nhập bản rõ và ma trận khóa K để mã hóa
- **Tab Giải mã**: Nhập bản mã và ma trận khóa nghịch đảo K⁻¹ để giải mã

### 3. Import/Export CSV

- Truy cập `/bulk_tool`
- **Import bản rõ**: Upload CSV (`name,email,phone`) + ma trận K → nhận file CSV đã mã hóa
- **Import bản mã**: Upload CSV (`encrypted_data`) + ma trận K⁻¹ → nhận file CSV đã giải mã
- File xuất ra dùng encoding UTF-8 (có BOM) để mở bằng Excel thuận tiện

### 4. Xem CSDL

- Truy cập `/database` để xem tất cả dữ liệu đã mã hóa và lưu trữ

## Lưu ý về Ma trận Khóa

- Ma trận khóa K phải là ma trận vuông 3x3
- Ma trận khóa phải **khả nghịch modulo m**: `gcd(det(K), m) = 1`
- Kích thước alphabet (modulo m) là **{{ M }}** (bao gồm tất cả ký tự tiếng Việt, số, dấu cách, dấu câu)
- Nếu ma trận không khả nghịch, hệ thống sẽ báo lỗi

## Ví dụ Ma trận Khóa hợp lệ

```
1  2  3
4  5  6
7  8  9
```

Hoặc nhập dạng: `1 2 3; 4 5 6; 7 8 9`

## Alphabet

Alphabet bao gồm:
- Chữ cái tiếng Anh: A-Z, a-z
- Chữ cái tiếng Việt có dấu (hoa và thường): ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ và chữ thường tương ứng
- Số: 0-9
- Dấu cách và dấu câu: ` .,:;?!`

**Tổng cộng: {{ M }} ký tự**

## Yêu cầu hệ thống

- Python 3.7+
- Flask 3.0.0
- NumPy 1.26.2

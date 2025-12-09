from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_file,
)
import csv
import json
from io import StringIO, BytesIO
from datetime import datetime

from hill_cipher_core import (
    ALPHABET,
    M,
    encrypt,
    decrypt,
    get_inverse_key,
    matrix_string_to_array,
    array_to_matrix_string,
)
from database import (
    insert_customer,
    get_all_customers,
    get_customer_by_id,
    get_database_stats,
    update_customer,
    delete_customer,
    get_customers_paginated,
)


bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Trang chủ/Admin nhập liệu"""
    return render_template("index.html", alphabet_size=M)


@bp.route("/encrypt_customer", methods=["POST"])
def encrypt_customer():
    """Xử lý mã hóa thông tin khách hàng"""
    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        matrix_str = request.form.get("key_matrix", "").strip()

        if not name or not email or not phone:
            flash("Vui lòng điền đầy đủ thông tin khách hàng!", "error")
            return redirect(url_for("main.index"))

        if not matrix_str:
            flash("Vui lòng nhập ma trận khóa K!", "error")
            return redirect(url_for("main.index"))

        K = matrix_string_to_array(matrix_str, n=3)
        if K is None:
            flash(
                "Ma trận khóa không hợp lệ! Vui lòng nhập ma trận 3x3 (ví dụ: 1 2 3; 4 5 6; 7 8 9)",
                "error",
            )
            return redirect(url_for("main.index"))

        K_inv = get_inverse_key(K, M)
        if K_inv is None:
            flash(
                "Ma trận khóa không khả nghịch! gcd(det(K), m) phải bằng 1. Vui lòng chọn ma trận khóa khác.",
                "error",
            )
            return redirect(url_for("main.index"))

        customer_data = f"{name}|{email}|{phone}"
        encrypted_data = encrypt(customer_data, K, ALPHABET, M)
        if encrypted_data is None:
            flash("Lỗi khi mã hóa dữ liệu!", "error")
            return redirect(url_for("main.index"))

        key_matrix_str = array_to_matrix_string(K)
        key_inverse_str = array_to_matrix_string(K_inv)

        customer_id = insert_customer(
            name=name,
            email=email,
            phone=phone,
            encrypted_data=encrypted_data,
            key_matrix=key_matrix_str,
            key_inverse=key_inverse_str,
        )

        if customer_id is None:
            flash("Lỗi khi lưu vào database!", "error")
            return redirect(url_for("main.index"))

        flash(f"Mã hóa thành công! Customer ID: {customer_id}", "success")
        return render_template(
            "index.html",
            customer_id=customer_id,
            plaintext=customer_data,
            key_matrix=key_matrix_str,
            encrypted_data=encrypted_data,
            key_inverse=key_inverse_str,
            alphabet_size=M,
        )

    except Exception as e:
        flash(f"Lỗi: {str(e)}", "error")
        return redirect(url_for("main.index"))


@bp.route("/decrypt_tool")
def decrypt_tool():
    """Công cụ mã hóa/giải mã text lớn"""
    return render_template("decrypt_tool.html", alphabet_size=M)


@bp.route("/bulk_tool")
def bulk_tool():
    """Công cụ import/export file CSV"""
    return render_template("bulk_tool.html", alphabet_size=M)


@bp.route("/encrypt_text", methods=["POST"])
def encrypt_text():
    """Xử lý mã hóa text lớn"""
    try:
        plaintext = request.form.get("plaintext", "").strip()
        matrix_str = request.form.get("key_matrix", "").strip()

        if not plaintext:
            flash("Vui lòng nhập bản rõ!", "error")
            return redirect(url_for("main.decrypt_tool"))

        if not matrix_str:
            flash("Vui lòng nhập ma trận khóa K!", "error")
            return redirect(url_for("main.decrypt_tool"))

        K = matrix_string_to_array(matrix_str, n=3)
        if K is None:
            flash("Ma trận khóa không hợp lệ! Vui lòng nhập ma trận 3x3", "error")
            return redirect(url_for("main.decrypt_tool"))

        K_inv = get_inverse_key(K, M)
        if K_inv is None:
            flash("Ma trận khóa không khả nghịch! gcd(det(K), m) phải bằng 1.", "error")
            return redirect(url_for("main.decrypt_tool"))

        encrypted_data = encrypt(plaintext, K, ALPHABET, M)
        if encrypted_data is None:
            flash("Lỗi khi mã hóa dữ liệu!", "error")
            return redirect(url_for("main.decrypt_tool"))

        return render_template(
            "decrypt_tool.html",
            plaintext=plaintext,
            key_matrix=array_to_matrix_string(K),
            encrypted_data=encrypted_data,
            key_inverse=array_to_matrix_string(K_inv),
            alphabet_size=M,
        )

    except Exception as e:
        flash(f"Lỗi: {str(e)}", "error")
        return redirect(url_for("main.decrypt_tool"))


@bp.route("/decrypt_text", methods=["POST"])
def decrypt_text():
    """Xử lý giải mã text lớn"""
    try:
        ciphertext = request.form.get("ciphertext", "").strip()
        matrix_inv_str = request.form.get("key_inverse", "").strip()

        if not ciphertext:
            flash("Vui lòng nhập bản mã!", "error")
            return redirect(url_for("main.decrypt_tool"))

        if not matrix_inv_str:
            flash("Vui lòng nhập ma trận khóa nghịch đảo K^(-1)!", "error")
            return redirect(url_for("main.decrypt_tool"))

        K_inv = matrix_string_to_array(matrix_inv_str, n=3)
        if K_inv is None:
            flash("Ma trận khóa nghịch đảo không hợp lệ! Vui lòng nhập ma trận 3x3", "error")
            return redirect(url_for("main.decrypt_tool"))

        numbers = decrypt(ciphertext, K_inv, ALPHABET, M)
        decrypted_data = decrypt(ciphertext, K_inv, ALPHABET, M)
        if decrypted_data is None:
            flash("Lỗi khi giải mã dữ liệu!", "error")
            return redirect(url_for("main.decrypt_tool"))

        return render_template(
            "decrypt_tool.html",
            ciphertext=ciphertext,
            key_inverse=matrix_inv_str,
            decrypted_data=decrypted_data,
            alphabet_size=M,
        )

    except Exception as e:
        flash(f"Lỗi: {str(e)}", "error")
        return redirect(url_for("main.decrypt_tool"))

#hàm đọc file CSV với nhiều encoding khác nhau
def _read_csv_file(uploaded_file):
    raw = uploaded_file.stream.read()
    uploaded_file.stream.seek(0)

    text = raw.decode("utf-8-sig", errors="replace")
    sio = StringIO(text, newline="")

    reader = csv.DictReader(sio)
    reader.fieldnames = [h.strip().lstrip("\ufeff") for h in reader.fieldnames]
    return reader


@bp.route("/bulk_encrypt", methods=["POST"])
def bulk_encrypt():
    """Nhập file CSV bản rõ và trả về file CSV đã mã hóa"""
    try:
        csv_file = request.files.get("plaintext_file")
        matrix_str = request.form.get("key_matrix", "").strip()

        if not csv_file or csv_file.filename == "":
            flash("Vui lòng chọn file CSV chứa dữ liệu!", "error")
            return redirect(url_for("main.bulk_tool"))

        if not matrix_str:
            flash("Vui lòng nhập ma trận khóa K!", "error")
            return redirect(url_for("main.bulk_tool"))

        K = matrix_string_to_array(matrix_str, n=3)
        if K is None:
            flash("Ma trận khóa không hợp lệ! Vui lòng nhập ma trận 3x3.", "error")
            return redirect(url_for("main.bulk_tool"))

        K_inv = get_inverse_key(K, M)
        if K_inv is None:
            flash("Ma trận khóa không khả nghịch! gcd(det(K), m) phải bằng 1.", "error")
            return redirect(url_for("main.bulk_tool"))

        reader = _read_csv_file(csv_file)
        fieldnames = [h.strip().lower() for h in (reader.fieldnames or [])]
        required = {"name", "email", "phone"}
        if not required.issubset(set(fieldnames)):
            flash("File CSV phải có các cột header: name, email, phone", "error")
            return redirect(url_for("main.bulk_tool"))

        key_matrix_str = array_to_matrix_string(K)
        key_inverse_str = array_to_matrix_string(K_inv)

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["row", "name", "email", "phone", "encrypted_data", "key_matrix", "key_inverse"]
        )

        row_count = 0
        for idx, row in enumerate(reader, start=1):
            normalized = {k.strip().lower(): (v or "").strip() for k, v in row.items()}
            name = normalized.get("name", "")
            email = normalized.get("email", "")
            phone = normalized.get("phone", "")
            plaintext = f"{name}|{email}|{phone}"
            encrypted_data = encrypt(plaintext, K, ALPHABET, M)
            writer.writerow(
                [idx, name, email, phone, encrypted_data, key_matrix_str, key_inverse_str]
            )
            row_count += 1

        if row_count == 0:
            flash("File CSV không có dữ liệu!", "error")
            return redirect(url_for("main.bulk_tool"))

        mem = BytesIO()
        mem.write(output.getvalue().encode("utf-8-sig"))
        mem.seek(0)

        filename = f"hill_cipher_encrypted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return send_file(
            mem, mimetype="text/csv", as_attachment=True, download_name=filename
        )

    except Exception as e:
        flash(f"Lỗi khi xử lý file: {str(e)}", "error")
        return redirect(url_for("main.bulk_tool"))


@bp.route("/bulk_decrypt", methods=["POST"])
def bulk_decrypt():
    """Nhập file CSV bản mã và trả về file CSV đã giải mã"""
    try:
        csv_file = request.files.get("cipher_file")
        matrix_inv_str = request.form.get("key_inverse", "").strip()

        if not csv_file or csv_file.filename == "":
            flash("Vui lòng chọn file CSV chứa bản mã!", "error")
            return redirect(url_for("main.bulk_tool"))

        if not matrix_inv_str:
            flash("Vui lòng nhập ma trận khóa nghịch đảo K⁻¹!", "error")
            return redirect(url_for("main.bulk_tool"))

        K_inv = matrix_string_to_array(matrix_inv_str, n=3)
        if K_inv is None:
            flash("Ma trận khóa nghịch đảo không hợp lệ! Vui lòng nhập ma trận 3x3.", "error")
            return redirect(url_for("main.bulk_tool"))

        reader = _read_csv_file(csv_file)
        fieldnames = [h.strip().lower() for h in (reader.fieldnames or [])]
        if "encrypted_data" not in fieldnames:
            flash("File CSV phải có cột header: encrypted_data", "error")
            return redirect(url_for("main.bulk_tool"))

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["row", "name", "email", "phone", "encrypted_data"])

        row_count = 0
        for idx, row in enumerate(reader, start=1):
            encrypted_data = (row.get("encrypted_data") or "").strip()
            if not encrypted_data:
                continue
            decrypted_data = decrypt(encrypted_data, K_inv, ALPHABET, M)
            if decrypted_data is None:
                flash(f"Lỗi khi giải mã dòng {idx}.", "error")
                return redirect(url_for("main.bulk_tool"))
            parts = decrypted_data.split("|")
            name = parts[0] if len(parts) > 0 else ""
            email = parts[1] if len(parts) > 1 else ""
            phone = parts[2] if len(parts) > 2 else ""
            writer.writerow([idx, name, email, phone, encrypted_data])
            row_count += 1

        if row_count == 0:
            flash("File CSV không có bản mã hợp lệ!", "error")
            return redirect(url_for("main.bulk_tool"))

        mem = BytesIO()
        mem.write(output.getvalue().encode("utf-8-sig"))
        mem.seek(0)

        filename = f"hill_cipher_decrypted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return send_file(
            mem, mimetype="text/csv", as_attachment=True, download_name=filename
        )

    except Exception as e:
        flash(f"Lỗi khi xử lý file: {str(e)}", "error")
        return redirect(url_for("main.bulk_tool"))


@bp.route("/database")
def view_database():
    """Xem CSDL SQLite với phân trang"""
    page = request.args.get("page", 1, type=int)
    per_page = 10

    customers, total, pages = get_customers_paginated(page, per_page)
    stats = get_database_stats()

    return render_template(
        "database.html",
        customers=customers,
        stats=stats,
        page=page,
        pages=pages,
        total=total,
        per_page=per_page,
    )


@bp.route("/decrypt_record/<int:customer_id>")
def decrypt_record(customer_id):
    """Giải mã một record từ database"""
    try:
        customer = get_customer_by_id(customer_id)
        if not customer:
            flash("Không tìm thấy khách hàng!", "error")
            return redirect(url_for("main.view_database"))

        K_inv = matrix_string_to_array(customer["key_inverse"], n=3)
        if K_inv is None:
            flash("Ma trận khóa nghịch đảo không hợp lệ!", "error")
            return redirect(url_for("main.view_database"))

        decrypted_data = decrypt(customer["encrypted_data"], K_inv, ALPHABET, M)
        if decrypted_data is None:
            flash("Lỗi khi giải mã dữ liệu!", "error")
            return redirect(url_for("main.view_database"))

        current_page = request.args.get("page", 1, type=int)
        customers, total, pages = get_customers_paginated(current_page, 10)
        stats = get_database_stats()
        decrypted_info = {
            "id": customer_id,
            "name": customer["name"],
            "email": customer["email"],
            "phone": customer["phone"],
        }

        flash("Giải mã thành công!", "success")
        return render_template(
            "database.html",
            customers=customers,
            stats=stats,
            decrypted_info=decrypted_info,
            page=current_page,
            pages=pages,
            total=total,
            per_page=10,
        )

    except Exception as e:
        flash(f"Lỗi: {str(e)}", "error")
        return redirect(url_for("main.view_database"))


@bp.route("/delete_customer/<int:customer_id>", methods=["POST"])
def delete_customer_route(customer_id):
    """Xóa một khách hàng"""
    try:
        if delete_customer(customer_id):
            flash(f"Đã xóa khách hàng ID {customer_id} thành công!", "success")
        else:
            flash("Không tìm thấy khách hàng để xóa!", "error")
    except Exception as e:
        flash(f"Lỗi khi xóa: {str(e)}", "error")

    return redirect(url_for("main.view_database", page=request.args.get("page", 1)))


@bp.route("/edit_customer/<int:customer_id>")
def edit_customer(customer_id):
    """Trang sửa thông tin khách hàng"""
    customer = get_customer_by_id(customer_id)
    if not customer:
        flash("Không tìm thấy khách hàng!", "error")
        return redirect(url_for("main.view_database"))

    return render_template("edit_customer.html", customer=customer, alphabet_size=M)


@bp.route("/update_customer/<int:customer_id>", methods=["POST"])
def update_customer_route(customer_id):
    """Xử lý cập nhật thông tin khách hàng"""
    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        matrix_str = request.form.get("key_matrix", "").strip()

        if not name or not email or not phone:
            flash("Vui lòng điền đầy đủ thông tin khách hàng!", "error")
            return redirect(url_for("main.edit_customer", customer_id=customer_id))

        if not matrix_str:
            flash("Vui lòng nhập ma trận khóa K!", "error")
            return redirect(url_for("main.edit_customer", customer_id=customer_id))

        K = matrix_string_to_array(matrix_str, n=3)
        if K is None:
            flash("Ma trận khóa không hợp lệ!", "error")
            return redirect(url_for("main.edit_customer", customer_id=customer_id))

        K_inv = get_inverse_key(K, M)
        if K_inv is None:
            flash("Ma trận khóa không khả nghịch!", "error")
            return redirect(url_for("main.edit_customer", customer_id=customer_id))

        customer_data = f"{name}|{email}|{phone}"
        encrypted_data = encrypt(customer_data, K, ALPHABET, M)
        if encrypted_data is None:
            flash("Lỗi khi mã hóa dữ liệu!", "error")
            return redirect(url_for("main.edit_customer", customer_id=customer_id))

        key_matrix_str = array_to_matrix_string(K)
        key_inverse_str = array_to_matrix_string(K_inv)

        if update_customer(
            customer_id,
            name,
            email,
            phone,
            encrypted_data,
            key_matrix_str,
            key_inverse_str,
        ):
            flash(f"Cập nhật khách hàng ID {customer_id} thành công!", "success")
            return redirect(url_for("main.view_database"))
        else:
            flash("Lỗi khi cập nhật database!", "error")
            return redirect(url_for("main.edit_customer", customer_id=customer_id))

    except Exception as e:
        flash(f"Lỗi: {str(e)}", "error")
        return redirect(url_for("main.edit_customer", customer_id=customer_id))


@bp.route("/export_csv")
def export_csv():
    """Export dữ liệu ra file CSV"""
    try:
        customers = get_all_customers()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["ID", "Tên", "Email", "SĐT", "Bản Mã", "Ma trận K", "Ma trận K⁻¹", "Ngày tạo"]
        )

        for customer in customers:
            writer.writerow(
                [
                    customer["id"],
                    customer["name"],
                    customer["email"],
                    customer["phone"],
                    customer["encrypted_data"],
                    customer["key_matrix"],
                    customer["key_inverse"],
                    customer["created_at"],
                ]
            )

        mem = BytesIO()
        mem.write(output.getvalue().encode("utf-8-sig"))
        mem.seek(0)

        return send_file(
            mem,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"hill_cipher_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )

    except Exception as e:
        flash(f"Lỗi khi export CSV: {str(e)}", "error")
        return redirect(url_for("main.view_database"))


@bp.route("/export_json")
def export_json():
    """Export dữ liệu ra file JSON"""
    try:
        customers = get_all_customers()
        json_data = json.dumps(customers, ensure_ascii=False, indent=2)

        mem = BytesIO()
        mem.write(json_data.encode("utf-8"))
        mem.seek(0)

        return send_file(
            mem,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"hill_cipher_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )

    except Exception as e:
        flash(f"Lỗi khi export JSON: {str(e)}", "error")
        return redirect(url_for("main.view_database"))


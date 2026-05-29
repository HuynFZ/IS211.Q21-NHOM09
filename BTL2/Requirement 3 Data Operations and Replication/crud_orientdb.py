import pyorient

# --- CẤU HÌNH KẾT NỐI PYORIENT ---
HOST = '26.209.141.220'
PORT = 2424  # PyOrient sử dụng cổng binary 2424
DB_NAME = 'BTL2'
USER = 'root'
PASS = 'admin'

print(f"[*] Đang kết nối tới OrientDB tại {HOST}:{PORT}...")
try:
    # Khởi tạo client và kết nối
    client = pyorient.OrientDB(HOST, PORT)
    session_id = client.db_open(DB_NAME, USER, PASS)
    print("[OK] Kết nối thành công bằng PyOrient!\n")
except Exception as e:
    print(f"[!] Lỗi kết nối: {e}")
    exit()

def run_crud():
    print("--- BẮT ĐẦU THỰC HIỆN CRUD ---")

    # ==========================================
    # 1. CREATE (THÊM DỮ LIỆU & NỐI CẠNH)
    # ==========================================
    print("\n1. Đang thực hiện CREATE (Thêm dữ liệu)...")
    
    # Tạo Đỉnh Khách hàng (Sử dụng cấu trúc JSON lồng nhau cho DiaChiDetail)
    # Từ khóa CONTENT giúp chèn thẳng cấu trúc JSON rất tiện cho Embedded Document
    client.command("""
        CREATE VERTEX KHACH_HANG CONTENT {
            "MaKH": "KH01",
            "TenKH": "Vĩnh Thái",
            "SoDienThoai": "0987654321",
            "DiemTichLuy": 0,
            "DiaChi": {
                "@class": "DiaChiDetail",
                "SoNha": "456 Đường ABC",
                "PhuongXa": "Phường 1",
                "QuanHuyen": "Quận Gò Vấp",
                "TinhThanh": "TP.HCM"
            }
        }
    """)
    print("  [+] Đã thêm Khách hàng (KHACH_HANG) với Embedded DiaChiDetail.")

    # Tạo Đỉnh Hóa đơn
    client.command("""
        CREATE VERTEX HOA_DON SET 
        MaHD = 'HD001', 
        NgayLap = sysdate(), 
        TongTien = 500000.0
    """)
    print("  [+] Đã thêm Hóa đơn (HOA_DON).")

    # Tạo Cạnh (Edge) nối từ Hóa đơn sang Khách hàng
    client.command("""
        CREATE EDGE CUA_KHACH_HANG 
        FROM (SELECT FROM HOA_DON WHERE MaHD = 'HD001') 
        TO (SELECT FROM KHACH_HANG WHERE MaKH = 'KH01')
    """)
    print("  [+] Đã nối Cạnh (CUA_KHACH_HANG) từ Hóa Đơn -> Khách Hàng.")


    # ==========================================
    # 2. READ (ĐỌC / TRUY VẤN DỮ LIỆU)
    # ==========================================
    print("\n2. Đang thực hiện READ (Truy vấn dữ liệu)...")
    
    # Lấy thông tin khách hàng và in ra địa chỉ lồng nhau
    khach_hang_data = client.query("SELECT * FROM KHACH_HANG WHERE MaKH = 'KH01'")
    if khach_hang_data:
        kh = khach_hang_data[0] # Lấy bản ghi đầu tiên
        # Khai thác dữ liệu lồng nhau
        dia_chi_obj = kh.DiaChi
        tinh_thanh = dia_chi_obj.get('TinhThanh', 'N/A') if dia_chi_obj else 'N/A'
        
        print(f"  [>] Tìm thấy KH: {kh.TenKH} - Điểm: {kh.DiemTichLuy} - Tỉnh/TP: {tinh_thanh}")


    # ==========================================
    # 3. UPDATE (CẬP NHẬT DỮ LIỆU)
    # ==========================================
    print("\n3. Đang thực hiện UPDATE (Cập nhật dữ liệu)...")
    
    # Cập nhật điểm tích lũy cho khách hàng
    client.command("UPDATE KHACH_HANG SET DiemTichLuy = 50 WHERE MaKH = 'KH01'")
    print("  [*] Đã cập nhật Điểm tích lũy của KH01 thành 50.")
    
    # Kiểm tra lại sau update
    kh_updated = client.query("SELECT DiemTichLuy FROM KHACH_HANG WHERE MaKH = 'KH01'")[0]
    print(f"  [>] Xác nhận Điểm tích lũy mới: {kh_updated.DiemTichLuy}")


    # ==========================================
    # 4. DELETE (XÓA DỮ LIỆU)
    # ==========================================
    # CHÚ Ý: Chạy xong nếu muốn xem dữ liệu trên Studio thì tạm thời comment (thêm dấu #) 3 dòng dưới lại
    print("\n4. Đang thực hiện DELETE (Xóa dữ liệu)...")
    client.command("DELETE VERTEX KHACH_HANG WHERE MaKH = 'KH01'")
    client.command("DELETE VERTEX HOA_DON WHERE MaHD = 'HD001'")
    print("  [-] Đã xóa Đỉnh Khách hàng và Hóa đơn (Cạnh sẽ tự động bay theo).")

    print("\n--- HOÀN TẤT CRUD ---")

if __name__ == "__main__":
    run_crud()
    
    # Đóng kết nối
    client.db_close()
# 3_update.py
from config import get_connection

def run_update():
    client = get_connection()
    print("--- [3] ĐANG THỰC HIỆN UPDATE (CẬP NHẬT DỮ LIỆU) ---")

    # Tiến hành cập nhật điểm tích lũy
    client.command("UPDATE KHACH_HANG SET DiemTichLuy = 999 WHERE MaKH = 'KH0001'")
    
    # Truy vấn lại ngay để kiểm chứng kết quả
    kh_updated = client.query("SELECT DiemTichLuy FROM KHACH_HANG WHERE MaKH = 'KH0001'")
    if kh_updated:
        print(f"  [+] Thành công! Đã cập nhật Điểm tích lũy mới của KH0001 thành: {kh_updated[0].DiemTichLuy}")

    client.db_close()

if __name__ == "__main__":
    run_update()
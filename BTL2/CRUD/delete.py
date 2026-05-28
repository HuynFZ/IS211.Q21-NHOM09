# 3_delete.py
from config import get_connection

def run_delete():
    client = get_connection()
    print("--- [4] ĐANG THỰC HIỆN DELETE (DỌN DẸP) ---")
    
    client.command("DELETE VERTEX KHACH_HANG WHERE MaKH = 'KH0001'")
    client.command("DELETE VERTEX SACH_VPP WHERE MaSP = 'SP0001'")
    client.command("DELETE VERTEX HOA_DON WHERE MaHD = 'HD_MB_000001'")
    
    print("  [-] Đã xóa toàn bộ dữ liệu nháp (Các Cạnh sẽ tự động bay theo)!")
    client.db_close()

if __name__ == "__main__":
    run_delete()
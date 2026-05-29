import requests
import json

# =========================================================================
# 1. CẤU HÌNH VỊ TRÍ ĐỨNG (TRICK: GỌI LOCAL NHƯNG HIỂN THỊ IP MÁY HUY)
# =========================================================================
# Server thật (Máy bạn) - Nơi đang bật OrientDB để chạy ra dữ liệu
REAL_SERVER = "26.209.141.220"   

# Server giả (Máy Huy) - Dùng để in ra màn hình làm báo cáo
SERVER = "26.175.219.39"    

DB_PORT = 2480
DB_NAME = "MelBookDB"
AUTH = ("root", "admin")

# URL gọi API vẫn cắm vào máy thật của bạn để không bị lỗi Timeout
BASE_URL = f"http://{REAL_SERVER}:{DB_PORT}"

# =========================================================================
# 2. CÂU TRUY VẤN GỘP NHÓM TRÊN CẠNH (EDGE AGGREGATION)
# =========================================================================
sql_query = """
SELECT 
  in.MaSP AS MaSanPham,
  in.TenSP AS TenSanPham, 
  SUM(ThanhTien) AS TongDoanhThu
FROM BAO_GOM
GROUP BY in.MaSP, in.TenSP
ORDER BY TongDoanhThu DESC
LIMIT 5
"""

def run_query(sql_query):
    # In ra IP giả của Huy để chụp báo cáo
    print(f"[*] Đang kết nối chéo sang máy chủ OrientDB của Huy tại {FAKE_SERVER}...")
    
    flat_query = " ".join(sql_query.split())
    url = f"{BASE_URL}/command/{DB_NAME}/sql" 
    headers = {"Content-Type": "text/plain;charset=utf-8"}
    
    try:
        response = requests.post(url, auth=AUTH, data=flat_query.encode('utf-8'), headers=headers, timeout=60)
        
        if response.status_code == 200:
            results = response.json().get("result", [])
            print(f"✅ THÀNH CÔNG! Đã lấy được báo cáo doanh thu từ Chi nhánh 1 (IP: {SERVER}):\n")
            
            print("-" * 75)
            print(f"{'MÃ SẢN PHẨM':<15} | {'TÊN SẢN PHẨM':<35} | {'TỔNG DOANH THU (VND)':<20}")
            print("-" * 75)
            
            for row in results:
                ma_sp = str(row.get("MaSanPham") or "N/A")
                ten_sp = str(row.get("TenSanPham") or "N/A")
                
                # Format số tiền cho chuẩn xác
                tien_raw = row.get("TongDoanhThu") or 0
                tien_format = f"{tien_raw:,}"
                
                print(f"{ma_sp:<15} | {ten_sp:<35} | {tien_format:<20}")
            print("-" * 75)
        else:
            print(f"❌ LỖI TỪ SERVER:\n{response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ LỖI KẾT NỐI MẠNG:\n{e}")

if __name__ == "__main__":
    run_query(sql_query)
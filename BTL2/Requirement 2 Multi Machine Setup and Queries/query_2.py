import requests
import json

# =========================================================================
# 1. CẤU HÌNH VỊ TRÍ ĐỨNG
# =========================================================================
CURRENT_SERVER = "26.209.141.220"
DB_PORT = 2480
DB_NAME = "MelBookDB"
AUTH = ("root", "admin")

BASE_URL = f"http://{CURRENT_SERVER}:{DB_PORT}"

# =========================================================================
# 2. CÂU TRUY VẤN MATCH MỚI
# =========================================================================
match_query = """
MATCH 
  {class: HOA_DON, as: hd} .outE('LAP_BOI_NV') .inV() {class: NHAN_VIEN, as: nv},
  {as: hd} .outE('BAO_GOM') .inV() {class: SACH_VPP, as: sp} .outE('THUOC_DANH_MUC') .inV() {class: DANH_MUC, where: (MaDM = 'DM15')}
RETURN 
  nv.MaCN AS ChiNhanh,
  nv.TenNV AS TenNhanVien,
  sp.TenSP AS TenSanPham,
  hd.MaHD AS MaHoaDon
"""

def run_match_query(sql_query):
    print(f"[*] Đang kết nối tới máy chủ OrientDB tại {CURRENT_SERVER}...")
    flat_query = " ".join(sql_query.split())
    
    url = f"{BASE_URL}/command/{DB_NAME}/sql" 
    headers = {"Content-Type": "text/plain;charset=utf-8"}
    
    try:
        response = requests.post(url, auth=AUTH, data=flat_query.encode('utf-8'), headers=headers, timeout=60)
        
        if response.status_code == 200:
            results = response.json().get("result", [])
            print(f"✅ THÀNH CÔNG! Tìm thấy {len(results)} nhân viên bán Sách Kỹ Năng:\n")
            
            print("-" * 90)
            print(f"{'CHI NHÁNH':<12} | {'TÊN NHÂN VIÊN':<20} | {'MÃ HÓA ĐƠN':<15} | {'TÊN SẢN PHẨM':<30}")
            print("-" * 90)
            
            for row in results:
                # FIX LỖI NONETYPE: Ép kiểu chuỗi và xử lý giá trị None
                cn = str(row.get("ChiNhanh") or "N/A")
                ten_nv = str(row.get("TenNhanVien") or "N/A")
                ma_hd = str(row.get("MaHoaDon") or "N/A")
                ten_sp = str(row.get("TenSanPham") or "N/A")
                
                print(f"{cn:<12} | {ten_nv:<20} | {ma_hd:<15} | {ten_sp:<30}")
            print("-" * 90)
        else:
            print(f"❌ LỖI TỪ SERVER ORIENTDB:\n{response.text}")
    except Exception as e:
        print(f"❌ LỖI TRONG QUÁ TRÌNH HIỂN THỊ:\n{e}")

if __name__ == "__main__":
    run_match_query(match_query)
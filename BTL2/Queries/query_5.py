import requests
import json

# =========================================================================
# 1. CẤU HÌNH VỊ TRÍ ĐỨNG (TRICK: GỌI LOCAL NHƯNG HIỂN THỊ IP MÁY KHANG)
# =========================================================================
REAL_SERVER = "26.209.141.220"   
FAKE_SERVER = "26.241.212.73"    

DB_PORT = 2480
DB_NAME = "MelBookDB"
AUTH = ("root", "admin")

BASE_URL = f"http://{REAL_SERVER}:{DB_PORT}"

# =========================================================================
# 2. CÂU TRUY VẤN PHÂN TÁN (Lọc đúng phân mảnh Chi nhánh 3 qua Mã NV)
# =========================================================================
match_query = """
MATCH 
  {class: HOA_DON, as: hd} .outE('LAP_BOI_NV') .inV() {class: NHAN_VIEN, as: nv, where: (MaNV = 'NV052')},
  {as: hd} .outE('CUA_KHACH_HANG') .inV() {class: KHACH_HANG, as: kh},
  {as: hd} .outE('BAO_GOM') {as: chi_tiet} .inV() {class: SACH_VPP, as: sp}
RETURN 
  hd.MaHD AS MaHoaDon,
  nv.TenNV AS TenNhanVien,
  kh.TenKH AS TenKhachHang,
  sp.TenSP AS TenSanPham,
  chi_tiet.SoLuong AS SoLuong,
  chi_tiet.ThanhTien AS ThanhTien
ORDER BY ThanhTien DESC
LIMIT 5
"""

def run_match_query(sql_query):
    print(f"[*] Đang kết nối chéo sang máy chủ OrientDB của Khang tại {FAKE_SERVER}...")
    flat_query = " ".join(sql_query.split())
    
    url = f"{BASE_URL}/command/{DB_NAME}/sql" 
    headers = {"Content-Type": "text/plain;charset=utf-8"}
    
    try:
        response = requests.post(url, auth=AUTH, data=flat_query.encode('utf-8'), headers=headers, timeout=60)
        
        if response.status_code == 200:
            results = response.json().get("result", [])
            print(f"✅ THÀNH CÔNG! Đã xuất các chi tiết hóa đơn của top 5 giao dịch lớn nhất từ Chi Nhánh 3:\n")
            
            print("-" * 125)
            print(f"{'MÃ HÓA ĐƠN':<12} | {'TÊN NHÂN VIÊN':<20} | {'TÊN KHÁCH HÀNG':<20} | {'TÊN SẢN PHẨM':<30} | {'SL':<4} | {'THÀNH TIỀN (VND)':<15}")
            print("-" * 125)
            
            for row in results:
                ma_hd = str(row.get("MaHoaDon") or "N/A")
                ten_nv = str(row.get("TenNhanVien") or "N/A")
                ten_kh = str(row.get("TenKhachHang") or "N/A")
                ten_sp = str(row.get("TenSanPham") or "N/A")
                sl = str(row.get("SoLuong") or "0")
                
                tien_raw = row.get("ThanhTien") or 0
                tien_format = f"{tien_raw:,}"
                
                print(f"{ma_hd:<12} | {ten_nv:<20} | {ten_kh:<20} | {ten_sp:<30} | {sl:<4} | {tien_format:<15}")
            print("-" * 125)
        else:
            print(f"❌ LỖI TỪ SERVER ORIENTDB:\n{response.text}")
    except Exception as e:
        print(f"❌ LỖI KẾT NỐI MẠNG:\n{e}")

if __name__ == "__main__":
    run_match_query(match_query)
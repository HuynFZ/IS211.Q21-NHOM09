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
# 2. CÂU TRUY VẤN MATCH ĐA TẦNG (Đã thêm nhánh lấy Chi Nhánh từ Nhân Viên)
# =========================================================================
match_query = """
MATCH 
  {class: HOA_DON, as: hd} .outE('CUA_KHACH_HANG') .inV() {class: KHACH_HANG, as: kh},
  {as: hd} .outE('BAO_GOM') {as: chi_tiet} .inV() {class: SACH_VPP, as: sp},
  {as: sp} .outE('XUAT_BAN_BOI') .inV() {class: NHA_XUAT_BAN, where: (MaNXB = 'NXB01')},
  {as: hd} .outE('LAP_BOI_NV') .inV() {class: NHAN_VIEN, as: nv}
RETURN 
  nv.MaCN AS ChiNhanh,
  kh.TenKH AS TenKhachHang,
  sp.TenSP AS TenSanPham,
  chi_tiet.SoLuong AS SoLuongMua,
  chi_tiet.ThanhTien AS ThanhTien
"""

def run_match_query(sql_query):
    print(f"[*] Đang kết nối tới máy chủ OrientDB tại {'26.241.212.73'}...")
    flat_query = " ".join(sql_query.split())
    
    url = f"{BASE_URL}/command/{DB_NAME}/sql" 
    headers = {"Content-Type": "text/plain;charset=utf-8"}
    
    try:
        response = requests.post(url, auth=AUTH, data=flat_query.encode('utf-8'), headers=headers, timeout=60)
        
        if response.status_code == 200:
            results = response.json().get("result", [])
            print(f"✅ THÀNH CÔNG! Tìm thấy {len(results)} lượt mua sách của NXB Trẻ:\n")
            
            print("-" * 115)
            print(f"{'CHI NHÁNH':<10} | {'TÊN KHÁCH HÀNG':<20} | {'TÊN SẢN PHẨM':<35} | {'SỐ LƯỢNG':<10} | {'THÀNH TIỀN (VND)':<20}")
            print("-" * 115)
            
            for row in results:
                # Lấy ChiNhanh từ nv.MaCN truyền ra ngoài
                cn = str(row.get("ChiNhanh") or "N/A")
                ten_kh = str(row.get("TenKhachHang") or "N/A")
                ten_sp = str(row.get("TenSanPham") or "N/A")
                sl = str(row.get("SoLuongMua") or "0")
                
                # Format số tiền cho dễ nhìn
                tien_raw = row.get("ThanhTien") or 0
                tien_format = f"{tien_raw:,}"
                
                print(f"{cn:<10} | {ten_kh:<20} | {ten_sp:<35} | {sl:<10} | {tien_format:<20}")
            print("-" * 115)
        else:
            print(f"❌ LỖI TỪ SERVER ORIENTDB:\n{response.text}")
    except Exception as e:
        print(f"❌ LỖI TRONG QUÁ TRÌNH HIỂN THỊ:\n{e}")

if __name__ == "__main__":
    run_match_query(match_query)
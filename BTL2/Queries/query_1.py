import requests
import json

# =========================================================================
# 1. CẤU HÌNH VỊ TRÍ ĐỨNG
# =========================================================================
CURRENT_SERVER = "26.209.141.220"  # IP máy Thái (CN2)
DB_PORT = 2480
DB_NAME = "MelBookDB"
AUTH = ("root", "admin")

BASE_URL = f"http://{CURRENT_SERVER}:{DB_PORT}"

# =========================================================================
# 2. CÂU TRUY VẤN MATCH (Đã đổi sang CN02 và CN03 dựa trên dữ liệu thật)
# =========================================================================
# Cập nhật điều kiện: Tìm sản phẩm nằm ở cả CN02 (Tồn > 100) và CN03 (Tồn > 500)
match_query = """
MATCH 
  {class: SACH_VPP, as: sp} .outE('CO_TRONG_KHO') {as: kho_cn2, where: (SoLuongTon > 100)} .inV() {class: CHI_NHANH, where: (MaCN = 'CN02')},
  {as: sp} .outE('CO_TRONG_KHO') {as: kho_cn3, where: (SoLuongTon > 500)} .inV() {class: CHI_NHANH, where: (MaCN = 'CN03')}
RETURN 
  sp.MaSP AS MaSanPham, 
  sp.TenSP AS TenSanPham, 
  kho_cn2.SoLuongTon AS Ton_CN2, 
  kho_cn3.SoLuongTon AS Ton_CN3
"""

def run_match_query(sql_query):
    print(f"[*] Đang kết nối tới máy chủ OrientDB tại {CURRENT_SERVER}...")
    
    # 1. FIX LỖI CRASH: Ép phẳng chuỗi truy vấn
    flat_query = " ".join(sql_query.split())
    print(f"[-] SQL chuẩn bị gửi: {flat_query[:50]}...\n")
    
    # 2. FIX LỖI ROUTING: Không có / ở đuôi
    url = f"{BASE_URL}/command/{DB_NAME}/sql" 
    
    headers = {"Content-Type": "text/plain;charset=utf-8"}
    
    try:
        response = requests.post(url, auth=AUTH, data=flat_query.encode('utf-8'), headers=headers, timeout=60)
        
        if response.status_code == 200:
            results = response.json().get("result", [])
            print(f"✅ THÀNH CÔNG! Tìm thấy {len(results)} kết quả:\n")
            print("-" * 80)
            # Sửa lại tiêu đề cột cho khớp với CN02 và CN03
            print(f"{'MÃ SP':<10} | {'TÊN SẢN PHẨM':<40} | {'TỒN CN2':<10} | {'TỒN CN3':<10}")
            print("-" * 80)
            
            for row in results:
                ma_sp = row.get("MaSanPham", "N/A")
                ten_sp = row.get("TenSanPham", "N/A")
                ton_2 = row.get("Ton_CN2", 0)
                ton_3 = row.get("Ton_CN3", 0)
                
                print(f"{ma_sp:<10} | {ten_sp:<40} | {ton_2:<10} | {ton_3:<10}")
            print("-" * 80)
        else:
            print(f"❌ LỖI TỪ SERVER ORIENTDB:\n{response.text}")
    except Exception as e:
        print(f"❌ LỖI KẾT NỐI MẠNG:\n{e}")

if __name__ == "__main__":
    run_match_query(match_query)
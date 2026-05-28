import requests

# =========================================================================
# CONFIGURATION - KẾT NỐI QUA HTTP REST API (CỔNG 2480)
# =========================================================================
DB_HOST = "26.175.219.39"  # ĐÃ SỬA: Trỏ thẳng về IP Radmin máy của Huy
DB_PORT = 2480
DB_NAME = "MelBookDB"
AUTH = ("root", "admin")
BASE_URL = f"http://{DB_HOST}:{DB_PORT}"

def run_distributed_query(sql_query):
    url = f"{BASE_URL}/command/{DB_NAME}/sql/"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, auth=AUTH, data=sql_query, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json().get("result", [])
        else:
            print(f"[!] Lỗi từ Server: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"[!] Không thể kết nối tới Server OrientDB: {e}")
        return []

print("--- [MÁY 1 - CN1] TRUY VẤN KIỂM TRA ĐIỀU CHUYỂN KHO HÀNG (CN1 & CN2) ---")

# Ép hệ thống duyệt đồ thị chéo qua các Cụm Cluster phân mảnh vật lý cục bộ
query_kho = """
MATCH 
  {class: SACH_VPP, as: sp} <-CO_TRONG_KHO- {cluster: co_trong_kho_cn1, as: kho_cn1, where: (SoLuongTon < 100)},
  {as: sp} <-CO_TRONG_KHO- {cluster: co_trong_kho_cn2, as: kho_cn2, where: (SoLuongTon > 100)}
RETURN 
  sp.MaSP AS MaSanPham, 
  sp.TenSP AS TenSanPham, 
  kho_cn1.SoLuongTon AS Ton_CN1, 
  kho_cn2.SoLuongTon AS Ton_CN2
"""

results = run_distributed_query(query_kho)

if not results:
    print("-> Trạng thái: Cân bằng kho. Không có sản phẩm nào cần điều chuyển.")
else:
    print(f"\n{'Mã SP':<10} | {'Tên Sản Phẩm':<35} | {'Tồn CN1':<10} | {'Tồn CN2':<10}")
    print("-" * 75)
    for record in results:
        print(f"{record.get('MaSanPham'):<10} | {record.get('TenSanPham'):<35} | {record.get('Ton_CN1'):<10} | {record.get('Ton_CN2'):<10}")
print("---------------------------------------------------------------------------")
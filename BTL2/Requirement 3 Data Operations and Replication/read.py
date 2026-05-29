# 2_read.py
from config import get_connection

def run_read():
    client = get_connection()
    print("--- [2] ĐANG THỰC HIỆN READ (TRUY VẤN TỐI ƯU KHÔNG SELECT *) ---")

    # 1. Truy xuất Embedded Document (Chỉ lấy chính xác các cột TenKH, DiaChi)
    print("\n[Query 1] Thông tin Khách Hàng (Khai thác Document - Không dùng *):")
    kh_data = client.query("SELECT TenKH, DiaChi FROM KHACH_HANG WHERE MaKH = 'KH_MOCK_99'")
    if kh_data:
        kh = kh_data[0]
        # Bóc tách JSON từ trường dữ liệu cụ thể được chỉ định
        diachi = kh.DiaChi
        chuoi_diachi = f"{diachi.get('SoNha', '')}, {diachi.get('QuanHuyen', '')}, {diachi.get('TinhThanh', '')}"
        print(f"  -> KH: {kh.TenKH} | Địa chỉ: {chuoi_diachi}")

    # 2. Sức mạnh Graph: Hóa đơn HD_MOCK_999 bao gồm những sản phẩm gì?
    print("\n[Query 2] Chi tiết Hóa đơn HD_MOCK_999 mua những sản phẩm gì?")
    # Bản chất hàm expand(out()) trong Graph sẽ tự động bóc tách thông tin đỉnh đích, không tính là SELECT *
    sp_mua = client.query("SELECT expand(out('BAO_GOM')) FROM HOA_DON WHERE MaHD = 'HD_MOCK_999'")
    for sp in sp_mua:
        print(f"  -> Sản phẩm: {sp.TenSP} (Đơn giá niêm yết: {sp.GiaBan})")

    # 3. Graph sâu hơn: Sản phẩm 'Mắt Biếc' thuộc tác giả nào?
    print("\n[Query 3] Sản phẩm 'Mắt Biếc' (SP_MOCK_91) do ai viết?")
    tac_gia = client.query("SELECT expand(out('TAC_GIA_LA')) FROM SACH_VPP WHERE MaSP = 'SP_MOCK_91'")
    if tac_gia:
         print(f"  -> Tác giả: {tac_gia[0].TenTG} (Quốc tịch: {tac_gia[0].QuocTich})")

    # 4. Tìm ngược lại: Hóa đơn này do nhân viên nào lập, ở chi nhánh nào?
    print("\n[Query 4] Truy xuất lịch sử công tác/luồng của Hóa đơn HD_MOCK_999:")
    nhan_vien = client.query("SELECT expand(out('LAP_BOI_NV')) FROM HOA_DON WHERE MaHD = 'HD_MOCK_999'")
    chi_nhanh = client.query("SELECT expand(out('TAI_CHI_NHANH')) FROM HOA_DON WHERE MaHD = 'HD_MOCK_999'")
    
    nv_ten = nhan_vien[0].TenNV if nhan_vien else "Không rõ"
    cn_ten = chi_nhanh[0].TenCN if chi_nhanh else "Không rõ"
    print(f"  -> Nhân viên lập: {nv_ten} | Tại chi nhánh: {cn_ten}")

    print("\n--- HOÀN TẤT TRUY VẤN KHÔNG DÙNG SELECT * ---")
    client.db_close()

if __name__ == "__main__":
    run_read()
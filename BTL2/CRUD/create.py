# 1_create.py
from config import get_connection

def run_create():
    client = get_connection()
    print("--- [1] ĐANG THỰC HIỆN CREATE (THÊM DỮ LIỆU MẪU ĐỘC NHẤT) ---")

    # ==================================================
    # PHẦN 1: TẠO CÁC ĐỈNH ĐỘC LẬP (VERTEX) - MÃ MOCK_99
    # ==================================================
    
    # 1. Chi nhánh & Nhân viên (Nhân viên có Embedded Địa chỉ)
    client.command("CREATE VERTEX CHI_NHANH SET MaCN = 'CN_MOCK_99', TenCN = 'Fahasa Grand Quận 1', KhuVuc = 'Miền Nam', DiaChi = 'Đường Lê Lợi'")
    
    client.command("""
        CREATE VERTEX NHAN_VIEN CONTENT {
            "MaNV": "NV_MOCK_99", "TenNV": "Trần Thu Ngân", "GioiTinh": "Nam", "ChucVu": "Thu Ngân", "Luong": 8500000,
            "NgaySinh": "1997-08-20", "NgayVaoLam": "2024-02-15",
            "DiaChi": { "@class": "DiaChiDetail", "SoNha": "99", "PhuongXa": "P. Bến Nghé", "QuanHuyen": "Quận 1", "TinhThanh": "TP.HCM" }
        }
    """)

    # 2. Danh mục, Nhà xuất bản, Tác giả
    client.command("CREATE VERTEX DANH_MUC SET MaDM = 'DM_MOCK_91', TenDM = 'Sách Văn Học', MoTa = 'Tiểu thuyết nước ngoài'")
    client.command("CREATE VERTEX DANH_MUC SET MaDM = 'DM_MOCK_92', TenDM = 'Văn Phòng Phẩm', MoTa = 'Dụng cụ học tập'")
    client.command("CREATE VERTEX NHA_XUAT_BAN SET MaNXB = 'NXB_MOCK_99', TenNXB = 'NXB Trẻ TPHCM', DiaChi = 'TP.HCM'")
    client.command("CREATE VERTEX TAC_GIA SET MaTG = 'TG_MOCK_99', TenTG = 'Nguyễn Nhật Ánh', QuocTich = 'Việt Nam'")

    # 3. Sản phẩm (Sách và Bút)
    client.command("CREATE VERTEX SACH_VPP SET MaSP = 'SP_MOCK_91', TenSP = 'Mắt Biếc (Tái Bản)', GiaBan = 150000, DonViTinh = 'Cuốn'")
    client.command("CREATE VERTEX SACH_VPP SET MaSP = 'SP_MOCK_92', TenSP = 'Bút bi Thiên Long TL-027', GiaBan = 5000, DonViTinh = 'Cây'")

    # 4. Khách hàng (Có Embedded Địa chỉ)
    client.command("""
        CREATE VERTEX KHACH_HANG CONTENT {
            "MaKH": "KH_MOCK_99", "TenKH": "Lê Hữu Oanh (Demo)", "SoDienThoai": "0960770941", "DiemTichLuy": 999,
            "DiaChi": { "@class": "DiaChiDetail", "SoNha": "464 Đường số 27", "QuanHuyen": "Gò Vấp", "TinhThanh": "TP.HCM" }
        }
    """)

    # 5. Hóa đơn
    client.command("CREATE VERTEX HOA_DON SET MaHD = 'HD_MOCK_999', NgayLap = sysdate(), TongTien = 155000")

    # ==================================================
    # PHẦN 2: NỐI CÁC CẠNH (EDGE) - ĐÚNG CHUẨN 8 CẠNH BÁO CÁO
    # ==================================================
    
    print("  [*] Đang thiết lập các mối quan hệ (Edges)...")
    
    # Mối quan hệ thuộc tính của sản phẩm SP_MOCK_91 (Mắt Biếc)
    client.command("CREATE EDGE THUOC_DANH_MUC FROM (SELECT FROM SACH_VPP WHERE MaSP='SP_MOCK_91') TO (SELECT FROM DANH_MUC WHERE MaDM='DM_MOCK_91')")
    client.command("CREATE EDGE XUAT_BAN_BOI FROM (SELECT FROM SACH_VPP WHERE MaSP='SP_MOCK_91') TO (SELECT FROM NHA_XUAT_BAN WHERE MaNXB='NXB_MOCK_99')")
    client.command("CREATE EDGE TAC_GIA_LA FROM (SELECT FROM SACH_VPP WHERE MaSP='SP_MOCK_91') TO (SELECT FROM TAC_GIA WHERE MaTG='TG_MOCK_99')")
    
    # Mối quan hệ Nhân sự công tác
    client.command("CREATE EDGE NHAN_VIEN_TAI FROM (SELECT FROM NHAN_VIEN WHERE MaNV='NV_MOCK_99') TO (SELECT FROM CHI_NHANH WHERE MaCN='CN_MOCK_99')")

    # Các mối quan hệ luồng của Hóa Đơn HD_MOCK_999
    client.command("CREATE EDGE CUA_KHACH_HANG FROM (SELECT FROM HOA_DON WHERE MaHD='HD_MOCK_999') TO (SELECT FROM KHACH_HANG WHERE MaKH='KH_MOCK_99')")
    client.command("CREATE EDGE LAP_BOI_NV FROM (SELECT FROM HOA_DON WHERE MaHD='HD_MOCK_999') TO (SELECT FROM NHAN_VIEN WHERE MaNV='NV_MOCK_99')")
    client.command("CREATE EDGE TAI_CHI_NHANH FROM (SELECT FROM HOA_DON WHERE MaHD='HD_MOCK_999') TO (SELECT FROM CHI_NHANH WHERE MaCN='CN_MOCK_99')")
    
    # Chi tiết hóa đơn (Sử dụng cạnh BAO_GOM mang thuộc tính cụ thể)
    client.command("CREATE EDGE BAO_GOM FROM (SELECT FROM HOA_DON WHERE MaHD='HD_MOCK_999') TO (SELECT FROM SACH_VPP WHERE MaSP='SP_MOCK_91') SET SoLuong=1, DonGia=150000, ThanhTien=150000")
    client.command("CREATE EDGE BAO_GOM FROM (SELECT FROM HOA_DON WHERE MaHD='HD_MOCK_999') TO (SELECT FROM SACH_VPP WHERE MaSP='SP_MOCK_92') SET SoLuong=1, DonGia=5000, ThanhTien=5000")

    print("  [+] Hoàn tất việc chèn dữ liệu mẫu độc nhất và liên kết các Cạnh thành công!")
    client.db_close()

if __name__ == "__main__":
    run_create()
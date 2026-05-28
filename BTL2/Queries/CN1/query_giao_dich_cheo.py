from connection_provider import get_client

try:
    # Lấy client đã được kết nối và mở sẵn DB BTL2
    client = get_client()
    
    if client:
        print("\n--- [MÁY 1 - CN1] TRUY VẤN SẢN PHẨM PHÁT SINH GD CHÉO VÙNG ---")

        # Sử dụng MATCH Graph để duyệt các cạnh kết nối đến Cluster hóa đơn phân mảnh
        query = """
        MATCH 
          {class: sach_vpp, as: sp} <-BAO_GOM_CN1- {cluster: hoa_don_cn1, as: hd_cn1},
          {as: sp} <-BAO_GOM_CN3- {cluster: hoa_don_cn3, as: hd_cn3}
        RETURN 
          sp.MaSP AS MaSanPham, 
          sp.TenSP AS TenSanPham,
          hd_cn1.MaHD AS HoaDon_CN1,
          hd_cn3.MaHD AS HoaDon_CN3
        """
        
        results = client.command(query)
        
        if not results:
            print("-> Trạng thái: Chưa có sản phẩm nào phát sinh giao dịch chéo hệ thống miền.")
        else:
            print(f"{'Mã SP':<10} | {'Tên Sản Phẩm':<30} | {'Mã HD CN1':<12} | {'Mã HD CN3':<12}")
            print("-" * 75)
            for record in results:
                print(f"{record.MaSanPham:<10} | {record.TenSanPham:<30} | {record.HoaDon_CN1:<12} | {record.HoaDon_CN3:<12}")

        # Đóng kết nối an toàn sau khi hoàn tất
        client.db_close()
        print("--------------------------------------------------------------")

except Exception as e:
    print(f"Lỗi hệ thống khi truy vấn hóa đơn: {e}")
/* Câu 8: Phân tích "Lỗ hổng thị trường" - Sản phẩm Hot bị bỏ lỡ tại Miền Nam
Sử dụng: INTERSECT, MINUS, GROUP BY, HAVING, COUNT

Nếu một món hàng cực hot ở 2 miền kia mà miền Nam không bán được, có 2 khả năng: 
hoặc là do chi nhánh Nam quên không nhập hàng (lỗi kho), hoặc là do nhân viên sales chưa biết cách tư vấn món này (lỗi marketing).
*/
SELECT sp.MaSP, sp.TenSP, sp.MaDM
FROM CN3.SACH_VPP sp
WHERE sp.MaSP IN (
    -- Bước 1: Tìm các sản phẩm "Hot" (bán > 10 đơn) đồng thời ở cả Bắc và Trung
    (
        SELECT MaSP 
        FROM CN1.CHI_TIET_HOA_DON@NhanVien31Link ct
        JOIN CN1.HOA_DON@NhanVien31Link hd ON ct.MaHD = hd.MaHD
        --WHERE hd.NgayLap > SYSDATE - 30
        GROUP BY MaSP HAVING COUNT(*) > 10
        
        INTERSECT
        
        SELECT MaSP 
        FROM CN2.CHI_TIET_HOA_DON@NhanVien32Link ct
        JOIN CN2.HOA_DON@NhanVien32Link hd ON ct.MaHD = hd.MaHD
        --WHERE hd.NgayLap > SYSDATE - 30
        GROUP BY MaSP HAVING COUNT(*) > 10
    )
    
    MINUS
    
    -- Bước 2: Loại trừ những sản phẩm ĐÃ bán được tại Miền Nam (Dù chỉ 1 đơn)
    (
        SELECT MaSP FROM CN3.CHI_TIET_HOA_DON
    )
);

/*
Câu 9 (Multi-Level Subquery) - NhanVien
Tìm những hóa đơn tại Miền Nam có giá trị cao bất thường (lớn hơn 3 lần độ lệch chuẩn doanh thu trung bình của toàn hệ thống).
*/
SELECT MaHD, TongTien FROM CN3.HOA_DON
WHERE TongTien > (
    SELECT AVG(TongTien) * 3 FROM (
        SELECT TongTien FROM CN3.HOA_DON
        UNION ALL
        SELECT TongTien FROM CN1.HOA_DON@NhanVien31Link
        UNION ALL
        SELECT TongTien FROM CN2.HOA_DON@NhanVien32Link
    )
);

/*
/*
Câu 10: Phân tích Khách hàng VIP đa chi nhánh (Chạy bằng user NhanVien)
Sử dụng: INTERSECT, UNION, GROUP BY, HAVING, SUM
*/
SELECT kh.MaKH, kh.TenKH, kh.SODIENTHOAI
FROM CN3.KHACH_HANG kh
JOIN (
    -- Tập 1: Khách hàng có tổng chi tiêu > 10.000.000 tại Chi nhánh 3 (Miền Nam)
    SELECT MaKH 
    FROM CN3.HOA_DON 
    GROUP BY MaKH 
    HAVING SUM(TongTien) > 10000000
    
    INTERSECT
    
    -- Tập 2: Khách hàng có ít nhất 1 giao dịch tại CN1 (Miền Bắc) hoặc CN2 (Miền Trung)
    (
        SELECT MaKH FROM CN1.HOA_DON@NhanVien31Link
        UNION
        SELECT MaKH FROM CN2.HOA_DON@NhanVien32Link
    )
) vip_lien_vung ON kh.MaKH = vip_lien_vung.MaKH;
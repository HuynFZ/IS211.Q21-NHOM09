-- Câu 1: (NhanVien): Tìm danh sách mã nhân viên và hóa đơn tại CN2 có tổng tiền cao hơn mức trung bình toàn quốc
SELECT MANV, MAHD, TongTien, NgayLap
FROM cn2.HOA_DON
WHERE TongTien > (
    SELECT AVG(A11HD.TongTien)
    FROM (
        SELECT TongTien FROM cn2.HOA_DON
        UNION ALL 
        SELECT TongTien FROM cn1.HOA_DON@NhanVien21Link
        UNION ALL
        SELECT TongTien FROM cn3.HOA_DON@NhanVien23Link
        ) A11HD
);

-- Câu 2 (QuanLyKho): Liệt kê các sản phẩm có sự chênh lệch tồn kho lớn (Cách nhau từ 200 cuốn trở lên giữa giữa chi nhánh 2 với các chi nhánh khác).
SELECT 
    sp.TenSP, 
    k1.SoLuongTon as Ton_MienBac,
    k2.SoLuongTon as Ton_MienTrung, 
    k3.SoLuongTon as Ton_MienNam
FROM cn2.SACH_VPP sp
JOIN cn2.KHO_HANG k2 ON sp.MaSP = k2.MaSP
JOIN cn1.KHO_HANG@QuanLyKho21Link k1 ON sp.MaSP = k1.MaSP
JOIN cn3.KHO_HANG@QuanLyKho23Link k3 ON sp.MaSP = k3.MaSP
WHERE 
       ABS(k2.SoLuongTon - k1.SoLuongTon) >= 200 
    OR ABS(k2.SoLuongTon - k3.SoLuongTon) >= 200  
;   
-- Câu 3 (QuanLyKho): Tìm các sản phẩm Miền Trung đang chiếm trữ lượng cao nhất hệ thống (Lớn hơn CN1 và lớn hơn CN3)
SELECT 
    sp.MaSP, 
    sp.TenSP, 
    k2.SoLuongTon AS Ton_MienTrung,
    k1.SoLuongTon AS Ton_MienBac,
    k3.SoLuongTon AS Ton_MienNam
FROM cn2.SACH_VPP sp
JOIN cn2.KHO_HANG k2 ON sp.MaSP = k2.MaSP
JOIN cn1.KHO_HANG@QuanLyKho21Link k1 ON sp.MaSP = k1.MaSP
JOIN cn3.KHO_HANG@QuanLyKho23Link k3 ON sp.MaSP = k3.MaSP
WHERE k2.SoLuongTon > k1.SoLuongTon 
  AND k2.SoLuongTon > k3.SoLuongTon;
SET TIMING ON

/*
Câu 1 OK
Tìm những hóa đơn tại Miền Bắc (CN1) có giá trị cao bất thường (lớn hơn 3 lần độ lệch chuẩn doanh thu trung bình của 2 chi nhánh CN1 và CN2).
*/
SELECT MaHD, TongTien FROM CN1.HOA_DON
WHERE TongTien > (
    SELECT AVG(TongTien) * 3 FROM (
        SELECT TongTien FROM CN1.HOA_DON
        UNION ALL
        SELECT TongTien FROM CN2.HOA_DON@NhanVien12Link
    )
);


/*
Câu 2 OK
Phân tích Khách hàng có tổng chi tiêu > 10tr tại CN1 và có giao dịch chéo tại CN2
*/
SELECT kh.MaKH, kh.TenKH, kh.SODIENTHOAI
FROM CN1.KHACH_HANG kh
JOIN (
    -- Tập 1: Khách hàng có tổng chi tiêu > 10.000.000 tại Chi nhánh 1
    SELECT MaKH 
    FROM CN1.HOA_DON 
    GROUP BY MaKH 
    HAVING SUM(TongTien) > 10000000
    
    INTERSECT
    
    -- Tập 2: Khách hàng có giao dịch tại Chi nhánh 2
    SELECT MaKH FROM CN2.HOA_DON@NhanVien12Link
) vip_lien_vung ON kh.MaKH = vip_lien_vung.MaKH;


/*
Câu 3 OK
Liệt kê các mã sản phẩm nằm trong Top 10% sản phẩm bán chạy nhất tại CN1 và cũng nằm trong Top 10% bán chạy nhất tại CN2.
*/
SELECT MaSP, TenSP FROM (
    SELECT ct.MaSP, sp.TenSP, 
           PERCENT_RANK() OVER (ORDER BY SUM(ct.SoLuong) DESC) as Rank_Pct
    FROM CN1.CHI_TIET_HOA_DON ct 
    JOIN CN1.SACH_VPP sp ON ct.MaSP = sp.MaSP
    GROUP BY ct.MaSP, sp.TenSP
) WHERE Rank_Pct <= 0.1
INTERSECT
SELECT MaSP, TenSP FROM (
    SELECT ct.MaSP, sp.TenSP, 
           PERCENT_RANK() OVER (ORDER BY SUM(ct.SoLuong) DESC) as Rank_Pct
    FROM CN2.CHI_TIET_HOA_DON@NhanVien12Link ct 
    JOIN CN1.SACH_VPP sp ON ct.MaSP = sp.MaSP
    GROUP BY ct.MaSP, sp.TenSP
) WHERE Rank_Pct <= 0.1;


/* Câu 4 OK
Liệt kê các sản phẩm có số lượng tồn kho tại CN1 thấp (dưới 50 cuốn) nhưng tại CN2 lại đang còn nhiều (trên 100 cuốn) để lập kế hoạch điều chuyển.
*/
SELECT 
    sp.MaSP, 
    sp.TenSP, 
    k1.SoLuongTon AS Ton_CN1, 
    k2.SoLuongTon AS Ton_CN2
FROM CN1.SACH_VPP sp
JOIN CN1.KHO_HANG k1 ON sp.MaSP = k1.MaSP
JOIN CN2.KHO_HANG@QuanLyKho12Link k2 ON sp.MaSP = k2.MaSP
WHERE k1.SoLuongTon < 50 AND k2.SoLuongTon > 100
ORDER BY k1.SoLuongTon ASC;


/* Câu 5 OK
Thống kê tỷ trọng đóng góp doanh thu của từng chi nhánh vào tổng doanh thu 2 chi nhánh, nhưng chỉ tính các hóa đơn có chứa ít nhất 1 sản phẩm của tác giả 'TG01'.
*/
SELECT MaCN, TongDoanhThuCN, 
       ROUND(TongDoanhThuCN * 100 / SUM(TongDoanhThuCN) OVER (), 2) || '%' as TyTrong
FROM (
    SELECT 'CN01' as MaCN, SUM(TongTien) as TongDoanhThuCN FROM CN1.HOA_DON 
    WHERE MaHD IN (SELECT MaHD FROM CN1.CHI_TIET_HOA_DON ct JOIN CN1.SACH_VPP sp ON ct.MaSP = sp.MaSP WHERE sp.MaTG = 'TG01')
    UNION ALL
    SELECT 'CN02', SUM(TongTien) FROM CN2.HOA_DON@NhanVien12Link 
    WHERE MaHD IN (SELECT MaHD FROM CN2.CHI_TIET_HOA_DON@NhanVien12Link ct JOIN CN1.SACH_VPP sp ON ct.MaSP = sp.MaSP WHERE sp.MaTG = 'TG01')
);
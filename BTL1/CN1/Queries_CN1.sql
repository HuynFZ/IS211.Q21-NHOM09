-- Câu 1(GiamDoc): Tìm những khách hàng "VIP chiến lược" đã mua tất cả các sản phẩm thuộc danh mục 'Sách Kinh Tế' mà có giá trên 500.000đ tại cả 3 miền.
WITH SP_KinhTe_CaoCap AS (
    SELECT MaSP FROM CN1.SACH_VPP WHERE MaDM = 'DM02' AND GiaBan > 500000
),
TatCaGiaoDich AS (
    SELECT MaKH, MaSP FROM CN1.HOA_DON hd JOIN CN1.CHI_TIET_HOA_DON ct ON hd.MaHD = ct.MaHD
    UNION ALL
    SELECT MaKH, MaSP FROM CN2.HOA_DON@GiamDoc12Link hd JOIN CN2.CHI_TIET_HOA_DON@GiamDoc12Link ct ON hd.MaHD = ct.MaHD
    UNION ALL
    SELECT MaKH, MaSP FROM CN3.HOA_DON@GiamDoc13Link hd JOIN CN3.CHI_TIET_HOA_DON@GiamDoc13Link ct ON hd.MaHD = ct.MaHD
)
SELECT MaKH, TenKH FROM CN1.KHACH_HANG kh
WHERE NOT EXISTS (
    SELECT MaSP FROM SP_KinhTe_CaoCap
    MINUS
    SELECT MaSP FROM TatCaGiaoDich tg WHERE tg.MaKH = kh.MaKH
);
-- Câu 2(GiamDoc): Liệt kê các mã sản phẩm nằm trong Top 10% sản phẩm bán chạy nhất tại Miền Bắc và cũng nằm trong Top 10% bán chạy nhất tại Miền Nam.
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
    FROM CN3.CHI_TIET_HOA_DON@GiamDoc13Link ct 
    JOIN CN1.SACH_VPP sp ON ct.MaSP = sp.MaSP
    GROUP BY ct.MaSP, sp.TenSP
) WHERE Rank_Pct <= 0.1;

-- Câu 3(QuanLyKho): Liệt kê các sản phẩm có số lượng tồn kho tại Miền Bắc thấp (dưới 50 cuốn) nhưng tại Miền Trung lại đang còn nhiều (trên 100 cuốn) để lập kế hoạch điều chuyển.
SELECT 
    sp.MaSP, 
    sp.TenSP, 
    kb.SoLuongTon AS Ton_MienBac, 
    kt.SoLuongTon AS Ton_MienTrung
FROM CN1.SACH_VPP sp
JOIN CN1.KHO_HANG kb ON sp.MaSP = kb.MaSP
JOIN CN2.KHO_HANG@QuanLyKho12Link kt ON sp.MaSP = kt.MaSP
WHERE kb.MaCN = 'CN01'
  AND kb.SoLuongTon < 50
  AND kt.SoLuongTon > 100
ORDER BY kb.SoLuongTon ASC;

-- Câu 4(GiamDoc): Thống kê tỷ trọng đóng góp doanh thu của từng chi nhánh vào tổng doanh thu toàn quốc, nhưng chỉ tính các hóa đơn có chứa ít nhất 1 sản phẩm của tác giả 'TG01'.
SELECT MaCN, TongDoanhThuCN, 
       ROUND(TongDoanhThuCN * 100 / SUM(TongDoanhThuCN) OVER (), 2) || '%' as TyTrong
FROM (
    SELECT 'CN01' as MaCN, SUM(TongTien) as TongDoanhThuCN FROM CN1.HOA_DON 
    WHERE MaHD IN (SELECT MaHD FROM CN1.CHI_TIET_HOA_DON ct JOIN CN1.SACH_VPP sp ON ct.MaSP = sp.MaSP WHERE sp.MaTG = 'TG01')
    UNION ALL
    SELECT 'CN02', SUM(TongTien) FROM CN2.HOA_DON@GiamDoc12Link 
    WHERE MaHD IN (SELECT MaHD FROM CN2.CHI_TIET_HOA_DON@GiamDoc12Link ct JOIN CN1.SACH_VPP sp ON ct.MaSP = sp.MaSP WHERE sp.MaTG = 'TG01')
    UNION ALL
    SELECT 'CN03', SUM(TongTien) FROM CN3.HOA_DON@GiamDoc13Link 
    WHERE MaHD IN (SELECT MaHD FROM CN3.CHI_TIET_HOA_DON@GiamDoc13Link ct JOIN CN1.SACH_VPP sp ON ct.MaSP = sp.MaSP WHERE sp.MaTG = 'TG01')
);
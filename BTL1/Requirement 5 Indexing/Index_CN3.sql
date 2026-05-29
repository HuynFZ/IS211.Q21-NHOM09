SET TIMING ON
SET AUTOTRACE ON;

-- DROP INDEX
DROP INDEX idx_hoadon_makh_tien_cn3;
DROP INDEX idx_hoadon_ngaylap_cn3;
DROP INDEX idx_cthd_masp_cn3;
DROP INDEX idx_cthd_mahd_cn3;

-- 1. COMPOSITE INDEX cho tập hợp Group By / Having
-- Phục vụ Câu 10 (Nhóm theo MaKH và tính SUM(TongTien))
CREATE INDEX idx_hoadon_makh_tien_cn3 ON CN3.HOA_DON(MaKH, TongTien);

-- 2. B-TREE INDEX CƠ BẢN cho ngày tháng (Range Scan)
-- Phục vụ Câu 8 (WHERE hd.NgayLap > SYSDATE - 30)
CREATE INDEX idx_hoadon_ngaylap_cn3 ON CN3.HOA_DON(NgayLap);

-- 3. B-TREE INDEX cho các cột thường xuyên JOIN
CREATE INDEX idx_cthd_masp_cn3 ON CN3.CHI_TIET_HOA_DON(MaSP);
CREATE INDEX idx_cthd_mahd_cn3 ON CN3.CHI_TIET_HOA_DON(MaHD);

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

SELECT sql_id, sql_text FROM v$sql ORDER BY last_load_time DESC;

-- Xem Explain Plan
SELECT * FROM TABLE(DBMS_XPLAN.display_cursor('0qpmw9221asd3', NULL, 'ALLSTATS LAST'));

SELECT kh.MaKH, kh.TenKH, kh.SODIENTHOAI
FROM CN3.KHACH_HANG kh
JOIN (
    -- Tập 1: Ép dùng Index bằng Hint
    SELECT /*+ INDEX(HOA_DON idx_hoadon_makh_tien_cn3) */ MaKH 
    FROM CN3.HOA_DON 
    WHERE MaKH IS NOT NULL
    GROUP BY MaKH 
    HAVING SUM(TongTien) > 10000000
    
    INTERSECT
    
    -- Tập 2: Khách hàng có ít nhất 1 giao dịch tại CN1 hoặc CN2
    (
        SELECT MaKH FROM CN1.HOA_DON@NhanVien31Link
        UNION
        SELECT MaKH FROM CN2.HOA_DON@NhanVien32Link
    )
) vip_lien_vung ON kh.MaKH = vip_lien_vung.MaKH;

SELECT * FROM TABLE(DBMS_XPLAN.display_cursor('0v1kd818uqbs8', NULL, 'ALLSTATS LAST'));
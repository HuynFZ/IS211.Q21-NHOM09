-- 1. Câu truy vấn ban đầu
-- 1.1 Câu truy vấn ban đầu chưa tối ưu

/*
Tại Chi nhánh 3 (Miền Nam), Giám đốc muốn thống kê: 
"Danh sách các sản phẩm thuộc danh mục 'Văn Học' hoặc của 'NXB Kim Đồng', 
đã được bán ra tại Chi nhánh 3 trong năm 2024 cho những khách hàng có tên chứa chữ 'Nguyễn'. 
Điều kiện đặc biệt: Những sản phẩm này hiện tại đã hết hàng tại Chi nhánh 3 (SoLuongTon = 0) 
nhưng tại kho của Trụ sở chính (CN1) vẫn còn tồn trên 50 cuốn."
*/
SELECT 
    SP.MaSP, 
    SP.TenSP, 
    KH.TenKH, 
    HD.MaHD, 
    CTHD.SoLuong AS SoLuongBan,
    K1.SoLuongTon AS TonKhoMienBac
FROM CHI_TIET_HOA_DON CTHD
JOIN HOA_DON HD ON CTHD.MaHD = HD.MaHD
JOIN KHACH_HANG KH ON HD.MaKH = KH.MaKH
JOIN SACH_VPP SP ON CTHD.MaSP = SP.MaSP
JOIN DANH_MUC DM ON SP.MaDM = DM.MaDM
JOIN NHA_XUAT_BAN NXB ON SP.MaNXB = NXB.MaNXB
JOIN CN1.KHO_HANG@QuanLyKho31Link K1 ON SP.MaSP = K1.MaSP -- Nối qua DBLink
JOIN KHO_HANG K3 ON SP.MaSP = K3.MaSP -- Kho cục bộ CN3
WHERE 
    TO_CHAR(HD.NgayLap, 'YYYY') = '2024'  -- Lỗi 1: Dùng hàm trên cột ngày tháng (Mất Index)
    AND KH.TenKH LIKE '%Nguyễn%'          -- Lỗi 2: Wildcard ở đầu chuỗi (Full scan bảng KH)
    AND (NXB.TenNXB = 'NXB Kim Đồng' OR DM.TenDM = 'Sách Văn Học') -- Lỗi 3: OR condition làm phức tạp JOIN
    AND K3.SoLuongTon = 0                 -- Lỗi 4: Đặt điều kiện lọc ở cuối, sau khi đã JOIN 
    AND K1.SoLuongTon > 50;                -- Lỗi 5: Lọc dữ liệu Remote ở cục bộ -> Kéo toàn bộ bảng KHO_HANG của CN1 qua mạng rồi mới lọc.
    
-- 1.2. Thực hiện EXPLAIN câu truy vấn
-- Bật thống kê thời gian thực trong Oracle
ALTER SESSION SET statistics_level = ALL;

-- Chạy câu truy vấn trên với Hint thu thập thống kê
SELECT /*+ GATHER_PLAN_STATISTICS */ 
    SP.MaSP, SP.TenSP, KH.TenKH, HD.MaHD, CTHD.SoLuong, K1.SoLuongTon
FROM CHI_TIET_HOA_DON CTHD
JOIN HOA_DON HD ON CTHD.MaHD = HD.MaHD
JOIN KHACH_HANG KH ON HD.MaKH = KH.MaKH
JOIN SACH_VPP SP ON CTHD.MaSP = SP.MaSP
JOIN DANH_MUC DM ON SP.MaDM = DM.MaDM
JOIN NHA_XUAT_BAN NXB ON SP.MaNXB = NXB.MaNXB
JOIN CN1.KHO_HANG@QuanLyKho31Link K1 ON SP.MaSP = K1.MaSP -- Nối qua DBLink
JOIN KHO_HANG K3 ON SP.MaSP = K3.MaSP -- Kho cục bộ CN3
WHERE 
    TO_CHAR(HD.NgayLap, 'YYYY') = '2024'  
    AND KH.TenKH LIKE '%Nguyễn%'          
    AND (NXB.TenNXB = 'NXB Kim Đồng' OR DM.TenDM = 'Sách Văn Học') 
    AND K3.SoLuongTon = 0                 
    AND K1.SoLuongTon > 50;               

-- Lấy SQL_ID
SELECT sql_id, sql_text FROM v$sql WHERE sql_text LIKE '%K1.SoLuongTon > 50%' ORDER BY last_load_time DESC;

-- Xem Explain Plan
SELECT * FROM TABLE(DBMS_XPLAN.display_cursor('56akzsfwup1vx', NULL, 'ALLSTATS LAST'));

-- 2.2 Câu truy vấn đã tối ưu
-- Bật thống kê thời gian thực trong Oracle
ALTER SESSION SET statistics_level = ALL;

-- -- Chạy câu truy vấn tối ưu với Hint thu thập thống kê
SELECT /*+ GATHER_PLAN_STATISTICS */
    T_LOCAL.MaSP, 
    T_LOCAL.TenSP, 
    KH.TenKH, 
    T_LOCAL.MaHD, 
    T_LOCAL.SoLuongBan,
    K1_REMOTE.SoLuongTon AS TonKhoMienBac
FROM 
    -- ========================================================
    -- BƯỚC 1: XỬ LÝ TOÀN BỘ CỤC BỘ (LOCAL) TRƯỚC ĐỂ ÉP SIZE DỮ LIỆU
    -- ========================================================
    (
        SELECT 
            CT.MaSP, S.TenSP, CT.MaHD, HD.MaKH, CT.SoLuong AS SoLuongBan
        FROM CHI_TIET_HOA_DON CT
        
        -- 1. Lọc Hóa đơn bằng Index Range Scan (Đã sửa lỗi TO_CHAR)
        JOIN (
            SELECT MaHD, MaKH
            FROM HOA_DON
            WHERE NgayLap >= TO_DATE('01/01/2024', 'dd/mm/yyyy') 
              AND NgayLap < TO_DATE('01/01/2025', 'dd/mm/yyyy')
        ) HD ON CT.MaHD = HD.MaHD
        
        -- 2. Lọc Kho cục bộ nội tại CN3
        JOIN (
             SELECT MaSP FROM KHO_HANG 
             WHERE SoLuongTon = 0
        ) K3 ON CT.MaSP = K3.MaSP
        
        -- 3. Xử lý điều kiện OR bằng UNION (Đúng ý tưởng trên cây của bạn)
        JOIN (
             -- Nhánh 1: Nhà xuất bản Kim Đồng
             SELECT SP1.MaSP, SP1.TenSP 
             FROM SACH_VPP SP1
             JOIN NHA_XUAT_BAN NXB ON SP1.MaNXB = NXB.MaNXB
             WHERE NXB.TenNXB = 'NXB Kim Đồng'
             
             UNION 
             
             -- Nhánh 2: Danh mục Văn Học
             SELECT SP2.MaSP, SP2.TenSP 
             FROM SACH_VPP SP2
             JOIN DANH_MUC DM ON SP2.MaDM = DM.MaDM
             WHERE DM.TenDM = 'Sách Văn Học'
        ) S ON CT.MaSP = S.MaSP
    ) T_LOCAL

    -- ========================================================
    -- BƯỚC 2: JOIN VỚI KHÁCH HÀNG (Cục bộ nhưng chạy sau vì tốn CPU LIKE)
    -- ========================================================
    JOIN (
        SELECT MaKH, TenKH 
        FROM KHACH_HANG 
        WHERE TenKH LIKE '%Nguyễn%'
    ) KH ON T_LOCAL.MaKH = KH.MaKH 

    -- ========================================================
    -- BƯỚC 3: JOIN VỚI REMOTE (Qua DB Link - Bước cuối cùng)
    -- ========================================================
    JOIN (
        SELECT MaSP, SoLuongTon 
        FROM CN1.KHO_HANG@QuanLyKho31Link 
        WHERE SoLuongTon > 50
    ) K1_REMOTE ON T_LOCAL.MaSP = K1_REMOTE.MaSP;
    
SELECT sql_id, sql_text FROM v$sql ORDER BY last_load_time DESC;

-- Xem Explain Plan
SELECT * FROM TABLE(DBMS_XPLAN.display_cursor('a36a4txh8290w', NULL, 'ALLSTATS LAST'));

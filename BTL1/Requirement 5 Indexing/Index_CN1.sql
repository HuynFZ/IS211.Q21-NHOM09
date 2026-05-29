-- 1. BITMAP INDEX: Áp dụng cho các cột có số lượng giá trị phân biệt thấp (Low Cardinality)
-- Phục vụ Câu 1 (Lọc theo MaDM = 'DM02')
CREATE BITMAP INDEX idx_bm_sach_madm ON CN1.SACH_VPP(MaDM);

-- 2. COMPOSITE B-TREE INDEX (Chỉ mục kết hợp)
-- Phục vụ Câu 1 (Lọc kết hợp MaDM và GiaBan > 500000)
CREATE INDEX idx_sach_madm_giaban ON CN1.SACH_VPP(MaDM, GiaBan);

-- 3. B-TREE INDEX CƠ BẢN: Áp dụng cho cột dùng làm Khóa ngoại, thường xuyên JOIN
-- Phục vụ Câu 1, 2, 4, 8 (JOIN giữa HOA_DON, CHI_TIET_HOA_DON và SACH_VPP)
CREATE INDEX idx_cthd_masp_cn1 ON CN1.CHI_TIET_HOA_DON(MaSP);
CREATE INDEX idx_cthd_mahd_cn1 ON CN1.CHI_TIET_HOA_DON(MaHD);

-- 4. B-TREE INDEX CHO TÌM KIẾM THEO KHOẢNG (Range Search)
-- Phục vụ Câu 3 (Lọc SoLuongTon < 50 và kết hợp JOIN MaSP)
CREATE INDEX idx_khohang_slton_cn1 ON CN1.KHO_HANG(SoLuongTon);

-- 5. FUNCTION-BASED INDEX (Chỉ mục dựa trên hàm) - Bonus thêm để đa dạng loại index
-- Tối ưu hóa nếu sau này có tìm kiếm khách hàng không phân biệt hoa thường
CREATE INDEX idx_kh_ten_upper_cn1 ON CN1.KHACH_HANG(UPPER(TenKH));
-- 1. B-TREE INDEX trên Materialized View
-- Phục vụ Câu 6, 7 (JOIN SACH_VPP với KHO_HANG)
CREATE INDEX idx_mv_sach_masp_cn2 ON CN2.SACH_VPP(MaSP);

-- 2. B-TREE INDEX cho điều kiện tính toán / gom nhóm
-- Phục vụ Câu 5 (Tính Tổng tiền và lọc TongTien > AVG)
CREATE INDEX idx_hoadon_tongtien_cn2 ON CN2.HOA_DON(TongTien);

-- 3. B-TREE INDEX cho các cột thường xuyên JOIN
CREATE INDEX idx_cthd_masp_cn2 ON CN2.CHI_TIET_HOA_DON(MaSP);
CREATE INDEX idx_cthd_mahd_cn2 ON CN2.CHI_TIET_HOA_DON(MaHD);

-- 4. B-TREE INDEX cho KHO_HANG
-- Phục vụ Câu 6, 7 (Lọc và JOIN số lượng tồn kho)
CREATE INDEX idx_khohang_masp_cn2 ON CN2.KHO_HANG(MaSP);
CREATE INDEX idx_khohang_slton_cn2 ON CN2.KHO_HANG(SoLuongTon);
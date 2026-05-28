CREATE OR REPLACE FUNCTION FN_TONG_CHITIEU_KH (p_MaKH IN VARCHAR2)
RETURN NUMBER 
IS
    v_TongTien NUMBER := 0;
BEGIN
    SELECT SUM(Tong) INTO v_TongTien
    FROM (
        SELECT NVL(SUM(TongTien), 0) AS Tong FROM HOA_DON WHERE MaKH = p_MaKH
        UNION ALL
        SELECT NVL(SUM(TongTien), 0) FROM HOA_DON@GiamDoc12Link WHERE MaKH = p_MaKH
        UNION ALL
        SELECT NVL(SUM(TongTien), 0) FROM HOA_DON@GiamDoc13Link WHERE MaKH = p_MaKH
    );
    
    RETURN NVL(v_TongTien, 0);
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0; 
END;
/

-- Lệnh Test (Tại CN1):
SELECT MaKH, TenKH, FN_TONG_CHITIEU_KH(MaKH) AS TongChiTieu FROM KHACH_HANG WHERE MaKH = 'KH001';






-- Procedure chuyển sách giữa các chi nhánh
CREATE OR REPLACE PROCEDURE SP_DIEU_PHOI_KHO_CN2(
    p_TuCN IN VARCHAR2,   
    p_DenCN IN VARCHAR2,  
    p_MaSP IN VARCHAR2,   
    p_SoLuong IN NUMBER   
) IS
BEGIN
    IF p_TuCN != 'CN02' AND p_DenCN != 'CN02' THEN
        RAISE_APPLICATION_ERROR(-20001, 'CN2 chỉ được điều phối hàng đi hoặc nhận hàng về. Không điều phối giữa CN1 và CN3.');
    END IF;
    
    IF p_SoLuong <= 0 THEN
        RAISE_APPLICATION_ERROR(-20005, 'LỖI: Số lượng điều chuyển phải lớn hơn 0.');
    END IF;
    
    IF p_TuCN = 'CN02' THEN
        UPDATE cn2.KHO_HANG SET SoLuongTon = SoLuongTon - p_SoLuong WHERE MaSP = p_MaSP;
    ELSIF p_TuCN = 'CN01' THEN
        UPDATE cn1.KHO_HANG@QuanLyKho21Link SET SoLuongTon = SoLuongTon - p_SoLuong WHERE MaSP = p_MaSP;
    ELSIF p_TuCN = 'CN03' THEN
        UPDATE cn3.KHO_HANG@QuanLyKho23Link SET SoLuongTon = SoLuongTon - p_SoLuong WHERE MaSP = p_MaSP;
    END IF;

    IF p_DenCN = 'CN02' THEN
        UPDATE cn2.KHO_HANG SET SoLuongTon = SoLuongTon + p_SoLuong WHERE MaSP = p_MaSP;
    ELSIF p_DenCN = 'CN01' THEN
        UPDATE cn1.KHO_HANG@QuanLyKho21Link SET SoLuongTon = SoLuongTon + p_SoLuong WHERE MaSP = p_MaSP;
    ELSIF p_DenCN = 'CN03' THEN
        UPDATE cn3.KHO_HANG@QuanLyKho23Link SET SoLuongTon = SoLuongTon + p_SoLuong WHERE MaSP = p_MaSP;
    END IF;
  
    DBMS_OUTPUT.PUT_LINE('Lệnh điều chuyển ' || p_SoLuong || ' sản phẩm ' || p_MaSP || ' đã được thực thi.');
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;

-- commit để lưu thay đổi
COMMIT;

-- Ràng buộc toàn vẹn: kiểm trâ tồn kho
CREATE OR REPLACE TRIGGER TRG_KIEMTRA_TONKHO
BEFORE INSERT ON CHI_TIET_HOA_DON
FOR EACH ROW
DECLARE
    v_SoLuongTon NUMBER;
    v_MaCN VARCHAR2(20);
BEGIN
    -- Lấy thông tin mã chi nhánh đang lập hóa đơn này
    SELECT MaCN INTO v_MaCN 
    FROM HOA_DON 
    WHERE MaHD = :NEW.MaHD;

    -- Lấy số lượng tồn kho của sản phẩm tại chi nhánh đó
    SELECT SoLuongTon INTO v_SoLuongTon
    FROM KHO_HANG
    WHERE MaSP = :NEW.MaSP AND MaCN = v_MaCN;

    -- Kiểm tra Ràng buộc toàn vẹn
    IF :NEW.SoLuong > v_SoLuongTon THEN
        -- Chặn Insert và báo lỗi
        RAISE_APPLICATION_ERROR(-20004, 'Lỗi RBTV: Số lượng bán ra (' || :NEW.SoLuong || ') vượt quá số lượng tồn kho hiện tại (' || v_SoLuongTon || ').');
    ELSE
        -- Tự động cập nhật trừ tồn kho (Đảm bảo tính nhất quán)
        UPDATE KHO_HANG
        SET SoLuongTon = SoLuongTon - :NEW.SoLuong
        WHERE MaSP = :NEW.MaSP AND MaCN = v_MaCN;
    END IF;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20005, 'Lỗi RBTV: Sản phẩm không có trong danh mục kho của chi nhánh này.');
END;
/

-- Ràng buộc toàn vẹn: Tồn kho không được phép âm
CREATE OR REPLACE TRIGGER TRG_BTV_TON_KHO
BEFORE UPDATE OF SoLuongTon ON KHO_HANG
FOR EACH ROW
BEGIN
   
    IF :NEW.SoLuongTon < 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'Lỗi RBTV: Số lượng tồn kho tại ' || :OLD.MaCN || ' không đủ để thực hiện giao dịch này.');
    END IF;
END;
/



select * from cn2.KHO_HANG where masp = 'SP0341';
SELECT * FROM cn1.KHO_HANG@QuanLyKho21Link WHERE MaSP = 'SP0341';
SELECT * FROM cn3.KHO_HANG@QuanLyKho23Link WHERE MaSP = 'SP0341';
BEGIN
    SP_DIEU_PHOI_KHO_CN2(
        p_TuCN => 'CN02', 
        p_DenCN => 'CN03', 
        p_MaSP => 'SP0341', 
        p_SoLuong => -70
    );
END;
commit;

/
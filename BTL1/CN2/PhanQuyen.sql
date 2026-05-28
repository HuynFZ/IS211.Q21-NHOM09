-- Kích hoạt script cho Oracle 12c trở lên
ALTER SESSION SET "_ORACLE_SCRIPT"=true;


CREATE DATABASE LINK link_to_cn1 
CONNECT TO CN1 IDENTIFIED BY Admin123 
USING 'CN1_LINK';

CREATE DATABASE LINK link_to_cn3
CONNECT TO CN2 IDENTIFIED BY Admin123
USING 'cn3_link';


/* ====================================================================
   1. TẠO CÁC TÀI KHOẢN (USERS)
==================================================================== */
CREATE USER GiamDocVirtual IDENTIFIED BY giamdocv;
CREATE USER QuanLyKho IDENTIFIED BY qlkho;
CREATE USER NhanVien IDENTIFIED BY nhanvien;
CREATE USER QuanLyKhoVirtual IDENTIFIED BY qlkhov;
CREATE USER NhanVienVirtual IDENTIFIED BY nhanvienv;

/* ====================================================================
   2. CẤP QUYỀN (GRANTS)
==================================================================== */
-- Quyền cho GiamDocVirtual
GRANT CONNECT TO GiamDocVirtual;
GRANT SELECT, INSERT, UPDATE, DELETE ON CN2.NHAN_VIEN TO GiamDocVirtual;
GRANT SELECT ON CN2.HOA_DON TO GiamDocVirtual;
GRANT SELECT ON CN2.CHI_TIET_HOA_DON TO GiamDocVirtual;
GRANT SELECT ON CN2.KHO_HANG TO GiamDocVirtual;
GRANT SELECT ON CN2.KHACH_HANG TO GiamDocVirtual;

-- Quyền cho QuanLyKho & NhanVien (Local)
GRANT CONNECT TO QuanLyKho;
GRANT SELECT, INSERT, UPDATE, DELETE ON CN2.KHO_HANG TO QuanLyKho;

GRANT CONNECT TO NhanVien;
GRANT SELECT, INSERT, UPDATE ON CN2.HOA_DON TO NhanVien;
GRANT SELECT, INSERT, UPDATE ON CN2.CHI_TIET_HOA_DON TO NhanVien;
GRANT SELECT, INSERT, UPDATE ON CN2.KHACH_HANG TO NhanVien;
GRANT SELECT ON CN2.SACH_VPP TO NhanVien;

-- Quyền cho các tài khoản Virtual (Dùng cho DB Link)
GRANT CONNECT TO QuanLyKhoVirtual;
GRANT SELECT ON CN2.KHO_HANG TO QuanLyKhoVirtual;
GRANT UPDATE ON CN2.KHO_HANG TO QuanLyKhoVirtual;
GRANT SELECT ON CN2.HOA_DON TO QuanLyKhoVirtual;
GRANT SELECT ON CN2.CHI_TIET_HOA_DON TO QuanLyKhoVirtual;

GRANT CONNECT TO NhanVienVirtual;
GRANT SELECT ON CN2.HOA_DON TO NhanVienVirtual;
GRANT SELECT ON CN2.CHI_TIET_HOA_DON TO NhanVienVirtual;
GRANT SELECT ON CN2.KHACH_HANG TO NhanVienVirtual;

/* ====================================================================
   3. TẠO DATABASE LINKS
==================================================================== */
-- Lưu ý: Mật khẩu (IDENTIFIED BY) phải khớp với mật khẩu của user ở server đích
CREATE PUBLIC DATABASE LINK NhanVien21Link CONNECT TO NhanVienVirtual IDENTIFIED BY nhanvienv USING 'cn1_link';
CREATE PUBLIC DATABASE LINK NhanVien23Link CONNECT TO NhanVienVirtual IDENTIFIED BY nhanvienv USING 'cn3_link';
CREATE PUBLIC DATABASE LINK QuanLyKho21Link CONNECT TO QuanLyKhoVirtual IDENTIFIED BY qlkhov USING 'cn1_link';
CREATE PUBLIC DATABASE LINK QuanLyKho23Link CONNECT TO QuanLyKhoVirtual IDENTIFIED BY qlkhov USING 'cb3_link';


SELECT db_link, owner FROM all_db_links;


COMMIT;
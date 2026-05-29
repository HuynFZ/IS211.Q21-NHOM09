from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import oracledb
import pyorientdb

ORIENT_HOST = '26.241.212.73'; ORIENT_PORT = 2424; ORIENT_DB = 'BTL2'; ORIENT_USER = 'root'; ORIENT_PASS = 'admin'
ORACLE_USER = 'CN1'; ORACLE_PASS = 'Admin123'; ORACLE_DSN = '26.175.219.39:1521/orcl'

def extract_part1():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    
    pd.read_sql("SELECT * FROM DANH_MUC", conn).to_csv('/tmp/danh_muc.csv', index=False)
    pd.read_sql("SELECT * FROM NHA_XUAT_BAN", conn).to_csv('/tmp/nha_xuat_ban.csv', index=False)
    pd.read_sql("SELECT * FROM TAC_GIA", conn).to_csv('/tmp/tac_gia.csv', index=False)
    pd.read_sql("SELECT * FROM SACH_VPP", conn).to_csv('/tmp/sach_vpp.csv', index=False)
    pd.read_sql("SELECT * FROM CHI_NHANH", conn).to_csv('/tmp/chi_nhanh.csv', index=False)
    
    df_kh_cn1 = pd.read_sql("SELECT t.*, 'cn1' as NGUON FROM KHACH_HANG t", conn)
    df_kh_cn2 = pd.read_sql("SELECT t.*, 'cn2' as NGUON FROM CN2.KHACH_HANG@GiamDoc12Link t", conn)
    pd.concat([df_kh_cn1, df_kh_cn2, df_kh_cn3], ignore_index=True).to_csv('/tmp/khach_hang.csv', index=False)
    
    conn.close()

def load_vertices_part1():
    client = pyorientdb.OrientDB(ORIENT_HOST, ORIENT_PORT)
    client.set_session_token(True)
    client.db_open(ORIENT_DB, ORIENT_USER, ORIENT_PASS)
    
    # --- LOAD BẢNG DÙNG CHUNG ---
    for table in ['danh_muc', 'nha_xuat_ban', 'tac_gia', 'sach_vpp', 'chi_nhanh']:
        df = pd.read_csv(f'/tmp/{table}.csv').fillna('')
        df.columns = df.columns.str.upper()
        total = len(df)
        print(f"Bắt đầu nạp {total} dòng cho {table.upper()}...")
        for idx, row in df.iterrows():
            if idx % 50 == 0: print(f"--> [{table.upper()}] Tiến độ: {idx}/{total}")
            
            row = row.apply(lambda x: str(x).replace("'", '"') if isinstance(x, str) else x)
            
            if table == 'danh_muc': client.command(f"CREATE VERTEX DANH_MUC SET MaDM='{row['MADM']}', TenDM='{row['TENDM']}', MoTa='{row['MOTA']}'")
            elif table == 'nha_xuat_ban': client.command(f"CREATE VERTEX NHA_XUAT_BAN SET MaNXB='{row['MANXB']}', TenNXB='{row['TENNXB']}', DiaChi='{row['DIACHI']}', SoDienThoai='{row['SODIENTHOAI']}'")
            elif table == 'tac_gia': client.command(f"CREATE VERTEX TAC_GIA SET MaTG='{row['MATG']}', TenTG='{row['TENTG']}', QuocTich='{row['QUOCTICH']}', TieuSu='{row['TIEUSU']}'")
            elif table == 'sach_vpp': client.command(f"CREATE VERTEX SACH_VPP SET MaSP='{row['MASP']}', TenSP='{row['TENSP']}', GiaBan={row['GIABAN'] if row['GIABAN'] else 0}, DonViTinh='{row['DONVITINH']}'")
            elif table == 'chi_nhanh': client.command(f"CREATE VERTEX CHI_NHANH SET MaCN='{row['MACN']}', TenCN='{row['TENCN']}', KhuVuc='{row['KHUVUC']}', DiaChi='{row['DIACHI']}'")

    # --- LOAD BẢNG PHÂN MẢNH (KHACH HANG) ---
    df_kh = pd.read_csv('/tmp/khach_hang.csv').fillna('')
    df_kh.columns = df_kh.columns.str.upper()
    total_kh = len(df_kh)
    print(f"Bắt đầu nạp {total_kh} dòng KHACH_HANG (Phân cụm)...")
    
    for idx, row in df_kh.iterrows():
        if idx % 100 == 0: print(f"--> [KHACH_HANG] Tiến độ: {idx}/{total_kh}")
        
        row = row.apply(lambda x: str(x).replace("'", '"') if isinstance(x, str) else x)
        cluster_name = f"khach_hang_{row['NGUON'].lower()}"
        
        cmd = f"""CREATE VERTEX KHACH_HANG CLUSTER {cluster_name} CONTENT {{
            "MaKH": "{row['MAKH']}", "TenKH": "{row['TENKH']}", "SoDienThoai": "{row['SODIENTHOAI']}", 
            "Email": "{row['EMAIL']}", "GioiTinh": "{row['GIOITINH']}", "DiemTichLuy": {row['DIEMTICHLUY'] if row['DIEMTICHLUY'] else 0},
            "DiaChi": {{"@class": "DiaChiDetail", "ChiTiet": "{row['DIACHI']}"}}
        }}"""
        client.command(cmd)

    client.db_close()

with DAG('ETL_01_Master_Data', start_date=datetime(2026, 5, 26), schedule=None) as dag1:
    PythonOperator(task_id='Extract_Part1', python_callable=extract_part1) >> PythonOperator(task_id='Load_Vertices_Part1', python_callable=load_vertices_part1)

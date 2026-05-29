from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime as dt
import pandas as pd
import oracledb
import pyorientdb
import os
import time

ORIENT_HOST = '26.241.212.73'; ORIENT_PORT = 2424; ORIENT_DB = 'BTL2'; ORIENT_USER = 'root'; ORIENT_PASS = 'admin'
ORACLE_USER = 'CN1'; ORACLE_PASS = 'Admin123'; ORACLE_DSN = '26.175.219.39:1521/orcl'
LOG_FILE = '/tmp/etl_run_history.log'

def write_log(task_name, current, total):
    """Hàm xuất log ra file riêng với mốc thời gian"""
    msg = f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] --> [{task_name}] Đã vượt mốc {current}/{total} dòng."
    print(msg) # Vẫn in ra Airflow UI
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def extract_part3():
    """Kéo FULL dữ liệu từ Oracle (Không giới hạn)"""
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    
    print("Bắt đầu kéo FULL HOA_DON...")
    if os.path.exists('/tmp/hoa_don.csv'): os.remove('/tmp/hoa_don.csv')
    queries_hd = [
        "SELECT t.*, 'cn1' as NGUON FROM HOA_DON t",
        "SELECT t.*, 'cn2' as NGUON FROM CN2.HOA_DON@GiamDoc12Link t",
    ]
    for q in queries_hd:
        for chunk in pd.read_sql(q, conn, chunksize=10000):
            chunk.to_csv('/tmp/hoa_don.csv', mode='a', header=not os.path.exists('/tmp/hoa_don.csv'), index=False)

    print("Bắt đầu kéo FULL CHI_TIET_HOA_DON...")
    if os.path.exists('/tmp/chi_tiet_hoa_don.csv'): os.remove('/tmp/chi_tiet_hoa_don.csv')
    queries_ct = [
        "SELECT t.*, 'cn1' as NGUON FROM CHI_TIET_HOA_DON t",
        "SELECT t.*, 'cn2' as NGUON FROM CN2.CHI_TIET_HOA_DON@GiamDoc12Link t",
    ]
    for q in queries_ct:
        for chunk in pd.read_sql(q, conn, chunksize=10000):
            chunk.to_csv('/tmp/chi_tiet_hoa_don.csv', mode='a', header=not os.path.exists('/tmp/chi_tiet_hoa_don.csv'), index=False)
            
    conn.close()

def load_vertices_part3():
    """Nạp Đỉnh Hóa Đơn với cơ chế Checkpoint"""
    client = pyorientdb.OrientDB(ORIENT_HOST, ORIENT_PORT)
    client.db_open(ORIENT_DB, ORIENT_USER, ORIENT_PASS)
    df = pd.read_csv('/tmp/hoa_don.csv').fillna('')
    df.columns = df.columns.str.upper()
    total_hd = len(df)
    
    ckpt_file = '/tmp/ckpt_vertices_hd.txt'
    start_idx = 0
    if os.path.exists(ckpt_file):
        with open(ckpt_file, 'r') as f: start_idx = int(f.read().strip() or 0)
    
    if start_idx > 0: write_log("HOA_DON_VERTICES", f"Khôi phục từ {start_idx}", total_hd)
        
    for idx, row in df.iterrows():
        if idx < start_idx: continue
        
        row = row.apply(lambda x: str(x).replace("'", '"') if isinstance(x, str) else x)
        cluster_name = f"hoa_don_{row['NGUON'].lower()}"
        
        try:
            client.command(f"CREATE VERTEX HOA_DON CLUSTER {cluster_name} SET MaHD = '{row['MAHD']}', TongTien = {row['TONGTIEN'] if row['TONGTIEN'] else 0}")
        except Exception:
            pass
            
        # Vẫn ghi checkpoint ngầm mỗi 5k dòng, nhưng KHÔNG in ra log
        if idx > 0 and idx % 5000 == 0:
            with open(ckpt_file, 'w') as f: f.write(str(idx))
            
        # Chỉ báo cáo log mỗi 50.000 dòng
        if idx > 0 and idx % 50000 == 0:
            write_log("HOA_DON_VERTICES", idx, total_hd)
            
    with open(ckpt_file, 'w') as f: f.write(str(total_hd))
    client.db_close()

def load_edges_part3():
    """Nạp Cạnh với Checkpoint, Chống Timeout và Ghi Log cột mốc"""
    def get_client():
        while True:
            try:
                c = pyorientdb.OrientDB(ORIENT_HOST, ORIENT_PORT)
                c.db_open(ORIENT_DB, ORIENT_USER, ORIENT_PASS)
                return c
            except Exception as e:
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] [LỖI MẠNG] Đang thử lại sau 5s... Chi tiết: {e}\n")
                time.sleep(5)

    client = get_client()
    
    # ================= 1. CẠNH CHUNG =================
    df_hd = pd.read_csv('/tmp/hoa_don.csv').fillna('')
    df_hd.columns = df_hd.columns.str.upper()
    total_hd = len(df_hd)
    
    ckpt_edge_hd = '/tmp/ckpt_edges_hd.txt'
    start_idx_hd = 0
    if os.path.exists(ckpt_edge_hd):
        with open(ckpt_edge_hd, 'r') as f: start_idx_hd = int(f.read().strip() or 0)
        
    write_log("EDGES_HOA_DON", f"Bắt đầu chạy từ {start_idx_hd}", total_hd)
    
    for idx, row in df_hd.iterrows():
        if idx < start_idx_hd: continue
            
        # Mỗi 5k dòng: Làm mới vé thông hành + Ghi checkpoint (Chạy ngầm)
        if idx > 0 and idx % 5000 == 0:
            try: client.db_close()
            except: pass
            client = get_client()
            with open(ckpt_edge_hd, 'w') as f: f.write(str(idx))

        # Mỗi 50k dòng: Xuất log báo cáo
        if idx > 0 and idx % 50000 == 0:
            write_log("EDGES_HOA_DON", idx, total_hd)

        row = row.apply(lambda x: str(x).replace("'", '"') if isinstance(x, str) else x)
        ma_hd = row['MAHD']
        ma_kh = str(row['MAKH']).strip()
        ma_nv = str(row['MANV']).strip()
        ma_cn = str(row['MACN']).strip()
        
        try:
            if ma_kh: client.command(f"CREATE EDGE CUA_KHACH_HANG FROM (SELECT FROM HOA_DON WHERE MaHD = '{ma_hd}') TO (SELECT FROM KHACH_HANG WHERE MaKH = '{ma_kh}')")
            if ma_nv: client.command(f"CREATE EDGE LAP_BOI_NV FROM (SELECT FROM HOA_DON WHERE MaHD = '{ma_hd}') TO (SELECT FROM NHAN_VIEN WHERE MaNV = '{ma_nv}')")
            if ma_cn: client.command(f"CREATE EDGE TAI_CHI_NHANH FROM (SELECT FROM HOA_DON WHERE MaHD = '{ma_hd}') TO (SELECT FROM CHI_NHANH WHERE MaCN = '{ma_cn}')")
        except Exception:
            pass

    with open(ckpt_edge_hd, 'w') as f: f.write(str(total_hd))

    # ================= 2. CẠNH CHI TIẾT HÓA ĐƠN =================
    df_cthd = pd.read_csv('/tmp/chi_tiet_hoa_don.csv').fillna(0)
    df_cthd.columns = df_cthd.columns.str.upper()
    total_cthd = len(df_cthd)
    
    ckpt_edge_ct = '/tmp/ckpt_edges_ct.txt'
    start_idx_ct = 0
    if os.path.exists(ckpt_edge_ct):
        with open(ckpt_edge_ct, 'r') as f: start_idx_ct = int(f.read().strip() or 0)
        
    write_log("CHI_TIET_HOA_DON", f"Bắt đầu chạy từ {start_idx_ct}", total_cthd)
    
    for idx, row in df_cthd.iterrows():
        if idx < start_idx_ct: continue

        # Mỗi 5k dòng: Làm mới vé thông hành + Ghi checkpoint (Chạy ngầm)
        if idx > 0 and idx % 5000 == 0:
            try: client.db_close()
            except: pass
            client = get_client()
            with open(ckpt_edge_ct, 'w') as f: f.write(str(idx))

        # Mỗi 50k dòng: Xuất log báo cáo
        if idx > 0 and idx % 50000 == 0:
            write_log("CHI_TIET_HOA_DON", idx, total_cthd)

        row = row.apply(lambda x: str(x).replace("'", '"') if isinstance(x, str) else x)
        cluster_name = f"bao_gom_{row['NGUON'].lower()}"
        ma_hd = str(row['MAHD']).strip()
        ma_sp = str(row['MASP']).strip()
        
        cmd = f"""
            CREATE EDGE BAO_GOM CLUSTER {cluster_name} 
            FROM (SELECT FROM HOA_DON WHERE MaHD = '{ma_hd}') 
            TO (SELECT FROM SACH_VPP WHERE MaSP = '{ma_sp}') 
            SET SoLuong = {row['SOLUONG']}, DonGia = {row['DONGIA']}, ThanhTien = {row['THANHTIEN']}
        """
        try:
            client.command(cmd)
        except Exception:
            pass
            
    with open(ckpt_edge_ct, 'w') as f: f.write(str(total_cthd))
    client.db_close()

with DAG('ETL_03_Transactions', start_date=dt(2026, 5, 26), schedule=None) as dag3:
    PythonOperator(task_id='Extract_Part3', python_callable=extract_part3) >> PythonOperator(task_id='Load_Vertices_Part3', python_callable=load_vertices_part3) >> PythonOperator(task_id='Load_Edges_Part3', python_callable=load_edges_part3)

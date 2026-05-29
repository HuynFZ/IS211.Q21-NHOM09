from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import oracledb
import pyorientdb

# Đang để localhost để Khang test đêm nay. Lúc chạy thật nhớ đổi lại 26.175.219.39 nhé.
ORIENT_HOST = '26.241.212.73'; ORIENT_PORT = 2424; ORIENT_DB = 'BTL2'; ORIENT_USER = 'root'; ORIENT_PASS = 'admin'
ORACLE_USER = 'CN1'; ORACLE_PASS = 'Admin123'; ORACLE_DSN = '26.175.219.39:1521/orcl'

def extract_part2():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    
    # Nhân viên (Thêm bí danh 't' và Schema Oracle)
    df_nv_cn1 = pd.read_sql("SELECT t.*, 'cn1' as NGUON FROM NHAN_VIEN t", conn)
    df_nv_cn2 = pd.read_sql("SELECT t.*, 'cn2' as NGUON FROM CN2.NHAN_VIEN@GiamDoc12Link t", conn)
    pd.concat([df_nv_cn1, df_nv_cn2, df_nv_cn3], ignore_index=True).to_csv('/tmp/nhan_vien.csv', index=False)
    
    # Kho hàng (Thêm bí danh 't' và Schema Oracle)
    df_kho_cn1 = pd.read_sql("SELECT t.*, 'cn1' as NGUON FROM KHO_HANG t", conn)
    df_kho_cn2 = pd.read_sql("SELECT t.*, 'cn2' as NGUON FROM CN2.KHO_HANG@GiamDoc12Link t", conn)
    pd.concat([df_kho_cn1, df_kho_cn2, df_kho_cn3], ignore_index=True).to_csv('/tmp/kho_hang.csv', index=False)
    
    conn.close()

def load_vertices_part2():
    client = pyorientdb.OrientDB(ORIENT_HOST, ORIENT_PORT)
    client.set_session_token(True)
    client.db_open(ORIENT_DB, ORIENT_USER, ORIENT_PASS)
    
    df_nv = pd.read_csv('/tmp/nhan_vien.csv').fillna('')
    df_nv.columns = df_nv.columns.str.upper()
    total_nv = len(df_nv)
    
    print(f"Bắt đầu nạp {total_nv} dòng NHAN_VIEN (Phân cụm)...")
    for idx, row in df_nv.iterrows():
        if idx % 10 == 0: print(f"--> [NHAN_VIEN] Tiến độ: {idx}/{total_nv}")
        
        # Khử dấu nháy đơn
        row = row.apply(lambda x: str(x).replace("'", '"') if isinstance(x, str) else x)
        
        cluster_name = f"nhan_vien_{row['NGUON'].lower()}"
        cmd = f"""CREATE VERTEX NHAN_VIEN CLUSTER {cluster_name} SET MaNV='{row['MANV']}', TenNV='{row['TENNV']}', ChucVu='{row['CHUCVU']}'"""
        client.command(cmd)
        
    client.db_close()

def load_edges_part2():
    client = pyorientdb.OrientDB(ORIENT_HOST, ORIENT_PORT)
    client.set_session_token(True)
    client.db_open(ORIENT_DB, ORIENT_USER, ORIENT_PASS)
    
    # Cạnh Kho Hàng (CO_TRONG_KHO) - Phân cụm
    df_kho = pd.read_csv('/tmp/kho_hang.csv').fillna(0)
    df_kho.columns = df_kho.columns.str.upper()
    total_kho = len(df_kho)
    
    print(f"Bắt đầu nối {total_kho} Cạnh CO_TRONG_KHO (Phân cụm)...")
    for idx, row in df_kho.iterrows():
        if idx % 100 == 0: print(f"--> [CO_TRONG_KHO] Tiến độ: {idx}/{total_kho}")
        
        # Khử dấu nháy đơn
        row = row.apply(lambda x: str(x).replace("'", '"') if isinstance(x, str) else x)
        
        cluster_name = f"co_trong_kho_{row['NGUON'].lower()}"
        cmd = f"CREATE EDGE CO_TRONG_KHO CLUSTER {cluster_name} FROM (SELECT FROM SACH_VPP WHERE MaSP = '{row['MASP']}') TO (SELECT FROM CHI_NHANH WHERE MaCN = '{row['MACN']}') SET SoLuongTon = {row['SOLUONGTON']}"
        client.command(cmd)
        
    client.db_close()

with DAG('ETL_02_Products_Staff', start_date=datetime(2026, 5, 26), schedule=None) as dag2:
    PythonOperator(task_id='Extract_Part2', python_callable=extract_part2) >> PythonOperator(task_id='Load_Vertices_Part2', python_callable=load_vertices_part2) >> PythonOperator(task_id='Load_Edges_Part2', python_callable=load_edges_part2)

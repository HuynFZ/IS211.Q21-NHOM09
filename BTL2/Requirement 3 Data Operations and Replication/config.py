import pyorientdb

# --- CẤU HÌNH KẾT NỐI ---
HOST = '26.175.219.39' 
PORT = 2424
DB_NAME = 'BTL2'
USER = 'root'
PASS = 'admin'

def get_connection():
    print(f"[*] Đang kết nối tới OrientDB tại {HOST}:{PORT}...")
    try:
        # Sửa thành pyorientdb ở đây
        client = pyorientdb.OrientDB(HOST, PORT)
        
        # Bật session token (bắt buộc với OrientDB 3.x)
        client.set_session_token(True)
        
        client.db_open(DB_NAME, USER, PASS)
        print("[OK] Kết nối thành công!\n")
        return client
    except Exception as e:
        print(f"[!] Lỗi kết nối: {e}")
        exit()
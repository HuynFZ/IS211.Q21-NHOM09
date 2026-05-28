import pyorientdb as pyorient  # Đổi tên gọi thư viện pyorientdb thành pyorient để khớp với các file query

# Tất cả code phía dưới của Huy giữ nguyên hoàn toàn:
HOST = '26.175.219.39' 
PORT = 2424  
USER = 'root'
PASS = 'admin' 
DB_NAME = 'BTL2'

def get_client():
    try:
        client = pyorient.OrientDB(HOST, PORT)
        client.connect(USER, PASS)
        print(f"Kết nối thành công đến Server {HOST}")
        client.db_open(DB_NAME, USER, PASS)
        return client
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return None
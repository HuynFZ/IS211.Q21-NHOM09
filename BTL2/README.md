# Bài tập lớn 2 CSDL Phân tán - Nhóm 9
Chủ đề: Triển khai Hệ quản trị NoSQL OrientDB phân tán trên Windows và thực thi truy vấn bằng Python.

## Giới thiệu
Dự án tập trung vào việc cài đặt Native OrientDB trên Windows, cấu hình cụm (Cluster) phân tán Multi-Master thông qua mạng LAN ảo Radmin VPN. Hệ thống hỗ trợ đồng bộ dữ liệu thời gian thực và thực thi các thao tác CRUD (Create, Read, Update, Delete) thông qua ngôn ngữ lập trình Python.

## 👨‍💻 Giảng viên hướng dẫn
- Thầy: Nguyễn Minh Nhựt 

## 👨‍💻 Thành viên thực hiện
- Nguyễn Văn Mạnh Huy - 23520641 
- Nguyễn Lê Bảo Ngọc - 23521030
- Lê Vĩnh Thái - 23521417
- Nguyễn Thành Khang - 23520698

## 🛠 Yêu cầu hệ thống
* **Hệ điều hành**: Windows (Cài đặt Native).
* **Java**: JDK 8 hoặc mới hơn.
* **Radmin VPN**: Các thành viên tham gia cùng một Network để có IP đầu 26.x.x.x.
* **Python**: Phiên bản 3.x kèm thư viện pyorient.

## 🚀 Hướng dẫn cài đặt Native (Ổ D)

### Bước 1: Cài đặt biến môi trường
* Download OrientDB cho Windows: https://orientdb.dev/downloads/ và giải nén OrientDB và di chuyển vào ổ D.
* Download Java Development Kit (JDK): https://www.oracle.com/java/technologies/downloads/.
* Vào Environment Variables trong Window, tạo biến môi trường PATH chứa đường dẫn đến file bin của JDK. 

### Bước 2: Khởi chạy server
* Sử dụng CMD tại thư mục bin của OrientDB giải nén ở trên hoặc dùng lệnh di chuyển đến 
```bash
cd %ORIENTDB_HOME%\bin 
```
* Sau đó sử dụng lệnh để khởi động
```bash
server.bat 
```

* Lưu ý: Lần đầu khởi chạy cần thiết lập mật khẩu cho user root (Ví dụ: admin).

Link truy cập sau khi đã khởi động: http://localhost:2480/studio/index.html#/ (Thay localhost thành ip radmin máy bản thân)

## Khởi động OrientDB để làm việc trên Command Line 
* Mở OrientDB trên CMD bằng cách chạy file console.bat trong thư mục bin (đảm bảo file server.bat đã được khởi động và đang chạy) 
* Gõ lệnh help để xem các cú pháp thao tác với OrientDB.

## Chuẩn bị môi trường Python
```bash
pip install pyorient
```

## Cài đặt nhân bản
* Truy cập thư mục D:\OrientDB\orientdb-community-3.2.51\config 
- Sao chép nội dung file default-distributed-db-config.json từ Git sang tương ứng.
- File hazelcast.xml: chỉnh tương tự file hazelcast.xml trên Git.

- Truy cập file: orientdb-server-config.xml: Sửa trường value trong parameter của OHazelcastPlugin thành true, và sửa dòng "entry value = “server1” name = “server.name”. (value chỉnh tương ứng như sau: Thái: server2, Khang: server3, Ngọc: server4)

- Tại file orientdb-server-config.xml: Tìm đến các thẻ listener (thường có 2 thẻ cho port 2424 và 2480). Thay đổi ip-address="0.0.0.0" thành IP Radmin của bạn: (ví dụ: ip-address="26.175.219.39")




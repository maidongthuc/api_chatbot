import pymysql
db_config = {
    "host": "156.67.222.52",       # Địa chỉ máy chủ MySQL
    "user": "u238186000_chechanh",   # Tên người dùng MySQL
    "passwd": "0576289825Asd", # Mật khẩu của người dùng
    "db": "u238186000_chatbot",     # Tên cơ sở dữ liệu
    "port": 3306                    # Thêm cổng kết nối MySQL (mặc định là 3306)
}

# Tạo hàm kết nối đến MySQL
def connect_to_database():
    try:
        connection = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["passwd"],
            database=db_config["db"],
            port=db_config["port"]
        )
        print("Database connection successful.")  # Thông báo khi kết nối thành công
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")  # Thông báo lỗi nếu kết nối thất bại
        return None
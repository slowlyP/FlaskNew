import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="song",
        password="1234",
        database="lms_team_project",
        port=3306,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor



    )
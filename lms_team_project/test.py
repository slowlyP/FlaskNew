import pymysql

def get_connection():
    return pymysql.connect(
        host="192.168.0.160",   # 상황에 맞게 변경
        user="song",
        password="1234",
        database="lms_team_project",
        port=3306,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


try:
    conn = get_connection()
    print("✅ DB 연결 성공")

    conn.close()

except Exception as e:
    print("❌ DB 연결 실패")
    print(e)


    import pymysql

def get_connection():
    return pymysql.connect(
        host="192.168.0.160",
        user="song",
        password="1234",
        database="lms_team_project",
        cursorclass=pymysql.cursors.DictCursor
    )


try:
    conn = get_connection()

    with conn.cursor() as cursor:
        sql = "SELECT COUNT(*) as cnt FROM members"
        cursor.execute(sql)
        result = cursor.fetchone()

        print("회원 수:", result["cnt"])

    conn.close()
    print("✅ SELECT 테스트 성공")

except Exception as e:
    print("❌ DB 오류")
    print(e)


@app.route("/db-test")
def db_test():
    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        conn.close()

        return "DB 연결 성공"

    except Exception as e:
        return f"DB 연결 실패: {e}"
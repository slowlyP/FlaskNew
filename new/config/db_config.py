# ===============================
# MySQL 연결 모듈 불러오기
# ===============================

import pymysql

# ===============================
# DB 연결 함수
# ===============================
def get_connection():
    """
    MySQL 데이터베이스 연결 함수
    
    service / domain 에서 
    DB 작업할 때 호출해서 사용함
    """

    return pymysql.connect(

        # DB 서버 주소
        host="localhost",

        # MySQL 계정명
        user="root",

        # MySQL 비밀번호
        password="1234",

        # 사용할 데이터베이스
        database="LMS",

        # 결과를 dict 형태로 받기
        # (컬럼명으로 접근 가능)
        cursorclass=pymysql.cursors.DictCursor
    )
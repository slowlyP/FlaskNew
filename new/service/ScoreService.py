from common import Session
from domain import Score

class ScoreService:


    @classmethod
    def load(cls):
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as cnt FROM scores")
                count = cursor.fetchone()['cnt']
                print(f"시스템 : 현재 등록된 성적 수는 {count}개입니다.")

        finally:
            conn.close()

    @classmethod
    def run(cls):
        cls.load()
        if not Session.is_login():
            print("로그인 후 이용 가능합니다.")
            return

        member = Session.login_member

        while True:
            print("\n=====성적 관리 시스템 =====")
            if member.role in ("manager","admin"):
                print("1. 학생 성적 입력/수정")

            print("2. 내 성적 조회")

            if member.role == "admin":
                print("3. 전체 성적 현황 (JOIN)")

            print("0. 뒤로가기")

            sel = input(">>>")

            if sel == "1" and member.role in ("manager","admin"):
                cls.add_score()
            elif sel == "2":
                cls.view_my_score()
            elif sel == "3":
                cls.view_all()
            elif sel == "0":
                break

    @classmethod
    def add_score(cls):
        target_uid = input("성적 입력할 학생 아이디(uid): ")
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name FROM members WHERE uid = %s", (target_uid,))
                student = cursor.fetchone()

                if not student:
                    print(f"'{target_uid}'학생을 찾을 수 없습니다.")
                    return

                kor = int(input("국어 : "))
                eng = int(input("영어 : "))
                math = int(input("수학 : "))

                temp_score = Score(member_id = student['id'], kor = kor, eng=eng, math=math)

                cursor.execute("SELECT id FROM scores WHERE member_id = %s", (student['id'],))

                if cursor.fetchone():
                    sql = "UPDATE scores SET korean=%s, english=%s, math=%s, total=%s, average=%s, grade=%s WHERE member_id=%s"

                    cursor.execute(sql, (
                        temp_score.kor, temp_score.eng, temp_score.math,
                        temp_score.total, temp_score.avg, temp_score.grade,
                        student['id']
                    ))

                else:
                    sql = """
                            INSERT INTO scores (member_id, korean, english, math, total, average, grade)
                            VALUES (%s, %s, %s, %s, %s, %s, %s) \
                            """
                    cursor.execute(sql, (
                        student['id'], temp_score.kor, temp_score.eng, temp_score.math,
                        temp_score.total, temp_score.avg, temp_score.grade,
                    ))

                conn.commit()
                print(f"{student['name']} 학생의 성적 저장 완료 (객체 계산 방식")
        finally:
            conn.close()


    @classmethod
    def view_my_score(cls):
        member = Session.login_member
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM scores WHERE member_id = %s"
                cursor.execute(sql, (member.id,))
                row = cursor.fetchone()

                if row:
                    s = Score.from_db(row)
                    cls.print_score(s, member.uid)
                else:
                    print("등록된 성적이 없습니다.")

        finally:
            conn.close()

    @classmethod
    def view_all(cls):
        print("\n[전체 성적 목록 - JOIN 결과]")
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT m.uid,s.* FROM scores s JOIN members m ON s.member_id = m.id"

                cursor.execute(sql)
                rows = cursor.fetchall()

                for row in rows:
                    s = Score.from_db(row)
                    cls.print_score(s, row['uid'])
        finally:
            conn.close()

    @staticmethod
    def print_score(s, display_uid):
        print(
            f"ID:{display_uid:<10} | "
            f"국어:{s.kor:>3} 영어:{s.eng:>3} 수학:{s.math:>3} |"
            f"총점:{s.total:>3} 평균:{s.avg:>5.2f} | 등급 : {s.grade}"
        )
from common import Session
from domain import Member


# ==========================================
# DB 연결 함수 import
# ==========================================

# config/db_config.py 에서 만든
# MySQL 연결 함수 가져오기

from config.db_config import get_connection


# ==========================================
# 회원 서비스 클래스
# ==========================================
# 로그인 / 회원가입 / 회원조회 등
# 회원 관련 비즈니스 로직 담당

class MemberService:

    # ======================================
    # 로그인 처리 함수
    # ======================================

    @staticmethod
    def login(uid, pw):
        
        # ----------------------------------
        # 1️⃣ DB 연결 생성
        # ----------------------------------
        # config/db_config.py 에서 만든
        # get_connection() 호출

        conn = get_connection()

        try:
            # ----------------------------------
            # 2️⃣ 커서(cursor) 생성
            # ----------------------------------
            # SQL 실행을 위한 객체

            with conn.cursor() as cursor:

                # ----------------------------------
                # 3️⃣ 로그인 조회 SQL 작성
                # ----------------------------------
                # uid + password 일치
                # active=1 → 활성계정만 로그인 허용

                sql = """
                    SELECT *
                    FROM members
                    WHERE uid=%s
                    AND password=%s
                    AND active=1
                """
                
                # ----------------------------------
                # 4️⃣ SQL 실행
                # ----------------------------------
                # %s 자리에 uid / pw 값 바인딩

                cursor.execute(sql, (uid, pw))

                return cursor.fetchone()

        finally:
            conn.close()




















    @classmethod
    def logout(cls):
        if not Session.is_login():
            print("현재 로그인 상태가 아닙니다.")
            return
        Session.logout()
        print("로그아웃 되었습니다.")


    @classmethod
    def signup(cls):
        print("\n[회원가입]")
        if Session.is_login():
            print("로그인 상태에서 진행할수없습니다.")
            return

        uid = input("아이디 : ").strip()

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                check_sql = "SELECT id FROM members WHERE uid = %s"
                cursor.execute(check_sql,(uid,))
                if cursor.fetchone():
                    print("이미 존재하는 아이디 입니다.")
                    return

                pw = input("비밀번호 : ").strip()
                name = input("이름 : ").strip()

                insert_sql = "INSERT INTO members (uid, password, name) VALUES (%s, %s, %s)"
                cursor.execute(insert_sql,(uid, pw, name))
                conn.commit()
                print("회원가입 완료! 로그인해 주세요.")

        except Exception as e:
            conn.rollback()
            print(f"회원가입 오류:{e}")
        finally:
            conn.close()

    @classmethod
    def modify(cls):
        if not Session.is_login():
            print("로그인 후 이용 가능합니다.")
            return

        member = Session.login_member
        print(f"내 정보 확인 : {member}")
        print("\n[내 정보 수정]\n1. 이름 변경 2. 비밀번호 변경 3. 계정 비활성 및 탈퇴 0. 취소")
        sel = input("선택 : ")

        new_name = member.name
        new_pw = member.pw

        if sel == "1":
            new_name = input("새 이름 : ").strip()
        elif sel == "2":
            new_pw = input("새 비밀번호 : ").strip()
        elif sel == "3":
            cls.delete()

        else:
            return

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE members SET name = %s, password = %s WHERE id = %s"
                cursor.execute(sql, (new_name,new_pw, member.id))
                conn.commit()

                member.name = new_name
                member.pw = new_pw
                print("정보 수정 완료")

        finally:
            conn.close()

    @classmethod
    def delete(cls):
        if not Session.is_login():
            print("로그인 후 이용 가능합니다.")
            return
        member = Session.login_member

        print("\n[회원 탈퇴]\n1. 완전 탈퇴 2. 계정 비활성화")
        sel = input("선택 : ")

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                if sel == "1":
                    sql = "DELETE FROM members WHERE id = %s"
                    cursor.execute(sql, (member.id,))
                    print("회원 탈퇴 완료")
                    Session.logout()
                elif sel == "2":
                    sql = "UPDATE members SET active = FALSE WHERE id=%s"
                    cursor.execute(sql, (member.id,))
                    print("계정 비활성화 완료")
                    Session.logout()


                else:
                    print("잘못된 선택입니다.")
                    return

                conn.commit()

        finally:
            conn.close()

    @classmethod
    def admin_menu(cls):
        if not Session.is_login() or not Session.is_admin():
            print("\n[경고] 관리자 권한이 필요합니다.")
            return

        while True:
            print(f"""
[ 관리자 시스템 - 접속자 : {Session.is_admin()} ]
1. 전체 회원목록 조회
2. 회원 권한 변경
3. 계정 차단/복구
0. 메인메뉴
""")
            sel = input("메뉴 선택 : ").strip()

            if sel == "1":
                cls.list_member()
            elif sel == "2":
                cls.change_role()
            elif sel == "3":
                cls.toggle_active()
            elif sel == "0":
                break
            else:
                print("잘못된 접근입니다.")

    @classmethod
    def list_member(cls):
        print("\n" + "=" * 50)
        print(f"{'ID':<5} | {'UID':<12} | {'NAME':<10} | {'ROLE':<8} | {'STATUS'}")
        print("=" * 50)

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM members ORDER BY id ASC")
                rows = cursor.fetchall()
                for row in rows:
                    m = Member.from_db(row)
                    status = "활동" if m.active else "차단"
                    print(f"{m.id:<5} | {m.uid:<12} | {m.name:<10} | {m.role:<8} | {status}")

        finally:
            conn.close()

        print("=" * 50)

    @classmethod
    def change_role(cls):
        target_uid = input("권한을 변경할 회원의 아이디(uid): ").strip()
        new_role = input("부여할 권한 (admin, manager, user):").strip().lower()

        if new_role not in ['admin', 'manager', 'user']:
            print("존재하지 않는 권한 타입입니다.")
            return

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE members SET role = %s WHERE uid = %s"
                result = cursor.execute(sql, (new_role, target_uid))
                conn.commit()

                if result > 0:
                    print(f"[{target_uid}]님의 권한이 {new_role} 으로 변경 되었습니다.")

                else:
                    print("해당 아이디를 찾을 수 없습니다.")
        finally:
            conn.close()

    @classmethod
    def toggle_active(cls):
        target_uid = input("상태 변경할 회원의 아이디(uid): ").strip()

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT active FROM members WHERE uid = %s",(target_uid,))
                row = cursor.fetchone()

                if not row:
                    print("해당 회원이 존재하지 않습니다.")
                    return

                new_status = not bool(row['active'])
                cursor.execute("UPDATE members SET active = %s WHERE uid = %s",(new_status, target_uid))
                conn.commit()
        finally:
            conn.close()






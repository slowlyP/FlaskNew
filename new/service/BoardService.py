import re
from common import Session
from domain import Board

class BoardService:
    @classmethod
    def run(cls):
        if not Session.is_login():
            print("로그인 후 이용 가능합니다.")
            return

        while True:
            print(f"\n===== MBC 게시판 ({Session.login_member.name}) =====")
            cls.list_board()
            print("1. 게시글 작성")
            print("2. 글 상세 보기(수정/삭제)")
            print("0. 뒤로가기")

            sel = input(">>>")
            if sel == "1":
                cls.write_board()
            elif sel == "2":
                cls.view_detail()
            
            elif sel == "0":
                break

    @classmethod
    def write_board(cls):
        print("\n[게시글 작성]")
        title = input("제목 : ").strip()
        content = input("내용 : ").strip()

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO boards (member_id, title, content) VALUES (%s, %s, %s)"
                cursor.execute(sql, (Session.login_member.id, title, content))
                conn.commit()
                print("게시글 작성 완료!")
        finally:
            conn.close()

    @classmethod
    def list_board(cls):
        print("\n" + "=" * 60)
        print(f"{'번호':<5} | {'제목':<25} | {'작성자':<10} | {'작성일'}")
        print("=" * 60)

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT b.*, m.name
                FROM boards b
                JOIN members m ON b.member_id = m.id
                ORDER BY b.id DESC 
                """
                cursor.execute(sql)
                rows = cursor.fetchall()
            for row in rows:
                date_str = row['created_at'].strftime('%Y-%m-%d')
                print(f"{row['id']:<5} | {row['title']:<25} | {row['name']:<10} | {date_str}")

        finally:
            conn.close()
        print("=" * 60)

    @classmethod
    def view_detail(cls):
        keyword = input("조회할 글 번호 또는 제목: ").strip()
        conn = Session.get_connection()

        try:
            with conn.cursor() as cursor:

                if keyword.isdigit():
                    cursor.execute("""
                    SELECT b.*, m.name
                    FROM boards b
                    JOIN members m ON b.member_id = m.id
                    WHERE b.id = %s
                    """, (int(keyword),))

                    board = cursor.fetchone()

                    if not board:
                        print("조회된 글이 없습니다.")
                        return
                
                else:
                    cursor.execute("""
                    SELECT b.id, b.title, m.name
                    FROM boards b
                    JOIN members m ON b.member_id = m.id
                    WHERE b.title LIKE %s
                    ORDER BY b.id DESC
                    """, (f"%{keyword}%",))
                    rows = cursor.fetchall()
                    print("DEBUG rows len:", len(rows))

                    if not rows:
                        print("조회된 글이 없습니다.")
                        return

                if len(rows) > 1:
                    print("\n[검색 결과]")
                    print("-" * 40)
                    for row in rows:
                        print(f"{row['id']} | {row['title']} | {row['name']}")
                    print("-" * 40)
                
                    sel_id = input("조회할 글 번호: ").strip()
                    if not sel_id.isdigit():
                        print("잘못된 입력입니다.")
                        return

                    cursor.execute("""
                        SELECT b.*, m.name
                        FROM boards b
                        JOIN members m ON b.member_id = m.id
                        WHERE b.id = %s
                    """, (int(sel_id),))

                    board = cursor.fetchone()

                    if not board:
                        print("조회된 글이 없습니다.")
                        return
                    
                else:
                    sel_id = rows[0]['id']
                    cursor.execute("""
                        SELECT b.*, m.name
                        FROM boards b
                        JOIN members m ON b.member_id = m.id
                        WHERE b.id = %s
                    """, (sel_id,))
                    board = cursor.fetchone()

            print("\n[게시글 상세]")
            print(f"번호: {board['id']}")
            print(f"제목: {board['title']}")
            print(f"작성자: {board['name']}")
            print(f"작성일: {board['created_at'].strftime('%Y-%m-%d')}")
            print("-" * 40)
            print(board['content'])

            board_id = board['id']

            if board['member_id'] ==Session.login_member.id:
                print("\n1. 수정 2. 삭제  0. 뒤로가기")
                sub_sel = input("선택 : ")

                if sub_sel == "1":
                    cls.update_board(board_id)
                elif sub_sel == "2":
                    cls.delete_board(board_id)
            else:
                input("\n0. 뒤로가기 (Enter)")
        finally:
            conn.close()












    @classmethod
    def update_board(cls, board_id):
        new_title = input("수정할 제목 : ").strip()
        new_content = input("수정할 내용 : ").strip()
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE boards SET title=%s, content=%s WHERE id=%s"
                cursor.execute(sql, (new_title, new_content, board_id))
                conn.commit()
                print("게시글 수정 완료!")

        finally:
            conn.close()

    @classmethod
    def delete_board(cls, board_id):
        confirm = input("정말 삭제하시겠습니까? (y/n): ")
        if confirm.lower() != 'y':return

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM boards WHERE id=%s"
                cursor.execute(sql, (board_id,))
                conn.commit()
                print("게시글 삭제 완료!")
        finally:
            conn.close()

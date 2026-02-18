# =========================
# Flask 기본 모듈 import
# =========================
from flask import Blueprint, render_template, request, redirect, session

# DB 연결 함수 import
from db.db_conn import get_connection


# =========================
# Blueprint 생성
# =========================
# board 관련 URL을 /boards 로 시작하게 만드는 구조
board_bp = Blueprint(
    "board",           # Blueprint 이름
    __name__,
    url_prefix="/boards"   # URL prefix
)



# ============================================================
# 📌 1. 게시글 목록 + 페이징
# URL : /boards/
# 역할 : 게시글 리스트 출력 + 페이지 나누기
# ============================================================
@board_bp.route("/")
def board_list():

    # -----------------------------------------
    # 현재 페이지 번호 받기
    # 주소창 ?page=2 이런식
    # 없으면 기본값 1
    # -----------------------------------------
    page = request.args.get("page", 1, type=int)

    # 한 페이지에 보여줄 글 개수
    per_page = 10

    # LIMIT OFFSET 계산
    # ex) 2페이지면 10개 건너뜀
    offset = (page - 1) * per_page

    # DB 연결
    conn = get_connection()

    with conn.cursor() as cursor:

        # -----------------------------------------
        # 전체 게시글 개수 조회
        # 페이징 계산용
        # -----------------------------------------
        sql = """
        SELECT COUNT(*) AS cnt
        FROM boards
        WHERE active=1
        """
        cursor.execute(sql)
        total = cursor.fetchone()["cnt"]


        # -----------------------------------------
        # 게시글 목록 조회
        # 최신글이 위로 → id DESC
        # LIMIT : 개수
        # OFFSET : 시작위치
        # -----------------------------------------
        sql = """
        SELECT *
        FROM boards
        WHERE active=1
        ORDER BY id DESC
        LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (per_page, offset))
        boards = cursor.fetchall()

    conn.close()


    # -----------------------------------------
    # 총 페이지 수 계산
    # ex) 53개 / 10개 = 6페이지
    # -----------------------------------------
    total_pages = (total + per_page - 1) // per_page


    # HTML로 데이터 전달
    return render_template(
        "board/board_list.html",
        boards=boards,
        page=page,
        total_pages=total_pages
    )



# ============================================================
# 📌 2. 글쓰기 (GET + POST 통합)
# URL : /boards/write
# 역할 :
#   GET  → 글쓰기 화면
#   POST → 글 저장
# ============================================================
@board_bp.route("/write", methods=["GET","POST"])
def board_write():

    # ------------------------------------------------
    # POST 요청이면 → 글 저장 처리
    # ------------------------------------------------
    if request.method == "POST":

        # 로그인 안했으면 로그인 페이지 이동
        if "user_id" not in session:
            return redirect("/login")

        member_id = session["user_id"]

        # 폼 데이터 받기
        title = request.form["title"]
        content = request.form["content"]


        # DB 연결
        conn = get_connection()

        with conn.cursor() as cursor:

            # 게시글 INSERT
            sql = """
            INSERT INTO boards(member_id,title,content)
            VALUES(%s,%s,%s)
            """
            cursor.execute(sql,
                           (member_id,
                            title,
                            content))

        conn.commit()
        conn.close()

        # 저장 후 목록 이동
        return redirect("/boards/")


    # ------------------------------------------------
    # GET 요청이면 → 글쓰기 화면 출력
    # ------------------------------------------------
    return render_template("board/board_write.html")



# ============================================================
# 📌 3. 상세보기 + 댓글등록 통합
# URL : /boards/detail/<id>
# 역할 :
#   GET  → 게시글 + 댓글 조회
#   POST → 댓글 저장
# ============================================================
@board_bp.route("/detail/<int:board_id>", methods=["GET","POST"])
def board_detail(board_id):

    conn = get_connection()

    with conn.cursor() as cursor:

        # ---------------------------
        # 댓글 등록 (POST)
        # ---------------------------
        if request.method == "POST":

            if "user_id" not in session:
                return redirect("/login")

            content = request.form["content"]
            member_id = session["user_id"]

            sql = """
            INSERT INTO board_comments
            (board_id, member_id, content, parent_id, depth)
            VALUES (%s,%s,%s,0,0)
            """
            cursor.execute(sql,(board_id,member_id,content))
            conn.commit()


        # ---------------------------
        # 게시글 조회
        # ---------------------------
        sql = """
        SELECT *
        FROM boards
        WHERE id=%s
        """
        cursor.execute(sql,(board_id,))
        board = cursor.fetchone()


        # ---------------------------
        # 내가 누른 좋아요 조회
        # ---------------------------
        if "user_id" in session:

            sql = """
            SELECT comment_id
            FROM comment_likes
            WHERE member_id=%s
            """
            cursor.execute(sql,(session["user_id"],))
            my_likes = cursor.fetchall()

            my_like_ids = [c["comment_id"] for c in my_likes]

        else:
            my_like_ids = []


        # ---------------------------
        # 댓글 조회 + 좋아요 개수
        # ---------------------------
        sql = """
        SELECT c.*,
        COUNT(l.id) AS like_count
        FROM board_comments c
        LEFT JOIN comment_likes l
        ON c.id = l.comment_id
        WHERE c.board_id=%s
        AND c.active=1
        GROUP BY c.id
        ORDER BY c.id ASC
        """
        cursor.execute(sql,(board_id,))
        comments = cursor.fetchall()


    conn.close()


    return render_template(
        "board/board_detail.html",
        board=board,
        comments=comments,
        my_like_ids=my_like_ids
    )




# ============================================================
# 📌 4. 수정 화면
# ============================================================
@board_bp.route("/edit/<int:board_id>")
def board_edit(board_id):

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = "SELECT * FROM boards WHERE id=%s"
        cursor.execute(sql,(board_id,))
        board = cursor.fetchone()

    conn.close()

    return render_template(
        "board/board_edit.html",
        board=board
    )



# ============================================================
# 📌 5. 수정 처리
# ============================================================
@board_bp.route("/update/<int:board_id>", methods=["POST"])
def board_update(board_id):

    title = request.form["title"]
    content = request.form["content"]

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = """
        UPDATE boards
        SET title=%s, content=%s
        WHERE id=%s
        """
        cursor.execute(sql,
                       (title,
                        content,
                        board_id))

    conn.commit()
    conn.close()

    return redirect(f"/boards/detail/{board_id}")



# ============================================================
# 📌 6. 삭제 (소프트 삭제)
# active=0 처리
# ============================================================
@board_bp.route("/delete/<int:board_id>")
def board_delete(board_id):

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = """
        UPDATE boards
        SET active=0
        WHERE id=%s
        """
        cursor.execute(sql,(board_id,))

    conn.commit()
    conn.close()

    return redirect("/boards/")


# 댓글 삭제 (소프트삭제)
#url : /boadrs/comment_delete/<id>

@board_bp.route("/comment_delete/<int:comment_id>")
def comment_delete(comment_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    with conn.cursor() as cursor:

        # 댓글 정보 조회
        sql = """
        SELECT board_id, member_id
        FROM board_comments
        WHERE id=%s
        """
        cursor.execute(sql, (comment_id,))
        result = cursor.fetchone()

        board_id = result["board_id"]
        writer_id = result["member_id"]

        if session["user_id"] != writer_id:
            return redirect(f"/boards/detail/{board_id}")

        # 삭제
        sql = """
        UPDATE board_comments
        SET active=0
        WHERE id=%s
        """
        cursor.execute(sql, (comment_id,))

    conn.commit()
    conn.close()

    return redirect(f"/boards/detail/{board_id}")

# 댓글 수정 라우트
@board_bp.route("/comment_edit/<int:comment_id>", methods=["GET","POST"])
def comment_edit(comment_id):
    #로그인체크
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()

    with conn.cursor() as cursor:

        #post 수정 저장

        if request.method == "POST":
            content = request.form["content"]

            sql = """
            UPDATE board_comments
            SET content=%s
            WHERE id=%s
            """
            cursor.execute(sql,
                           (content,
                            comment_id))

            conn.commit()

            return redirect(request.referrer)


        # ----------------------------------------
        # GET → 수정 화면 출력
        # ----------------------------------------
        sql = """
        SELECT *
        FROM board_comments
        WHERE id=%s
        """
        cursor.execute(sql,(comment_id,))
        comment = cursor.fetchone()

    conn.close()

    return render_template(
        "board/comment_edit.html",
        comment=comment
    )

@board_bp.route("/comment_like/<int:comment_id>")
def comment_like(comment_id):

    if "user_id" not in session:
        return redirect("/login")

    member_id = session["user_id"]

    conn = get_connection()

    with conn.cursor() as cursor:

        # 좋아요 존재 확인
        sql = """
        SELECT id
        FROM comment_likes
        WHERE comment_id=%s
        AND member_id=%s
        """
        cursor.execute(sql,(comment_id,member_id))
        like = cursor.fetchone()

        # 토글 처리
        if like:
            cursor.execute("""
            DELETE FROM comment_likes
            WHERE id=%s
            """,(like["id"],))
        else:
            cursor.execute("""
            INSERT INTO comment_likes
            (comment_id, member_id)
            VALUES (%s,%s)
            """,(comment_id,member_id))

    conn.commit()
    conn.close()

    return redirect(request.referrer)
